from collections import deque
from typing import Deque, Iterator, Optional

from engine.order_book.order import Order
from engine.order_book.queue import OrderQueue


class MarketOrderQueue(OrderQueue):
    """A FIFO queue for market orders (orders without a limit price).

    Each queue holds only `Order` instances with `limit_price is None`.
    Supports efficient enqueue/dequeue in arrival order, arbitrary removal,
    and complete clearing of all orders.

    Attributes:
        _queue (collections.deque[Order]):
            Deque storing market orders in FIFO sequence.

    """

    def __init__(self):
        self._queue: Deque = deque[Order]()

    def enqueue(self, order: Order):
        """Add an order to the back of the queue.

        Args:
            order (Order): The order to append.

        Raises:
            (ValueError): If `order.limit_price` is not `None`.

        """
        if order.limit_price:
            raise ValueError("Cannot enqueue a limit order")

        self._queue.append(order)

    def dequeue(self) -> Optional[Order]:
        """Remove and return the order at the front of the queue.

        Returns:
            Order or None: The oldest order in queue, `None` if queue empty.

        """
        if not self._queue:
            return None
        order = self._queue.popleft()
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

        """
        self._queue.remove(order)

    def clear(self):
        """Remove all orders from this market price queue.

        Side Effects:
            - Empties the queue.
        """
        self._queue.clear()

    def is_empty(self) -> bool:
        """Check if the queue has no orders.

        Returns:
            bool: `True` if no orders are queued, `False` otherwise.

        """
        return not self._queue

    def __len__(self) -> int:
        return len(self._queue)

    def __getitem__(self, index: int) -> Order | None:
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
        return f"<MarketOrderQueue orders={len(self)}>"
