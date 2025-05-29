from typing import Dict, List, Optional
from .order import Order


class Trader:
    """Represents a market participant with cash balance and equity holdings.

    Allows a trader to place buy/sell orders and tracks cash, holdings, and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        cash_balance (float): Available cash balance.
        holdings (Dict[str, int]): A map of the trader's stock holdings.
        transaction_log (List[Order]): List of previous transactions.

    Example:
        >>> t = Trader(trader_id=1, cash_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 999.0)
    """

    def __init__(
        self,
        trader_id: int,
        cash_balance: float,
    ):
        """Initialize trader with ID and starting cash.

        Holdings and transaction_log start empty.
        """
        self.trader_id = trader_id
        self.cash_balance = cash_balance
        self.holdings: Dict[str, int] = {}
        self.transaction_log: List[Order] = []

    def place_order(
        self, symbol: str, order_type: str, quantity: int, price: Optional[float]
    ) -> Order:
        """Create a new Order for this trader.

        Args:
            symbol (str): Stock ticker, e.g. "AAPL".
            order_type (str): "buy" or "sell".
            quantity (int): Shares to trade; must be > 0.
            price (Optional[float]): Limit price, or None for market order.

        Returns:
            Order: the created order instance.

        Raises:
            ValueError: If quantity <= 0 or order_type is invalid.

        Note:
            Caller must enqueue the returned Order with Exchange.add_order().
        """

        if quantity <= 0:
            raise ValueError(f"quantity must be > 0 (got {quantity})")

        if order_type not in ("buy", "sell"):
            raise ValueError(f"order_type must be 'buy' or 'sell' (got {order_type!r})")

        return Order(
            trader_id=self.trader_id,
            symbol=symbol,
            order_type=order_type,
            quantity=quantity,
            limit_price=price,
        )

    def update_portfolio(
        self, order: Order, executed_qty: int, execution_price: float
    ) -> None:
        # TODO: docstring
        pass
