from typing import Dict, List, Optional
from order import Order


class Trader:
    # TODO: docstring

    def __init__(
        self,
        trader_id: int,
        cash_balance: float,
    ):
        # TODO: docstring
        self.trader_id = trader_id
        self.cash_balance = cash_balance
        self.holdings: Dict[str, int] = {}
        self.transaction_log: List[Order] = []

    def place_order(
        self, symbol: str, order_type: str, qty: int, price: Optional[float]
    ) -> Order:
        # TODO: docstring
        pass

    def update_portfolio(
        self, order: Order, executed_qty: int, execution_price: float
    ) -> None:
        # TODO: docstring
        pass
