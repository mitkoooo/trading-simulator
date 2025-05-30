from typing import List, Optional

from .order import Order


class OrderBook:
    """Maintain separate buy and sell priority queues of orders.

    The book ensures that matching always pulls the highest bid and lowest ask first.

    Attributes:
        buy_heap (List[Order]): A min-heap that prioritizes pending buy orders.
        sell_heap (List[Order]): A max-heap that prioritizes pending sell orders.

    Examples:
    >>> from engine.order_book import OrderBook
    >>> from engine.order      import Order
    >>> order_book = OrderBook()
    >>> o = Order(
    ...     trader_id=1,
    ...     symbol="MTKO",
    ...     order_type="buy",
    ...     quantity=2,
    ...     limit_price=999.0
    ... )
    >>> order_book.add_order(o)
    >>> len(order_book.buy_heap)
    1
    """

    def __init__(self):
        self.buy_heap: List[Order] = []
        self.sell_heap: List[Order] = []
        self._heap_map = {"buy": self.buy_heap, "sell": self.sell_heap}

    def add_order(self, order: Order) -> None:
        """
        Enqueue an Order into the appropriate heap.

        Args:
            order (Order): The order to add.

        Raises:
            ValueError: if order.order_type is not 'buy' or 'sell'.
        """

        if order.order_type not in self._heap_map:
            raise ValueError(f"Unknown order type: {order.order_type}")

        heap = self._heap_map[order.order_type]

        heap.append(order)

    def peek_best_buy(self) -> Optional[Order]:
        """
        Return the highest-price sell order without removing it.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.

        Raises:
            NotImplementedError: until heap logic is implemented.
        """
        raise NotImplementedError("peek_best_sell not yet implemented")

    def peek_best_sell(self) -> Optional[Order]:
        """
        Return the lowest-price sell order without removing it.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.

        Raises:
            NotImplementedError: until heap logic is implemented.
        """
        raise NotImplementedError("peek_best_sell not yet implemented")

    def pop_best_buy(self) -> Order:
        """
        Remove and return the highest-price buy order.

        Returns:
            The Order with the highest limit_price.

        Raises:
            IndexError: if there are no buy orders.
            NotImplementedError: until heap logic is implemented.
        """
        raise NotImplementedError("OrderBook.pop_best_buy not yet implemented")

    def pop_best_sell(self) -> Order:
        """
        Remove and return the lowest-price sell order.

        Returns:
            The Order with the lowest limit_price.

        Raises:
            IndexError: if there are no sell orders.
            NotImplementedError: until heap logic is implemented.
        """
        raise NotImplementedError("OrderBook.pop_best_sell not yet implemented")
