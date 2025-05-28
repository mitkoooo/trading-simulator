from typing import List, Callable, Optional
import logging
from cli.commands import do_next, do_place_order, do_match, do_status, log_quit


class CLI:
    def __init__(
        self,
        exchange,
        trader,
        logger: logging.Logger,
    ):
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
