from collections import deque
from typing import Deque, List, Optional

from engine.market_data.quote import MarketQuote


class MarketDataHandler:
    """SOME DOCSTRING"""  # TODO

    def __init__(self, hist_len=200) -> None:
        self.mid_history: Deque[float] = deque(maxlen=hist_len)
        self.bid_size = self.ask_size = 0

    def on_book_update(self, market_quote: MarketQuote) -> None:
        # Guard clause for when either side is empty
        if market_quote.bid_size == 0 or market_quote.ask_size == 0:
            return

        if not market_quote.bid_price or not market_quote.ask_price:
            if not market_quote.last_price:
                return
            reference_bid = reference_ask = market_quote.last_price
        else:
            reference_bid = market_quote.bid_price
            reference_ask = market_quote.ask_price

        # Get order book depth for calculating depth imbalance later on.
        self.bid_size = market_quote.bid_size
        self.ask_size = market_quote.ask_size

        # Compute mid-price so you can estimate volatility and center your quotes.

        m_t = (reference_bid + reference_ask) / 2

        self.mid_history.append(m_t)

        return

    def get_mid(self) -> Optional[float]:
        return self.mid_history[-1] if self.mid_history else None

    def get_depth_imbalance(self) -> float:
        total = self.bid_size + self.ask_size or 1
        return (self.bid_size - self.ask_size) / total

    def get_mid_history(self) -> List[float]:
        return list(self.mid_history)
