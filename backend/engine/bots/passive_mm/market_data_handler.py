from collections import deque

from engine.market_data.quote import MarketQuote


class MarketDataHandler:
    """Tracks mid-price history and book-depth metrics from live quotes.

    Processes incoming `MarketQuote` updates to maintain a rolling deque
    of mid prices, and exposes methods to retrieve the latest mid,
    the full history, and the current bid/ask depth imbalance.
    """

    def __init__(self, hist_len: int = 200) -> None:
        """Initialize `MarketDataHandler`.

        Args:
            hist_len(int):
                Maximum allowed deque capacity holding historical mid prices.

        """
        self.mid_history: deque[float] = deque(maxlen=hist_len)
        self.bid_size = self.ask_size = 0

    def on_book_update(self, market_quote: MarketQuote) -> None:
        """Update historical mid prices on order book change.
        
        Args:
            market_quote (MarketQuote):
                Latest market quote on the exchange.

        """
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

        # Compute mid-price so you can estimate volatility and
        # center your quotes.

        m_t = (reference_bid + reference_ask) / 2

        self.mid_history.append(m_t)

        return

    def get_mid(self) -> float | None:
        """Retrieve latest mid price.

        Mid price is an average of bid and ask prices on the exchange.
        """
        return self.mid_history[-1] if self.mid_history else None

    def get_depth_imbalance(self) -> float:
        """Retrieve depth imbalance of the order book.

        Depth imbalance is the difference in depths of bid and ask queues.
        """
        total = self.bid_size + self.ask_size or 1
        return (self.bid_size - self.ask_size) / total

    def get_mid_history(self) -> list[float]:
        """Retrieve list of historical mid prices."""
        return list(self.mid_history)
