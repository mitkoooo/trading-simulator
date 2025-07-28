from typing import List, Dict
from uuid import uuid4
from engine.order_book.order import Order
from .portfolio import Portfolio


class Trader:
    """Represents a market participant with cash balance and equity positions.

    Allows a trader to place buy/sell orders and tracks cash, positions,
    and transaction history.

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
        trader_id: str | None,
        starting_balance: float,
    ):
        """Initialize trader with ID and starting cash.

        positions and transaction_log start empty.

        Examples:
        >>> t = Trader(trader_id=1, starting_balance=10000.0)
        >>> o = t.place_order("MTKO", "buy", 42, 10.0)
        """
        self.trader_id = trader_id or str(uuid4())
        self.portfolio = Portfolio(starting_balance)
        self.transaction_log: List[Order] = []
        self.pending_orders: Dict[str, Order] = {}
