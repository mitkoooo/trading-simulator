import asyncio, random

from typing import Dict, Literal
from engine.bots.passive_mm.inventory_manager import InventoryManager
from engine.bots.passive_mm.market_data_handler import MarketDataHandler
from engine.bots.passive_mm.quote_engine import QuoteEngine
from engine.bots.passive_mm.volatility_estimator import VolatilityEstimator

from engine.order_book.order import Order


class PassiveMM:
    """SOME DOCSTRING""" #TODO

    def __init__(self, exchange, symbol, mpid, 
                 base_size=50, alpha=1.0, beta=0.001, gamma=0.5, 
                 inventory_limit = 200, pnl_limit=1e5, hist_len=200, quote_interval=0.2):
        self.exchange = exchange
        self.symbol = symbol
        self.base_size = base_size
        self.mpid = mpid
        self.quote_interval = quote_interval
        self._running = False

        # Compose core blocks
        self.data_handler = MarketDataHandler(hist_len)
        self.vol_estimator = VolatilityEstimator()
        self.inv_manager = InventoryManager(inventory_limit, pnl_limit)
        self.quote_engine = QuoteEngine(alpha, beta, gamma, base_size)

        self.active_orders: Dict[Literal["buy", "sell"], Order] = {} # Order side -> Order

        self.exchange.subscribe(f"book_update:{symbol}", self.data_handler.on_book_update)
        self.exchange.subscribe(f"trade:{symbol}", lambda t: self.inv_manager.on_trade(t, mpid))

    async def run(self):
        self._running = True

        while self._running:
            # Risk check
            if self.inv_manager.risk_breached():
                for order in list(self.active_orders.values()):
                    self.exchange.cancel_order(order.order_id)
                self.active_orders.clear()
            else:
                # No mid price history? Wait.
                if len(self.data_handler.mid_history) < 2:
                    await asyncio.sleep(self.quote_interval)
                    continue

                mid = self.data_handler.mid_history[-1]
                # Compute volatility and depth imbalance
                vol = self.vol_estimator.realized_vol(self.data_handler.mid_history)
                imb = self.data_handler.get_depth_imbalance()

                buy_price, sell_price = self.quote_engine.compute(mid, vol, imb, self.inv_manager.position)

                # Add random scatter
                buy_price += random.choice([-0.01, 0.00, 0.01])
                sell_price -= random.choice([-0.01, 0.00, 0.01])

                await self._refresh_quotes(buy_price, sell_price)

            await asyncio.sleep(self.quote_interval + random.random() * 0.05)

    def stop(self):
        self._running = False

    async def _refresh_quotes(self, buy_price, sell_price):
        # Cancel stale orders if prices have changed
        for side, order in list(self.active_orders.items()):
            target = buy_price if side == "buy" else sell_price
            if order.limit_price != target:
                self.exchange.cancel_order(order.order_id)
                del self.active_orders[side]

        # Place missing orders
        for side, price in [("buy", buy_price), ("sell", sell_price)]:
            if side not in self.active_orders:
                assert side == "buy" or side == "sell"
                order = Order(mpid=self.mpid, symbol=self.symbol, order_type=side, quantity=self.base_size, limit_price=price)
                self.exchange.add_order(order)
                self.active_orders[side] = order

