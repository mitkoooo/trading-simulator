from .trade import Trade


class Portfolio:
    """
    Tracks a trader's positions and cash balance.

    Responsibilities (to be implemented in Week 2):
      - apply_trade(trade: Trade) → None
      - get_position(symbol: str) → int
    """

    def __init__(self):
        """Initializes a new Portfolio.

        Keeps track of a trader's cash balance and holdings dict.

        Raises:
            NotImplementedError: until matching and portfolio wiring in Week 2.
        """
        raise NotImplementedError("Portfolio.__init__ not yet implemented")

    def apply_trade(self, trade: Trade) -> None:
        """
        Update cash and holdings based on a filled trade.

        Raises:
            NotImplementedError: until matching and portfolio wiring in Week 2.
        """
        raise NotImplementedError("Portfolio.apply_trade not yet implemented")
