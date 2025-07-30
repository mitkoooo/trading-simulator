import asyncio
from abc import ABC, abstractmethod


class BaseBot(ABC):
    @property
    @abstractmethod
    def mpid(self) -> str:
        """Unique identifier for market participants."""
        pass

    @abstractmethod
    async def run(self) -> asyncio.Task:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...


