from abc import ABC, abstractmethod
from typing import Iterator, Optional

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
        ...

    @abstractmethod
    def dequeue(self) -> Optional[Order]:
        ...

    @abstractmethod
    def peek(self) -> Optional[Order]:
        ...

    @abstractmethod
    def remove(self, order: Order) -> None:
        ...

    @abstractmethod
    def clear(self) -> None:
        ...

    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __iter__(self) -> Iterator[Order]:
        ...

    @abstractmethod
    def __repr__(self) -> str:
        ...
