import asyncio
from abc import ABC, abstractmethod


class BaseBot(ABC):
    """Abstract parent class that encapsulates core shared features of bots."""

    @property
    @abstractmethod
    def mpid(self) -> str:
        """Unique identifier of the bots on the exchange."""
        pass

    @abstractmethod
    async def run(self) -> asyncio.Task:
        """Boot the bot's trading algorithm.
        
        Returns:
            (asyncio.Task): Task that executes bot's algorithm.

        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop the bot's trading algorithm."""
        ...


