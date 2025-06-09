from typing import Callable, Optional
from datetime import timedelta

from .exchange import Exchange
from .trade import Trade


class MarketSimulator:
    """
    Drives price ticks and matching in one place.

    Responsibilities:
      - step(): advance one tick + match all symbols
      - (Future) start/end real-time streams
      - (Future) replay historical CSV feeds
      - (Future) register_listener(callback)
    """

    def __init__(self, exchange: Exchange, tick_interval: timedelta):
        """
        Args:
            exchange: the Exchange instance to drive
            tick_interval: how much “time” passes per step()
        """
        self.exchange = exchange
        self.tick_interval = tick_interval
        self._running = False

    def step(self) -> list[Trade]:
        """
        Advance prices by one tick, then match all symbols.
        Returns the list of Trades executed this step.
        """
        # 1) advance every stock by one tick
        self.exchange.process_tick()
        # 2) match on every book, collect trades
        symbols = self.exchange.order_books.keys()

        for symbol in symbols:
            self.exchange.match_orders(symbol)
        return

    def run(self, steps: Optional[int] = None) -> None:
        """
        Auto-run for `steps` iterations (or endlessly if None).
        """
        self._running = True
        count = 0

        while self._running and (steps is None or count < steps):
            trades = self.step()

            if not trades:
                continue

            for t in trades:
                print(f"\nTRADE: {t.quantity}x{t.symbol} @ ${t.price:.2f}")
            print()
            count += 1

    def stop(self):
        """Stop an ongoing run()."""
        self._running = False

    def start_stream(self) -> None:
        """Begin feeding ticks into Exchange

        Raises:
            NotImplementedError: until Week 3 real-time integration.
        """
        raise NotImplementedError("MarketSimulator.start_stream not yet implemented")

    def end_stream(self) -> None:
        """Stop feeding ticks (pause) into the Exchange

        Raises:
            NotImplementedError: until Week 3 real-time integration
        """
        raise NotImplementedError("MarketSimulator.end_stream not yet implemented")

    def register_listener(self, callback: Callable[[str, float], None]) -> None:
        """
        Register a function to be called on each new price tick.

        Args:
            callback (Callable[[str, float], None]):
                Receives (symbol, new_price) on each tick.

        Raises:
            NotImplementedError: until real-time integration in Week 3.
        """
        raise NotImplementedError(
            "MarketSimulator.register_listener not yet implemented"
        )
