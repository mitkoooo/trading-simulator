from dataclasses import dataclass


@dataclass(frozen=True)
class Stock:
    """Capital stock of a company that is traded on the exchange.
    
    Attributes:
        symbol (str):
            A ticker symbol (eg. AAPL or MSFT).

        tick_size (float):
            Smallest price increment in which the prices are quoted.

        lot_size (int):
            Round lot, which is micro-lot (0.01) or 1 share by default

        currency (str):
            Currency in which the stock is traded (USD by default)

    """

    symbol: str
    tick_size: float
    lot_size: int = 1
    currency: str = "USD"
