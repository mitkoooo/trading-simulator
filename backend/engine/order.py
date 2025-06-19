from datetime import datetime
from typing import Optional, Literal
import uuid


class Order:
    """A client order to buy or sell shares on the exchange.

    Attributes:
        trader_id (int): ID of the trader submitting the order.
        symbol (str): Stock ticker (e.g. "AAPL").
        order_type (Literal["buy", "sell"]): Direction of the order.
        quantity (int): Number of shares; must be > 0.
        limit_price (Optional[float]): Limit price; None for market orders.
        order_id (Optional[int]): Unique ID, auto-generated if omitted.
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
        order_id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
    ):
        """Initialize a new Order.

        Args:
            trader_id (int): ID of the submitting trader.
            symbol (str): Stock ticker.
            order_type (Literal['buy','sell']): One of 'buy' or 'sell'.
            quantity (int): >0 shares to trade.
            limit_price (Optional[float]): Limit price; None for market orders.
            order_id (Optional[int]): Unique ID, auto-generated if None.
            timestamp (Optional[datetime]): Creation time, auto-set if None.

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
        self.order_type = order_type
        self.quantity = quantity
        self.limit_price = limit_price
        self.order_id = order_id or str(uuid.uuid4())  # or auto-generated
        self.timestamp = timestamp or datetime.now()

        self.sequence: Optional[int] = None  # Serialization number for OrderBook

    def __eq__(self, other: "Order") -> bool:
        """Compare orders by order_id for equality.

        Returns:
        (bool): True if two orders have the same order_id, False otherwise.
        """
        if isinstance(other, Order) == False:
            return False

        return self.order_id == other.order_id

    def __hash__(self):
        return hash(self.order_id)

    def __lt__(self, other: "Order") -> bool:
        """Define ordering for heap operations: price priority then FIFO sequence.

        Args:
            other (Order): Another Order to compare against.

        Returns:
            bool: True if self has higher priority than other (i.e., “comes out first” in a min-heap).

        Raises:
            TypeError: If `other` is not an Order.
            ValueError: If `self.order_type` and `other.order_type` differ.
        """

        if not isinstance(other, Order):
            raise TypeError(f"Cannot compare Order with {type(other).__name__}")

        if self.order_type not in ("buy", "sell") or other.order_type not in (
            "buy",
            "sell",
        ):
            raise ValueError("order_type must be 'buy' or 'sell'")

        if self.order_type != other.order_type:
            raise ValueError(
                f"Cannot compare {self.order_type!r} order with {other.order_type!r} order"
            )

        if self.order_type == "buy":
            # Higher price ⇒ “less” so it pops first in the min-heap
            if self.limit_price != other.limit_price:
                return self.limit_price > other.limit_price

            if self.timestamp != other.timestamp:
                return self.timestamp < other.timestamp

            return self.sequence < other.sequence

        # Lower price ⇒ “less” so it pops first
        if self.limit_price != other.limit_price:
            return self.limit_price < other.limit_price

        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp

        return self.sequence < other.sequence
