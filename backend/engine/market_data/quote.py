from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MarketQuote:
    """Current price at which a stock or commodity is being traded.

    Attributes:
        symbol (str):
            A ticker symbol (eg. AAPL or MSFT).

        bid_price (float or None):
            Currently highest bid price.

        bid_size (int or None):
            Current number of bid orders in order book.

        ask_price (float or None):
            Currently lowest ask price.

        ask_size (int or None):
            Current number of ask orders in order book.

        last_price (float or None):
            Latest price at which a stock or a commodity was traded.

        daily_vol (int or None):
            Current daily volume of shares traded so far.

    """

    symbol: str
    bid_price: float | None
    bid_size: int
    ask_price: float | None
    ask_size: int
    last_price: float | None
    daily_vol: int | None
    timestamp: datetime

    @property
    def mid(self) -> float | None:
        """Computes a mid price, which is average of bid and ask prices."""
        if self.bid_price is None or self.ask_price is None:
            return None

        return (self.bid_price + self.ask_price) / 2

    @property
    def spread(self) -> float | None:
        """Computes spread of a market quotation.

        Spread is a difference between ask and bid prices.
        """
        if self.bid_price is None or self.ask_price is None:
            return None

        return self.ask_price - self.bid_price
