from typing import Dict, List, Optional
from order import Order


class Trader:
    """Represents a market participant with cash balance and equity holdings.

    Allows a trader to place buy/sell orders and tracks cash, holdings, and transaction history.

    Attributes:
        trader_id (int): A unique trader identifier.
        cash_balance (float): Available cash balance.
        holdings (Dict[str, int]): A map of the trader's stock holdings.
        transaction_log (List[Order]): List of previous transactions.

    Example:
        >>> t = Trader(trader_id=1, starting_cash=10000.0)
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
        self, symbol: str, order_type: str, qty: int, price: Optional[float]
    ) -> Order:
        """Construct and enqueue an Order for matching.

        Args:
            symbol (str): Ticker symbol, e.g. "AAPL".
            order_type (str): A literal of either "buy" or "sell".
            qty (int): Number of shares; must be > 0.
            price (Optional[float]): Limit price for limit orders;
                None indicates a market order.

        Returns:
            Order: The newly created Order object.

        Side-Effects:
            - Adds the Order to the Exchange's order queue.

        Raises:
            ValueError: If qty <= 0 or order_type not in {"buy", "sell"}.
        """
        pass

    def update_portfolio(
        self, order: Order, executed_qty: int, execution_price: float
    ) -> None:
        # TODO: docstring
        pass
