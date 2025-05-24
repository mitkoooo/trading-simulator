from datetime import datetime
from typing import Optional, Literal


class Order:
    # TODO: docstring

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
        # TODO: docstring

        # system‐generated if not provided:
        self.order_id = order_id  # TODO: add ID generator
        self.timestamp = timestamp or datetime.now()

        self.order_id = order_id
        self.trader_id = trader_id
        self.symbol = symbol
        self.order_type = order_type  # 'buy' or 'sell'
        self.quantity = quantity
        self.limit_price = limit_price
        self.timestamp = timestamp

    def __eq__(self, other: "Order") -> bool:
        # TODO: docstring
        pass

    def __lt__(self, other: "Order") -> bool:
        # TODO: docstring
        pass
