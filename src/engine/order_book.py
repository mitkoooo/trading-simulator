from typing import List, Optional
import heapq


from .order import Order


class OrderBook:
    """Maintain separate buy and sell priority queues of orders.

    The book ensures that matching always pulls the highest bid and lowest ask first.

    Attributes:
        buy_heap (List[Order]): A min-heap that prioritizes pending buy orders.
        sell_heap (List[Order]): A max-heap that prioritizes pending sell orders.
        global_seq (int): OrderBook-wide counter of the next order sequence.

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
        self._buy_heap: List[Order] = []
        self._sell_heap: List[Order] = []
        self._heap_map = {"buy": self._buy_heap, "sell": self._sell_heap}
        self._global_seq = 0

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

        self.serialize(order)

        heap = self._heap_map[order.order_type]

        heapq.heappush(heap, order)

    def peek_best_buy(self) -> Optional[Order]:
        """
        Return the highest-price sell order without removing it.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.
        """
        if not self._buy_heap:
            return None
        return self._buy_heap[0]

    def peek_best_sell(self) -> Optional[Order]:
        """
        Return the lowest-price sell order without removing it.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.
        """
        if not self._sell_heap:
            return None
        return self._sell_heap[0]

    def pop_best_buy(self) -> Optional[Order]:
        """
        Remove and return the highest-price buy order.

        Returns:
            The Order with the highest limit_price.
        """
        if not self._buy_heap:
            return None
        return heapq.heappop(self._buy_heap)

    def pop_best_sell(self) -> Order:
        """
        Remove and return the lowest-price sell order.

        Returns:
            The Order with the lowest limit_price.

        Raises:
            IndexError: if there are no sell orders.
        """
        if not self._sell_heap:
            return None
        return heapq.heappop(self._sell_heap)

    def serialize(self, order: Order) -> None:
        """Adds a sequence number to Order object

        Args:
            order (Order): Order to be serialized
        """
        if order.sequence != None:
            return

        order.sequence = self._global_seq

        self._global_seq += 1

    def buy_size(self) -> int:
        """Return the number of buy orders currently in the book."""
        return len(self._buy_heap)

    def sell_size(self) -> int:
        """Return the number of sell orders currently in the book."""
        return len(self._sell_heap)

    @property
    def total_size(self) -> int:
        """Return the total number of orders (buy + sell)."""
        return len(self._buy_heap) + len(self._sell_heap)

    def get_buy_orders(self) -> List[Order]:
        """
        Return a list of all buy Orders currently in the book (unsorted).
        """
        return [order for order in self._buy_heap]

    def get_sell_orders(self) -> List[Order]:
        """
        Return a list of all sell Orders currently in the book (unsorted).
        """
        return [order for order in self._sell_heap]
