from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass(frozen=True)
class MarketQuote:
    """SOME DOCSTRING""" #TODO
    symbol: str
    bid_price: Optional[float]
    bid_size: int
    ask_price: Optional[float]
    ask_size: int
    last_price: Optional[float]
    timestamp: datetime

    @property
    def mid(self) -> Optional[float]:
        if self.bid_price is None or self.ask_price is None:
            return None

        return (self.bid_price + self.ask_price) / 2

    @property
    def spread(self) -> Optional[float]:
        if self.bid_price is None or self.ask_price is None:
            return None

        return (self.ask_price - self.bid_price)

