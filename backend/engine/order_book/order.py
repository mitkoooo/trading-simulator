import uuid
from datetime import datetime
from typing import Literal, Optional


class Order:
    """A client order to buy or sell shares on the exchange.

    Attributes:
        trader_id (int): ID of the trader submitting the order.
        symbol (str): Stock ticker (e.g. "AAPL").
        order_type (Literal["buy", "sell"]): Direction of the order.
        status (Literal["pending", "partially_filled", "filled", "cancelled"]
        quantity (int): Number of shares; must be > 0.
        limit_price (float or None): Limit price; None for market orders.
        order_id (str): Unique ID, auto-generated if omitted in the initializer.
        timestamp (datetime): Creation time of the order.

    Examples:
        >>> o = Order(
        ...     trader_id=1,
        ...     symbol="MTKO",
        ...     order_type="buy",
        ...     quantity=2,
        ...     limit_price=999.0
        ... )

    """

    def __init__(
        self,
        trader_id: int,
        symbol: str,
        order_type: Literal["buy", "sell"],
        quantity: int,
        limit_price: Optional[float] = None,
        *,
        order_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        """Initialize a new Order.

        Args:
            trader_id (int): ID of the submitting trader.
            symbol (str): Stock ticker.
            order_type (Literal['buy','sell']): One of 'buy' or 'sell'.
            quantity (int): >0 shares to trade.
            limit_price (float or None): Limit price; None for market orders.
            order_id (str or None): Unique ID, auto-generated if None.
            timestamp (datetime or None): Creation time, auto-set if None.

        Raises:
            ValueError: If quantity <= 0 or order_type invalid.

        Examples:
        >>> o = Order(
        ...     trader_id=1,
        ...     symbol="MTKO",
        ...     order_type="buy",
        ...     quantity=2,
        ...     limit_price=999.0
        ... )

        """
        if quantity <= 0:
            raise ValueError(
                f"Order must have quantity > 0. Current order quantity: {quantity}."
            )

        if limit_price and limit_price <= 0:
            raise ValueError(
                f"Order must have limit_price > 0. Current limit price: {limit_price}"
            )

        if order_type not in ["buy", "sell"]:
            raise ValueError("Invalid order type. Must be of type: 'buy' or 'sell'.")

        self.trader_id = trader_id
        self.symbol = symbol
        self.order_type: Literal["buy", "sell"] = order_type
        self.status = "pending"                         # All orders at first are initialized as pending
        self.quantity = quantity
        self.limit_price = limit_price
        self.order_id = order_id or str(uuid.uuid4())   # or auto-generated
        self.timestamp = timestamp or datetime.now()

        self.sequence: Optional[int] = None  # Serialization number for OrderBook

    def __eq__(self, other: object) -> bool:
        """Orders compare equal if they share the same order_id."""
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        """Hash based solely on order_id, to match __eq__ semantics."""
        return hash(self.order_id)

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        lp = self.limit_price if self.limit_price is not None else "MARKET"
        return (
            f"{cls}("
            f"id={self.order_id!r}, "
            f"{self.order_type}@{self.symbol!r}, "
            f"qty={self.quantity!r}, "
            f"price={lp!r}, "
            f"status={self.status!r}, "
            f"time={self.timestamp.isoformat()!r}"
            f")"
        )
