import uuid
from datetime import datetime
from typing import Literal


class Order:
    """A client order to buy or sell shares on the exchange.

    Attributes:
        mpid (str): ID of market participant owning `Order`.
        symbol (str): Stock ticker (e.g. "AAPL").
        order_type (Literal["buy", "sell"]): Direction of the order.
        status (Literal["pending", "partially_filled", "filled", "cancelled"]
        quantity (int): Number of shares; must be > 0.
        limit_price (float or None): Limit price; None for market orders.
        order_id (str): Unique ID, auto-generated if omitted.
        timestamp (datetime): Creation time of the order.

    Examples:
        >>> o = Order(
        ...     mpid=1,
        ...     symbol="MTKO",
        ...     order_type="buy",
        ...     quantity=2,
        ...     limit_price=999.0
        ... )

    """

    def __init__(
        self,
        mpid: str,
        symbol: str,
        order_type: Literal["buy", "sell"],
        quantity: int,
        limit_price: float | None = None,
    ) -> None:
        """Initialize a new Order.

        Args:
            mpid (int): ID of the submitting market participant.
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
            msg = f"Order must have quantity > 0. (got {quantity})"
            raise ValueError(msg)

        if limit_price and limit_price <= 0:
            msg = f"Order must have limit_price > 0. (got {limit_price})"
            raise ValueError(msg)

        if order_type not in ["buy", "sell"]:
            msg = "Invalid order type. Must be of type: 'buy' or 'sell'"
            raise ValueError(msg)

        self.mpid = mpid
        self.symbol = symbol
        self.order_type: Literal["buy", "sell"] = order_type
        self.status = "pending"
        self.quantity = quantity
        self.limit_price = limit_price
        self.order_id = str(uuid.uuid4())
        self.timestamp = datetime.now()
        self.sequence: int | None = None

    def __eq__(self, other: object) -> bool:
        """Orders compare equal if they share the same order_id."""
        if not isinstance(other, Order):
            return NotImplemented
        return self.order_id == other.order_id

    def __hash__(self) -> int:
        """Hash based solely on order_id, to match __eq__ semantics."""
        return hash(self.order_id)

    def __repr__(self) -> str:
        """Display representation string of `Order`."""
        cls = self.__class__.__name__
        lp = self.limit_price if self.limit_price is not None else "NONE"
        return (
            f"{cls}("
            f"mpid={self.mpid},"
            f"id={self.order_id!r}, "
            f"{self.order_type}@{self.symbol!r}, "
            f"qty={self.quantity!r}, "
            f"price={lp!r}, "
            f"status={self.status!r}, "
            f"time={self.timestamp.isoformat()!r}"
            f")"
        )
