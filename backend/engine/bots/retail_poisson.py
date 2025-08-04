import asyncio
import random
from dataclasses import dataclass
from typing import Literal

from engine.bots.base_bot import BaseBot
from engine.exchange.exchange import Exchange
from engine.market_data.quote import MarketQuote
from engine.order_book.order import Order


@dataclass
class RetailPoissonSettings:
    """Configuration for RetailPoisson bot simulating retail order flow.

    Attributes:
        limit_rate (float):
            Exponential rate (λ) for delay between market orders (events/sec).

        market_rate (float):
            Exponential rate for delay between limit orders.

        quantity_range (tuple[int, int]:
            Tuple of (min, max) shares/contracts per order.

        tick_size (float):
            Price increment for limit order offsets from mid price.

        market_probability (float):
            Probability of generating a market order instead of limit.

    """

    limit_rate: float = 1.0
    market_rate: float = 0.2
    quantity_range: tuple[int, int] = (1, 5)
    tick_size: float = 0.01
    market_probability: float = 0.3

class RetailPoisson(BaseBot):
    """Simulates a retail trader using a Poisson process for order arrivals.

    Generates limit and market orders for a single symbol according to
    configurable rates, quantities, and price tick sizes, aiming to mimic
    retail order flow dynamics.
    """

    def __init__(
        self,
        exchange: Exchange,
        symbol: str,
        mpid: str,
        settings: RetailPoissonSettings | None = None
    ) -> None:
        """Initialize a `RetailPoisson` Bot."""
        self.current_mid: float | None = None
        self.exchange = exchange
        self.symbol = symbol
        self.settings = settings if settings else RetailPoissonSettings()
        self.quantity_min, self.quantity_max = self.settings.quantity_range
        self._mpid = mpid
        self._running = False

        self.exchange.subscribe(f"book_update{symbol}", self.update_mid)
    
    @property
    def mpid(self) -> str:
        """Market participant ID of the RetailPoisson Bot."""
        return self._mpid

    def update_mid(self, market_quote: MarketQuote) -> None:
        """Update historical mid prices based on new market quote.
        
        Args:
            market_quote (MarketQuote): Latest market quotation.

        """
        if market_quote.bid_size == 0 or market_quote.ask_size == 0:
            return

        bid_price = market_quote.bid_price
        ask_price = market_quote.ask_price

        if not bid_price or not ask_price:
            if not market_quote.last_price:
                return
            reference_bid = reference_ask = market_quote.last_price
        else:
            reference_bid = bid_price
            reference_ask = ask_price

        self.current_mid = (reference_bid + reference_ask) / 2

    async def run(self) -> None:
        """Boot the bot's trading algorithm."""
        self._running = True
        while self._running:
            # Sample inter-arrival delay ~ (Poisson) Exponential(rate)
            if random.random() < self.settings.market_probability:
                order_type = "limit"
                delay = random.expovariate(self.settings.market_rate)
            else:
                order_type = "market"
                delay = random.expovariate(self.settings.limit_rate)
            await asyncio.sleep(delay)

            # Don't know mid and limit order? Do nothing.
            if order_type == "limit" and self.current_mid is None:
                continue

            # Randomly choose side
            side: Literal["buy", "sell"] = random.choice(["buy", "sell"])
            # Random size in configured size_range
            quantity = random.randint(self.quantity_min, self.quantity_max)

            # Place market order_book
            if order_type == "market":
                order = Order(
                    mpid=self.mpid,
                    order_type=side,
                    symbol=self.symbol,
                    quantity=quantity,
                    limit_price=None,
                )
            else:
                # one tick inward from mid
                tick_size = self.settings.tick_size 
                offset = -tick_size if side == "buy" else tick_size
                assert self.current_mid, ValueError(
                    "Current mid price is unexpectedly None"
                )
                price = round(self.current_mid + offset, 2)
                order = Order(
                    mpid=self.mpid,
                    order_type=side,
                    symbol=self.symbol,
                    quantity=quantity,
                    limit_price=price,
                )
            try:
                await self.exchange.add_order(order)
            except Exception:
                continue

    def stop(self) -> None:
        """Stop the bot's trading algorithm."""
        self._running = False
