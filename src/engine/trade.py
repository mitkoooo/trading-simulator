from datetime import datetime
import uuid

from .order import Order


class Trade:
    """
    A record of an executed match between a buy and a sell order.

    Attributes:
      trade_id (str): Unique trade indentifier.
      buy_order (Order): The buy order involved in the trade.
      sell_order (Order): The sell order involved in the trade.
      symbol (str): Ticker symbol (e.g. "AAPL").
      quantity (int): Actual number of shares traded.
      price (float): Actual execution price.
      timestamp (datetime): Creation time of the trade.
    """

    def __init__(
        self,
        buy_order: Order,
        sell_order: Order,
        symbol: str,
        quantity: int,
        price: float,
        orig_buy_qty: int,
        orig_sell_qty: int,
    ):
        """
        Create a Trade. Used by Exchange.match_orders().

        Args:
          buy_order (Order): The buy order involved in the trade.
          sell_order (Order): The sell order involved in the trade.
          symbol (str): Ticker symbol (e.g. "AAPL").
          quantity (int): Actual number of shares traded.
          price (float): Actual execution price.

        Example:
            >>> from engine.trade import Trade
            >>> from engine.order import Order
            >>> o1 = Order(1, "AAPL", "buy", 4, 42)
            >>> o2 = Order(2, "AAPL", "sell", 4, 42)
            >>> t = Trade(o1, o2, "AAPL", 4, 42, 4, 42)
            >>> t.symbol
            'AAPL'
        """
        self.trade_id = str(uuid.uuid4())  # Generate new unique identifier
        self.buy_order = buy_order
        self.sell_order = sell_order
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.timestamp = datetime.now()
        self.orig_buy_qty = orig_buy_qty
        self.orig_sell_qty = orig_sell_qty
