from typing import Callable


class MarketSimulator:
    """Orchestrates live or historical tick feeds into Exchange

    Responsibilities (planned for Week 3):
        - start_stream() -> None
        - stop_stream() -> None
        - register_listener(callback) -> None
    """

    def __init__(self):
        """Initialize the MarketSimulator.

        This stub will later connect to a live market-data websocket or
        replay ticks from a CSV file in Week 3's real-time integration.

        Raises:
            NotImplementedError: until real-time feed support is implemented.
        """
        # hook up websocket or CSV playback
        raise NotImplementedError("MarketSimulator.__init__ not yet implemented")

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
