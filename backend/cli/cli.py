import inspect
import asyncio

from .commands import (
    do_next,
    do_place_order,
    do_cancel_order,
    do_match,
    do_status,
    log_quit,
    do_portfolio,
    do_login,
    do_logout,
    do_help,
)

from app.context import AppContext

from cli.render import display_welcome

import functools


def log_command_factory(logger):
    """
    Returns a decorator that will log using the supplied `logger`.
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            cmd = fn.__name__.replace("do_", "").upper()
            logger.info("%s command received: args=%r, kwargs=%r", cmd, args, kwargs)
            result = fn(*args, **kwargs)
            logger.info("%s command processed", cmd)
            return result

        return wrapper

    return decorator


class CLI:
    """
    Read-Eval-Print Loop for the York Stock Exchange CLI.

    Manages user input and dispatches commands (next, buy, sell, match, status) to the appropriate handlers.

    Attributes:
        exchange (Exchange): the market exchange instance.
        trader (Trader): the trader instance.
        logger (logging.Logger): logger for audit logs.
        commands (dict[str, Callable[[Optional[List[str]]], None]]): mapping of command names to handler callables.

    Examples:
        >>> from logging_config import setup_logger
        >>> exchange = Exchange(market_data={})
        >>> trader = Trader(trader_id=1, starting_balance=100000)
        >>> logger = setup_logger()
        >>> cli = CLI(exchange, trader, logger)
        >>> list(cli.commands)
        ['next', 'buy', 'sell', 'match', 'status']
    """

    def __init__(self, context: AppContext):
        """
        Initialize the CLI with its core dependencies and command map.

        Args:
            context (AppContext): Current application context.

        Examples:
        >>> from logging_config import setup_logger
        >>> exchange = Exchange(market_data={})
        >>> trader = Trader(trader_id=1, starting_balance=100000)
        >>> logger = setup_logger()
        >>> cli = CLI(exchange, trader, logger)
        >>> isinstance(cli, CLI)
        True
        """
        self.context = context

        wrap = log_command_factory(self.context.logger)

        # --- helper factories ---
        def _no_args(fn):
            """Wrap a command fn(ctx) → None"""

            @functools.wraps(fn)
            def handler(_args=None):
                return fn(self.context)

            return wrap(handler)

        def _with_args(fn):
            """Wrap a command fn(ctx, args) → None"""

            @functools.wraps(fn)
            def handler(args=None):
                return fn(self.context, args or [])

            return wrap(handler)

        def _with_side(side):
            """Special factory for buy/sell which need (ctx, side, args)"""

            @functools.wraps(do_place_order)
            def handler(args=None):
                return do_place_order(self.context, side, args or [])

            return wrap(handler)

        # map command strings to handler callables
        # --- build the dispatch table ---
        self.commands = {
            "login": _with_args(do_login),
            "logout": _no_args(do_logout),
            "next": _no_args(do_next),
            "buy":  _with_side("buy"),
            "sell": _with_side("sell"),
            "cancel": _no_args(do_cancel_order),
            "match": _with_args(do_match),
            "status": _no_args(do_status),
            "portfolio": _no_args(do_portfolio),
            "help": _no_args(do_help),
        }

    async def run(self):
        """
        Start the interactive loop, reading user input and dispatching commands.

        Continuously prompts with '>>> '.
        Handles empty input by printing a blank line, EOF by exiting gracefully,
        and 'quit' to terminate.

        Examples:
        >>> from cli.cli import CLI
        >>> from engine.exchange import Exchange
        >>> from engine.trader import Trader
        >>> from logging_config import setup_logger
        >>> logger = setup_logger()
        >>> exchange = Exchange(market_data={})
        >>> trader = Trader(trader_id=1, starting_balance=1000)
        >>> cli = CLI(exchange, trader, logger)
        >>> # This would start an interactive loop
        >>> cli.run()  # doctest: +SKIP
        """

        display_welcome()
        while True:
            try:
                loop = asyncio.get_event_loop()
                raw = await loop.run_in_executor(None, input, ">>> ")
            except EOFError:
                log_quit()
                break

            if not raw.strip():
                print()  # blank line on empty enter
                continue

            cmd, *args = raw.split()
            if cmd in ["quit", "exit"]:
                log_quit(self.context)
                break


            handler = self.commands.get(cmd)
            if not handler:
                print("Unknown command. Please try again.")
                continue

            result = handler(args if args else None)
            if inspect.iscoroutine(result):
                await result

                
