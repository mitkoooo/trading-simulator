from typing import Callable, Optional
from datetime import timedelta

from .exchange import Exchange
from .trade import Trade


class MarketSimulator:
    """Drives price ticks and matches them automatically based on historical/live data.

    Examples:
    >>> from engine.exchange import Exchange
    >>> from engine.order import Order
    >>> from datetime import timedelta
    >>> MARKET_DATA = {"AAPL": 150.00}
    >>> TICK_INTERVAL = timedelta(seconds=1)
    >>> ex = Exchange(MARKET_DATA)
    >>> o = Order(
        ...     trader_id=1,
        ...     symbol="AAPL",
        ...     order_type="buy",
        ...     quantity=2,
        ...     limit_price=150.0)
    >>> exchange.add_order(o)
    >>> ms = MarketSimulator(ex, TICK_INTERVAL)
    >>> ms.run()


    """

    def __init__(self, exchange: Exchange, tick_interval: timedelta):
        """
        Args:
            exchange (Exchange): the Exchange instance to drive
            tick_interval (timedelta): how much “time” passes per step()
        """
        self._exchange = exchange
        self._tick_interval = tick_interval
        self._running = False

    def step(self) -> list[Trade]:
        """
        Advance prices by one tick, then match all symbols.
        Returns the list of Trades executed this step.
        """
        # 1) advance every stock by one tick
        self._exchange.process_tick()
        # 2) match on every book, collect trades
        symbols = self._exchange.order_books.keys()

        for symbol in symbols:
            self._exchange.match_orders(symbol)
        return

    def run(self, steps: Optional[int] = None) -> None:
        """Execute preplaced orders or orders based on historical data.

        Attributes:
            steps (Optional[int]): Auto run for `steps` iterations (endlessly if None).
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
