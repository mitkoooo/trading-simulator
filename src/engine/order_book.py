from typing import List, Optional

from .order import Order


class OrderBook:
    # TODO: docstring

    def __init__(self):
        # TODO: docstring
        self.buy_heap: List[Order] = []
        self.sell_heap: List[Order] = []
        self._heap_map = {"buy": self.buy_heap, "sell": self.sell_heap}

    def add_order(self, order: Order) -> None:
        if order.order_type not in self._heap_map:
            raise ValueError(f"Unknown order type: {order.order_type}")

        (self._heap_map[order.order_type]).append(order)

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
