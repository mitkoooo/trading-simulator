from typing import List, Callable, Optional
import logging
from cli.commands import do_next, do_place_order, do_match, do_status, log_quit
from engine.exchange import Exchange
from engine.trader import Trader


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
        >>> trader = Trader(trader_id=1, cash_balance=100000)
        >>> logger = setup_logger()
        >>> cli = CLI(exchange, trader, logger)
        >>> list(cli.commands)
        ['next', 'buy', 'sell', 'match', 'status']
    """

    def __init__(
        self,
        exchange,
        trader,
        logger: logging.Logger,
    ):
        """
        Initialize the CLI with its core dependencies and command map.

        Args:
            exchange (Exchange): the market exchange instance for price and order operations.
            trader (Trader): the trader instance representing the user.
            logger (logging.Logger): logger used to record command execution.

        Examples:
        >>> from logging_config import setup_logger
        >>> exchange = Exchange(market_data={})
        >>> trader = Trader(trader_id=1, cash_balance=100000)
        >>> logger = setup_logger()
        >>> cli = CLI(exchange, trader, logger)
        >>> isinstance(cli, CLI)
        True
        """
        self.exchange = exchange
        self.trader = trader
        self.logger = logger

        # map command strings to handler callables
        self.commands: dict[str, Callable[[Optional[List[str]]], None]] = {
            "next": lambda args=None: do_next(self.exchange, self.trader),
            "buy": lambda args=[]: do_place_order(
                self.exchange, self.trader, "buy", args
            ),
            "sell": lambda args=[]: do_place_order(
                self.exchange, self.trader, "sell", args
            ),
            "match": lambda args=[]: do_match(self.exchange, args),
            "status": lambda args=None: do_status(self.exchange, self.trader),
        }

    def run(self):
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
        >>> trader = Trader(trader_id=1, cash_balance=1000)
        >>> cli = CLI(exchange, trader, logger)
        >>> # This would start an interactive loop
        >>> cli.run()  # doctest: +SKIP
        """
        while True:
            try:
                raw = input(">>> ")
            except EOFError:
                log_quit()
                break

            if not raw.strip():
                print()  # blank line on empty enter
                continue

            cmd, *args = raw.split()
            if cmd == "quit":
                log_quit()
                break

            handler = self.commands.get(cmd)
            if handler:
                # for buy/sell/match, args is non-empty list; for next/status, it’s None
                handler(args if args else None)
            else:
                print("Unknown command. Please try again.")
