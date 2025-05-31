from datetime import datetime
from typing import Dict, List

from .order_book import OrderBook
from .stock import Stock
from .order import Order
from .trade import Trade


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

    Examples:
        >>> from engine.trader import Trader
        >>> data = {"MTKO": Stock("MTKO", 100.0)}
        >>> exchange = Exchange(market_data=data)
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
        >>> exchange.add_order(o)
        >>> exchange.process_tick()
        >>> trades = exchange.match_orders("MTKO")
    """

    def __init__(
        self,
        market_data: Dict[str, Stock],
    ):
        """Initialize the Exchange with market data and prepare order books.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
        """
        self.market_data = market_data
        self.order_books: Dict[str, OrderBook] = {
            symbol: OrderBook() for symbol in market_data.keys()
        }
        self.current_time = datetime.now()

    def add_order(self, order: Order) -> None:
        """Enqueue an Order in its respective order book for later matching.

        Args:
            order (Order): The order to add to the order book.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy", quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> len(exchange.order_books["AAPL"].buy_heap)
            1
        """
        self.order_books[order.symbol].add_order(order)

    def process_tick(
        self,
    ) -> None:
        """Advance the exchange clock and update market prices based on stocks.

        Examples:
        >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
        >>> exchange = Exchange(market_data=data)
        >>> before = [s.price for s in exchange.market_data.values()]
        >>> exchange.process_tick()
        >>> after = [s.price for s in exchange.market_data.values()]
        >>> any(b != a for b, a in zip(before, after))
        True
        """
        self.current_time = datetime.now()

        for stock in self.market_data.values():
            nxt = stock.simulate_price_tick()
            stock.update_price(nxt)

    def match_orders(self, symbol: str) -> List[Trade]:
        """Match buy and sell orders in the specified symbol's order book.

        Args:
            symbol (str): The stock symbol for which to perform matching.

        Returns:
            List[Trade]: Empty list but later in the project list of executed trades for this symbol.

        Examples:
            >>> data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
            >>> exchange = Exchange(market_data=data)
            >>> o = Order(trader_id=1,symbol="AAPL",order_type="buy", quantity=42, limit_price=100.0)
            >>> exchange.add_order(o)
            >>> exchange.match_orders("AAPL")
            []
        """
        return []
