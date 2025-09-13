from uuid import uuid4

from engine.order_book.order import Order
from engine.order_info import OrderInfo

from .portfolio import Portfolio


class Trader:
    """Represents a market participant with cash balance and equity positions.

    Allows a trader to place buy/sell orders and tracks cash, positions,
    and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        portfolio (Portfolio): #TODO
        transaction_log (dict[str, Order]): List of previous transactions.

    Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)

    """

    def __init__(
        self,
        trader_id: str | None,
        starting_balance: float,
    ) -> None:
        """Initialize trader with ID and starting cash.

        positions and transaction_log start empty.

        Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)

        """
        self.trader_id = trader_id or str(uuid4())
        self.portfolio = Portfolio(starting_balance)
        self.transaction_log: dict[str, OrderInfo] = {}
        self.pending_orders: dict[str, Order] = {}

    def update_order_avg_fill_price(self, order_id: str, trade_price: float,
                                    quantity: int) -> None:
        order_info = self.transaction_log[order_id]

        avg_fill_price = (order_info.avg_fill_price if
                            order_info.avg_fill_price else 0)

        filled_qty = order_info.fill_qty - order_info.remaining_qty
        net = avg_fill_price * filled_qty + trade_price * quantity

        filled_qty += quantity
        order_info.remaining_qty -= quantity

        order_info.avg_fill_price = net / filled_qty
