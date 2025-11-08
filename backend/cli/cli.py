import asyncio
import functools
import inspect
from collections.abc import Callable
from logging import Logger
from typing import Literal

from app.context import AppContext
from cli.render import display_welcome

from .commands import (
    do_cancel_order,
    do_help,
    do_login,
    do_logout,
    do_next,
    do_place_order,
    do_portfolio,
    do_status,
    log_quit,
)


def log_command_factory(logger: Logger) -> Callable:
    """Retturn a decorator that will log using the supplied `logger`.
    
    Args:
        logger (Logger):
            Logger to use for CLI commands.

    """

    def _decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def _wrapper(*args: list[str], **kwargs: list[str]) -> Callable:
            cmd = fn.__name__.replace("do_", "").upper()
            logger.info(
                "%s command received: args=%r, kwargs=%r", cmd, args, kwargs
            )
            result = fn(*args, **kwargs)
            logger.info("%s command processed", cmd)
            return result

        return _wrapper

    return _decorator


class CLI:
    """Read-Eval-Print Loop for the Stock Exchange CLI.

    Manages user input and dispatches commands to the appropriate handlers.

    Attributes:
        exchange (Exchange):
            The market exchange instance.

        trader (Trader):
            The trader instance.

        logger (logging.Logger):
            Logger for audit logs.

        commands (dict[str, Callable[[Optional[List[str]]], None]]):
            Mapping of command names to handler callables.

    Examples:
        >>> from logging_config import setup_logger
        >>> exchange = Exchange(market_data={})
        >>> trader = Trader(trader_id=1, starting_balance=100000)
        >>> logger = setup_logger()
        >>> cli = CLI(exchange, trader, logger)
        >>> list(cli.commands)
        ['next', 'buy', 'sell', 'match', 'status']

    """

    def __init__(self, context: AppContext) -> None:
        """Initialize the CLI with its core dependencies and command map.

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
        assert self.context.logger

        wrap = log_command_factory(self.context.logger)

        # --- helper factories ---
        def _no_args(fn: Callable) -> Callable:
            """Wrap a command fn(ctx) → None."""

            @functools.wraps(fn)
            def _handler(_: list[str] | None) -> Callable:
                return fn(self.context)

            return wrap(_handler)

        def _with_args(fn: Callable) -> Callable:
            """Wrap a command fn(ctx, args) → None.

            Args:
                fn (Callable):
                    Function to wrap with AppContext and args.

            """

            @functools.wraps(fn)
            def _handler(args: list[str] | None = None) -> Callable:
                return fn(self.context, args or [])

            return wrap(_handler)

        def _with_side(side: Literal["buy", "sell"]) -> Callable:
            """Add special factory for buy/sell commands.
            
            Args:
                side (Literal["buy", "sell"]):
                    Buy or sell an order.

            """

            @functools.wraps(do_place_order)
            async def handler(args: list[str] | None = None) -> None:
                await do_place_order(self.context, side, args or [])

            return wrap(handler)

        # map command strings to handler callables
        # --- build the dispatch table ---
        self.commands = {
            "login": _with_args(do_login),
            "logout": _no_args(do_logout),
            "next": _no_args(do_next),
            "buy": _with_side("buy"),
            "sell": _with_side("sell"),
            "cancel": _no_args(do_cancel_order),
            "status": _no_args(do_status),
            "portfolio": _no_args(do_portfolio),
            "help": _no_args(do_help),
        }

    async def run(self) -> None:
        """Start the interactive loop, reading input and dispatching commands.

        Continuously prompts with '>>> '.
        Handles empty input by printing a blank line,
        EOF by exiting gracefully,
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
                log_quit(self.context)
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
