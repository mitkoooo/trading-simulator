from collections import deque
from typing import Iterator, Optional

from engine.order_book.order import Order
from engine.order_book.queue import OrderQueue


class PriceLevel(OrderQueue):
    """A FIFO bucket of orders all at a single price.

    Each PriceLevel holds a queue of `Order` objects that
    arrived at the same limit price.  It supports efficient
    FIFO enqueue/dequeue and tracks the aggregate share count.

    Attributes:
        _queue (collections.deque[Order]):
            Deque storing orders at the same price in FIFO sequence.
        total_shares (int):
            Sum of `order.quantity` for all orders currently in the queue.
    """

    def __init__(self) -> None:
        self._queue = deque[Order]()
        self.total_shares = 0

    def enqueue(self, order: Order) -> None:
        """Add an order to the back of the queue.

        Args:
            order (Order): The order to append.

        Side Effects:
            - Increments `total_shares` by `order.quantity`.
        """
        self._queue.append(order)
        self.total_shares += order.quantity

    def dequeue(self) -> Optional[Order]:
        """Remove and return the order at the front of the queue.

        Returns:
            Order or None:
                The oldest order in queue, `None` if queue is empty.

        Side Effects:
            - Decrements `total_shares` by the returned order's quantity.
        """
        if not self._queue:
            return None

        order = self._queue.popleft()
        self.total_shares -= order.quantity

        return order

    def peek(self) -> Optional[Order]:
        """Return the order at the front of the queue without removing it.

        Returns:
            Order or None: The oldest order, or `None` if the queue is empty.
        """
        return self._queue[0] if self._queue else None

    def remove(self, order: Order) -> None:
        """Remove a specific order from the queue.

        Args:
            order (Order): The order to remove.

        Side Effects:
            - Decrements `total_shares` by `order.quantity`.
        """
        self._queue.remove(order)
        self.total_shares -= order.quantity

    def clear(self):
        """Remove all orders from this price level.

        Side Effects:
            - Empties the queue.
            - Resets `total_shares` to zero.
        """
        self._queue.clear()
        self.total_shares = 0

    def is_empty(self) -> bool:
        """Check if the queue has no orders.

        Returns:
            bool: `True` if no orders are queued, `False` otherwise.
        """
        return not self._queue

    def __len__(self) -> int:
        return len(self._queue)

    def __getitem__(self, index: int) -> Optional[Order]:
        """Retrieve an order by position without removing it.

        Args:
            index (int): Zero-based index into the queue.

        Returns:
            Order or None: The order at `index`, or `None` if out of range.
        """
        if index == 0:
            return self.peek()

        try:
            return self._queue[index]
        except IndexError:
            return None

    def __bool__(self) -> bool:
        return bool(self._queue)

    def __iter__(self) -> Iterator[Order]:
        yield from self._queue

    def __repr__(self) -> str:
        return f"""<PriceLevel
                    orders={len(self)}
                    total_shares={self.total_shares}>"""
