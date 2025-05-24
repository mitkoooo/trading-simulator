from datetime import datetime
from typing import Dict, List

from order_book import OrderBook
from stock import Stock
from order import Order
from trade import Trade


class Exchange:
    # TODO: docstring

    def __init__(
        self,
        order_books: Dict[str, OrderBook],
        market_data: Dict[str, Stock],
        current_time: datetime,
    ):
        # TODO: docstring
        pass

    def add_order(self, order: Order) -> None:
        # TODO: docstring
        pass

    def process_tick(
        self,
    ) -> None:
        # TODO: docstring
        pass

    def match_orders(self, symbol: str) -> List[Trade]:
        # TODO: docstring
        pass
