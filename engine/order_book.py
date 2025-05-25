from typing import List, Optional

from order import Order


class OrderBook:
    # TODO: docstring

    def __init__(self):
        # TODO: docstring
        self.buy_heap: List[Order] = []
        self.sell_heap: List[Order] = []
        pass

    def add_order(self, order: Order) -> None:
        # TODO: docstring
        pass

    def _add(self, heap: List[Order], order: Order, max_heap: bool) -> None:
        # TODO: docstring
        pass

    def peek_best_buy(self) -> Optional[Order]:
        # TODO: docstring
        pass

    def peek_best_sell(self) -> Optional[Order]:
        # TODO: docstring
        pass

    def pop_best_buy(self) -> Order:
        # TODO: docstring
        pass

    def pop_best_sell(self) -> Order:
        # TODO: docstring
        pass
