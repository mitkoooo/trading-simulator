from datetime import datetime


class Trade:
    """
    A record of an executed match between a buy and a sell order.

    Attributes:
      symbol (str)
      quantity (int)
      price (float)
      timestamp (datetime)
    """

    def __init__(self, symbol: str, quantity: int, price: float):
        """
        Create a Trade. Used by OrderBook.match().

        Example:
            >>> from engine.trade import Trade
            >>> t = Trade("AAPL", 5, 150.0)
            >>> t.symbol
            'AAPL'
        """
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.timestamp = datetime.now()
