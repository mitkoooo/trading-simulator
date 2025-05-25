from datetime import datetime
from typing import Dict, List

from order_book import OrderBook
from stock import Stock
from order import Order
from trade import Trade


class Exchange:
    """A central exchange for matching buy and sell orders and tracking trade history.

    Responsibilities:
      - Maintain order books for each stock symbol.
      - Enqueue orders arriving from traders.
      - Execute price ticks and process order matching.

    Attributes:
        market_data (Dict[str, Stock]): Current market price and history for each symbol.
        order_books (Dict[str, OrderBook]): Order book per symbol for managing open orders.
        current_time (datetime): Timestamp of the last processed tick.

    Example:
        >>> from trader import Trader
        >>> from exchange import Exchange
        >>> from stock import Stock
        >>> market = {"MTKO": Stock("MTKO", 100.0)}
        >>> ex = Exchange(market)
        >>> t = Trader(trader_id=1, starting_cash=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
        >>> ex.add_order(o)
        >>> ex.process_tick()
        >>> trades = ex.match_orders("MTKO")
    """

    def __init__(
        self,
        market_data: Dict[str, Stock],
    ):
        """Initialize the Exchange with market data and prepare order books."""
        self.market_data = market_data
        self.order_books: Dict[str, OrderBook] = {
            symbol: OrderBook() for symbol in market_data.keys()
        }
        self.current_time = datetime.now()

    def add_order(self, order: Order) -> None:
        """Enqueue an Order in its respective order book for later matching.

        Args:
            order (Order): The order to add to the order book.
        """
        self.order_books[order.symbol].add_order(order)

    def process_tick(
        self,
    ) -> None:
        """Advance the exchange clock and update market prices based on stocks."""
        self.current_time = datetime.now()

    def match_orders(self, symbol: str) -> List[Trade]:
        """Match buy and sell orders in the specified symbol's order book.

        Args:
            symbol (str): The stock symbol for which to perform matching.

        Returns:
            List[Trade]: List of executed trades for this symbol.
        """
        pass
