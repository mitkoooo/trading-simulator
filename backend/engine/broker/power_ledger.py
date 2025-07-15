from typing import Dict
from math import log1p

from engine.exchange import Exchange
from engine.position import Position
from engine.trader import Trader
from engine.order import Order

class PowerLedger:
    """TODO"""
    def __init__(self, exchange: Exchange, traders: Dict[int, Trader]):
        self.exchange = exchange
        self.traders = traders

        self._reserved_cash: Dict[str, float] = {}    # order_id -> cash amount
        self._reserved_shares: Dict[str, int] = {}    # order_id -> share number


    def reserve_cash(self, order: Order) -> None:
        """Reserve required cash for a new buy order."""
        tid = order.trader_id
        trader = self.traders.get(tid, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")

        if order.order_type != "buy":
            raise ValueError("Cannot reserve cash for a sell order.")
       
        quantity = order.quantity
        limit_price = order.limit_price
        symbol = order.symbol

        cost_estimate = quantity * limit_price if limit_price else self.estimate_market_buy_cost(symbol, quantity)
        
        if trader.portfolio.cash < cost_estimate:
            raise ValueError("Insufficient cash to place buy order.")
        # Reserve cash
        trader.portfolio.cash -= cost_estimate
        self._reserved_cash[order.order_id] = cost_estimate

        return


    def release_cash(self, order: Order) -> None:
        """Unreserve unused cash for a buy order."""
        tid = order.trader_id
        trader = self.traders.get(tid, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")

        
        reserved_amount = self._reserved_cash.pop(order.order_id)
        trader.portfolio.cash += reserved_amount

        return


    def reserve_shares(self, order: Order) -> None:
        """Reserve required shares for a new sell order"""
        tid = order.trader_id
        trader = self.traders.get(tid, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")

        if order.order_type != "sell":
            raise ValueError("Cannot reserve shares for a buy order.")

        quantity = order.quantity
        symbol = order.symbol
        position = trader.portfolio.positions.get(symbol, None)
        
        if not position:
            raise KeyError("Cannot reserve shares that the trader does not own.")

        held = position.qty

        if held < quantity:
            raise ValueError("Insufficient shares to place sell order.")

        trader.portfolio.positions[symbol].qty -= quantity

        self._reserved_shares[order.order_id] = self._reserved_shares.get(order.order_id, 0) + quantity

        return


    def release_shares(self, order: Order) -> None:
        """Unreserve unused shares for a sell order."""
        tid = order.trader_id
        trader = self.traders.get(tid, None)
        if not trader:
            raise KeyError(f"Trader with this trader id does not exist. (got {tid}")

        symbol = order.symbol
        position: Position | None = trader.portfolio.positions.get(symbol)
        reserved_quantity: int = self._reserved_shares.pop(order.order_id)

        if not position:
            raise KeyError("Cannot unreserve the shares that the trader does not own.")

        position.qty += reserved_quantity

        return 


    def estimate_market_buy_cost(self, symbol: str, quantity: int):
        """Estimates the total cost to buy `quantity` shares at market price,
        walking down the ask (sell) side of the order book.
        """
        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book
        # Not the most efficient method. If later causes problems,
        # try to approximate n based of quantity and order_book statistics
        sell_orders = order_book.get_n_sell_orders()

        remaining = quantity
        expected_cost = 0.0
        
        for sell in sell_orders:
            if sell.limit_price is None: # Market price sells dont contribute information
                continue

            fill_quantity = min(remaining, sell.quantity)
            expected_cost += fill_quantity * sell.limit_price
            remaining -= fill_quantity

            if remaining <= 0:
                break

        if remaining > 0:
            raise ValueError("Not enough market surplus liquidity to estimate cost.")

        return expected_cost * (1 + self._compute_slippage_buffer(symbol))

    def _compute_slippage_buffer(self, symbol: str) -> float:
        """Compute slippage buffer (safety margin) when estimating reservation amount for a market price buy."""
        BASE_LINE = 0.01

        stock = self.exchange.market_data.get(symbol, None)
        assert stock
        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book

        # Scale depth to [0, 1]-ish range using log
        liquidity_penalty = 1 / (1 + log1p(order_book.sell_size())) # shrinks fast
        
        slippage_buffer = BASE_LINE + stock.volatility * liquidity_penalty

        return min(slippage_buffer, 0.05) # cap at 5%

    def get_reserved_shares(self, order_id: str) -> int | None:
        return self._reserved_shares.get(order_id, None)

    def get_reserved_cash(self, order_id: str) -> float | None:
        return self._reserved_cash.get(order_id, None)
