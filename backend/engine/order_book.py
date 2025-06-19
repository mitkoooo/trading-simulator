from typing import List, Optional
import heapq


from .order import Order


class OrderBook:
    """Maintain separate buy and sell priority queues of orders.

    The book ensures that matching always pulls the highest bid and lowest ask first.

    Attributes:
        buy_heap (List[Order]): A max-heap that prioritizes pending buy orders.
        sell_heap (List[Order]): A min-heap that prioritizes pending sell orders.
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
    >>> order_book.buy_size()
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

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.peek_best_buy() == o
        True
        """

        if order.order_type not in self._heap_map:
            raise ValueError(f"Unknown order type: {order.order_type}")

        self._serialize(order)

        heap = self._heap_map[order.order_type]

        heapq.heappush(heap, order)

    def peek_best_buy(self) -> Optional[Order]:
        """Return the highest-price sell order without removing it.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.peek_best_buy() == o
        True
        """
        if not self._buy_heap:
            return None
        return self._buy_heap[0]

    def peek_best_sell(self) -> Optional[Order]:
        """Return the lowest-price sell order without removing it.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="sell", quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.peek_best_sell() == o
        True
        """
        if not self._sell_heap:
            return None
        return self._sell_heap[0]

    def pop_best_buy(self) -> Optional[Order]:
        """
        Remove and return the highest-price buy order.

        Returns:
            The Order with the highest limit_price, or None if no buy orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.pop_best_buy() == o
        True
        >>> ob.buy_size() == 0
        True
        """
        if not self._buy_heap:
            return None
        return heapq.heappop(self._buy_heap)

    def pop_best_sell(self) -> Optional[Order]:
        """Remove and return the lowest-price sell order.

        Returns:
            The Order with the lowest limit_price, or None if no sell orders.

        Examples:
        >>> from engine.order import Order
        >>> from engine.order_book import OrderBook
        >>> ob = OrderBook()
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="sell", quantity=10, limit_price=150.0)
        >>> ob.add_order(o)
        >>> ob.pop_best_sell() == o
        True
        >>> ob.sell_size() == 0
        True
        """
        if not self._sell_heap:
            return None
        return heapq.heappop(self._sell_heap)

    def _serialize(self, order: Order) -> None:
        """Adds a sequence number to Order object

        Args:
            order (Order): Order to be serialized
        """
        if order.sequence != None:
            return

        order.sequence = self._global_seq

        self._global_seq += 1

    def buy_size(self) -> int:
        """Return the number of buy orders currently in the book.

        Examples:
        >>> from engine.order_book import OrderBook
        >>> from engine.order import Order
        >>> ob = OrderBook()
        >>> ob.buy_size()
        0
        >>> o = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=5, limit_price=50.0)
        >>> ob.add_order(o)
        >>> ob.buy_size()
        1
        """
        return len(self._buy_heap)

    def sell_size(self) -> int:
        """Return the number of sell orders currently in the book.

        Examples:
        >>> from engine.order_book import OrderBook
        >>> from engine.order import Order
        >>> ob = OrderBook()
        >>> ob.sell_size()
        0
        >>> o = Order(trader_id=2, symbol="AAPL", order_type="sell", quantity=3, limit_price=75.0)
        >>> ob.add_order(o)
        >>> ob.sell_size()
        1
        """
        return len(self._sell_heap)

    @property
    def total_size(self) -> int:
        """Return the total number of orders (buy + sell).

        Examples:
            >>> from engine.order_book import OrderBook
            >>> from engine.order import Order
            >>> ob = OrderBook()
            >>> ob.total_size
            0
            >>> ob.add_order(Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=1, limit_price=10.0))
            >>> ob.add_order(Order(trader_id=2, symbol="AAPL", order_type="sell", quantity=2, limit_price=20.0))
            >>> ob.total_size
            2
        """
        return len(self._buy_heap) + len(self._sell_heap)

    def get_buy_orders(self) -> List[Order]:
        """Return a list of all buy orders in descending priority (highest-price first).

        Examples:
            >>> from engine.order_book import OrderBook
            >>> from engine.order import Order
            >>> ob = OrderBook()
            >>> o1 = Order(trader_id=1, symbol="AAPL", order_type="buy", quantity=5, limit_price=50.0)
            >>> o2 = Order(trader_id=2, symbol="AAPL", order_type="buy", quantity=1, limit_price=55.0)
            >>> ob.add_order(o1)
            >>> ob.add_order(o2)
            >>> buys = ob.get_buy_orders()
            >>> [o.limit_price for o in buys]
            [55.0, 50.0]
        """
        heap_copy = list(self._buy_heap)

        return sorted(heap_copy, reverse=False)

    def get_sell_orders(self) -> List[Order]:
        """
        Return a list of all sell Orders currently in the book (lowest-priority first).

        Examples:
            >>> from engine.order_book import OrderBook
            >>> from engine.order import Order
            >>> ob = OrderBook()
            >>> o1 = Order(trader_id=1, symbol="AAPL", order_type="sell", quantity=5, limit_price=50.0)
            >>> o2 = Order(trader_id=2, symbol="AAPL", order_type="sell", quantity=1, limit_price=55.0)
            >>> ob.add_order(o1)
            >>> ob.add_order(o2)
            >>> sells = ob.get_sell_orders()
            >>> [o.limit_price for o in sells]
            [50.0, 55.0]
        """
        heap_copy = list(self._sell_heap)

        return sorted(heap_copy)
