from typing import Dict, List, Literal, Optional

from engine.order_book.order import Order

from .portfolio import Portfolio


class Trader:
    """Represents a market participant with cash balance and equity positions.

    Allows a trader to place buy/sell orders and tracks cash, positions, and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        portfolio (Portfolio): #TODO
        transaction_log (List[Order]): List of previous transactions.

    Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)

    """

    def __init__(
        self,
        trader_id: int,
        starting_balance: float,
    ):
        """Initialize trader with ID and starting cash.

        positions and transaction_log start empty.

        Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)

        """
        self.trader_id = trader_id
        self.portfolio = Portfolio(starting_balance)
        self.transaction_log: List[Order] = []
        self.pending_orders: Dict[str, Order] = {}

    def create_order(
        self, symbol: str, order_type: Literal["buy", "sell"], quantity: int, limit_price: Optional[float] = None
    ) -> Order:
        """Create a new Order for this trader.

        Args:
            symbol (str): Stock ticker, e.g. "AAPL".
            order_type (Literal["buy", "sell"]): "buy" or "sell".
            quantity (int): Shares to trade; must be > 0.
            price (Optional[float]): Limit price, or None for market order.

        Returns:
            Order: the created order instance.

        Note:
            Caller must enqueue the returned Order with Exchange.add_order().

        Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.stock import Stock
        >>> data = {"MTKO": Stock("MTKO", 100.0)}
        >>> exchange = Exchange(market_data=data)
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
        >>> exchange.add_order(o)

        """
        o = Order(
            trader_id=self.trader_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
        )



        return o
