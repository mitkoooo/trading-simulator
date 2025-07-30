from abc import ABC, abstractmethod
from collections.abc import Iterator

from engine.order_book.order import Order


class OrderQueue(ABC):
    """Abstract FIFO queue interface for Order objects.

    Specifies the core operations shared by all order queues:
    - enqueue: add an order to the back
    - dequeue: remove from the front
    - peek: inspect the front without removal
    - remove: delete a specific order
    - clear: empty the queue
    - __len__: count orders
    - __iter__: iterate in FIFO order
    """

    @abstractmethod
    def enqueue(self, order: Order) -> None:
        """Add `Order` to the back of `Queue.queue`."""
        ...

    @abstractmethod
    def dequeue(self) -> Order | None:
        """Remove the oldest `Order` from the front of `Queue.queue`."""
        ...

    @abstractmethod
    def peek(self) -> Order | None:
        """Return next `Order` at the front of `Queue.queue`."""
        ...

    @abstractmethod
    def remove(self, order: Order) -> None:
        """Remove `order` from `Queue.queue`."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Delete all `Order` objects from `Queue.queue`."""
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        """Return True if `Queue.queue` is empty, False otherwise."""
        ...

    @abstractmethod
    def __len__(self) -> int:
        """Compute length of `Queue.queue`."""
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[Order]:
        """Yield an iterator over `Queue.queue`."""
        ...

    @abstractmethod
    def __repr__(self) -> str:
        """Display representation string of `Queue`."""
        ...
