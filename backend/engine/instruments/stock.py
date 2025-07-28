from asyncio import wait
from dataclasses import dataclass

@dataclass(frozen=True)
class Stock:
    """SOME DOCSTRING""" #TODO
    symbol: str
    tick_size: float
    lot_size: int = 1
    currency: str = "USD"


