import asyncio
import random
from typing import Literal

from engine.bots.base_bot import BaseBot
from engine.bots.passive_mm.inventory_manager import InventoryManager
from engine.bots.passive_mm.market_data_handler import MarketDataHandler
from engine.bots.passive_mm.quote_engine import QuoteEngine
from engine.exchange.exchange import Exchange
from engine.order_book.order import Order
from engine.risk.volatility_estimator import VolatilityEstimator


class PassiveMMSettings:
    """Configuration parameters for the Passive Market-Making bot.

    Attributes:
        base_size (int):
            Number of shares to quote on each side.

        alpha (float):
            Spread multiplier per unit of realized volatility.

        beta (float):
            Inventory skew factor to drift position toward zero.

        gamma (float):
            Additional spread factor for order-book imbalance.

        inv_limit (int):
            Maximum allowable inventory before risk triggers.

        pnl_limit (float):
            Maximum allowable P&L deviation before risk triggers.

        hist_len (int):
            Length of mid-price history for volatility estimation.

        quote_interval (float):
            Time interval (seconds) between quote updates.

    """

    base_size: float = 50
    alpha: float = 1.0
    beta: float = 0.001
    gamma: float = 0.5
    inv_limit: int = 200
    pnl_limit: float = 1e5
    hist_len: int = 200
    quote_interval: float = 0.2


class PassiveMM(BaseBot):
    """Places adaptive bid/ask quotes around the mid-price.

    A passive market-making bot that adjusts its spread based on
    volatility, order-book imbalance, and inventory, refreshing quotes
    at fixed intervals with random scatter and enforcing risk limits.
    """

    def __init__(
        self,
        exchange: Exchange,
        symbol: str,
        mpid: str,
        settings: PassiveMMSettings | None = None
        ) -> None:
        """Initialize a `PassiveMM`.

        Args:
            exchange (Exchange):
                The exchange in which bot is registered.

            symbol (str):
                A ticker symbol which the bot trades.

            mpid (str):
                Market participant id of the bot.

            settings (PassiveMMSettings):
                Optional configurable settings for the bot.

        """
        self.exchange = exchange
        self.symbol = symbol
        self._mpid = mpid
        self.settings = settings if settings else PassiveMMSettings()
        self._running = False

        # Compose core blocks
        hist_len = self.settings.hist_len
        inv_limit = self.settings.inv_limit
        pnl_limit = self.settings.pnl_limit
        alpha = self.settings.alpha
        beta = self.settings.beta
        gamma = self.settings.gamma
        base_size = self.settings.base_size

        self.data_handler = MarketDataHandler(hist_len)
        self.vol_estimator = VolatilityEstimator()
        self.inv_manager = InventoryManager(mpid, inv_limit, pnl_limit)
        self.quote_engine = QuoteEngine(alpha, beta, gamma, base_size)

        self.active_orders: dict[
            Literal["buy", "sell"], Order
        ] = {}  # Order side -> Order

        self.exchange.subscribe(
            f"book_update:{symbol}", self.data_handler.on_book_update
        )
        self.exchange.subscribe(
            f"trade:{symbol}:{mpid}", lambda t: self.inv_manager.on_trade(t)
        )

    @property
    def mpid(self) -> str:
         """Market participant ID of the PassiveMarketMaker Bot."""
         return self._mpid

    async def run(self) -> None:
        """Boot the bot's trading algorithm."""
        min_len = 2
        self._running = True

        while self._running:
            # Risk check
            if self.inv_manager.risk_breached():
                for order in list(self.active_orders.values()):
                    await self.exchange.cancel_order(order.order_id)
                self.active_orders.clear()
            else:
                # No mid price history? Wait.
                if len(self.data_handler.mid_history) < min_len:
                    await asyncio.sleep(self.quote_interval)
                    continue

                mid = self.data_handler.mid_history[-1]
                # Compute volatility and depth imbalance
                vol = self.vol_estimator.realized_vol(
                    self.data_handler.mid_history
                )
                imb = self.data_handler.get_depth_imbalance()

                buy_price, sell_price = self.quote_engine.compute(
                    mid, vol, imb, self.inv_manager.position
                )

                # Add random scatter
                buy_price += random.choice([-0.01, 0.00, 0.01])
                sell_price -= random.choice([-0.01, 0.00, 0.01])

                await self._refresh_quotes(buy_price, sell_price)
                
            await asyncio.sleep(self.quote_interval + random.random() * 0.05)

    def stop(self) -> None:
        """Stop the bot's trading algorithm."""
        self._running = False

    async def _refresh_quotes(self, bid_price: float,
                              ask_price: float) -> None:

        # Cancel stale orders if prices have changed
        for side, order in list(self.active_orders.items()):
            target = bid_price if side == "buy" else ask_price
            if order.limit_price != target:
                try:
                    await self.exchange.cancel_order(order.order_id)
                    del self.active_orders[side]
                except RuntimeError:
                    pass

        # Place missing orders
        for side, price in [("buy", bid_price), ("sell", ask_price)]:
            if side not in self.active_orders:
                assert side in {"buy", "sell"}
                order = Order(
                    mpid=self.mpid,
                    symbol=self.symbol,
                    order_type=side,
                    quantity=self.settings.base_size,
                    limit_price=price,
                )
                await self.exchange.add_order(order)
                self.active_orders[side] = order
