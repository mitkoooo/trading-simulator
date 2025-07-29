from collections import deque
from math import log1p
from typing import Deque, Dict, Optional

from engine.exchange.exchange import Exchange
from engine.market_data.quote import MarketQuote
from engine.order_book.order import Order
from engine.position import Position
from engine.risk.volatility_estimator import VolatilityEstimator
from engine.trader import Trader


class PowerLedger:
    """Manage reservations of cash and shares for orders.

    The PowerLedger tracks reserved cash for buy orders and reserved shares
    for sell orders, ensuring that funds or holdings are set aside when orders
    are submitted and released when orders are cancelled or filled.

    Attributes:
        exchange (Exchange):
            The central entity providing order books and market data.
        traders (Dict[int, Trader]):
            Mapping of trader IDs to `Trader` objects with portfolios.
        _reserved_cash (Dict[str, float]):
            Maps order IDs to the amount of cash reserved for buy orders.
        _reserved_shares (Dict[str, int]):
            Maps order IDs to the quantity of shares reserved for sell orders.

    """

    def __init__(
        self,
        exchange: Exchange,
        traders: Dict[str, Trader],
        volatility_window: int = 100,
    ):
        self.exchange = exchange
        self.traders = traders

        self.volatility_window = volatility_window
        self.volatility_estimator = VolatilityEstimator()
        self.mid_histories: Dict[str, Deque[float]] = {}

        for symbol in self.exchange.instruments:
            self.mid_histories[symbol] = deque(maxlen=volatility_window)

        # order_id -> cash amount
        self._reserved_cash: Dict[str, float] = {}

        # order_id -> share number
        self._reserved_shares: Dict[str, int] = {}

    def reserve_cash(self, trader_id: str, order: Order) -> None:
        """Reserve cash for a new buy order.

        Deducts an estimated cost from the trader’s cash balance and reserves
        it under the order ID.

        Args:
            order (Order): A buy order requiring cash reservation.

        Raises:
            KeyError: If the trader is not registered.
            ValueError: If `order.order_type` is not 'buy' or if the trader’s
                cash balance is insufficient.

        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            msg = f"Trader with id {trader_id} does not exist."
            raise KeyError(msg)

        if order.order_type != "buy":
            raise ValueError("Cannot reserve cash for a sell order.")

        quantity = order.quantity
        limit_price = order.limit_price
        symbol = order.symbol

        if limit_price:
            cost_estimate = quantity * limit_price
        else:
            cost_estimate = self.estimate_market_buy_cost(symbol, quantity)

        if trader.portfolio.cash < cost_estimate:
            raise ValueError("Insufficient cash to place buy order.")
        # Reserve cash
        trader.portfolio.cash -= cost_estimate
        self._reserved_cash[order.order_id] = cost_estimate

        return

    def release_cash(self, trader_id: str, order: Order) -> None:
        """Release reserved cash back to the trader’s balance.

        Returns the full reserved amount for the given buy order ID to the
        trader’s cash, removing the reservation record.

        Args:
            order (Order): A previously reserved buy order.

        Raises:
            KeyError: If the trader is not registered

        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            msg = f"Trader with id {trader_id} does not exist."
            raise KeyError(msg)

        reserved_amount = self._reserved_cash.pop(order.order_id)
        trader.portfolio.cash += reserved_amount

        return

    def reserve_shares(self, trader_id: str, order: Order) -> None:
        """Reserve shares for a new sell order.

        Deducts the order’s quantity from the trader’s position and reserves
        it under the order ID.

        Args:
            order (Order):
                A sell order requiring share reservation.

        Raises:
            KeyError:
                If the trader is not registered or does not hold the shares.
            ValueError:
                If the trader’s position is insufficient.

        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            msg = f"Trader with id {trader_id} does not exist."
            raise KeyError(msg)

        if order.order_type != "sell":
            msg = "Cannot reserve shares for a buy order."
            raise ValueError(msg)

        quantity = order.quantity
        symbol = order.symbol
        position = trader.portfolio.positions.get(symbol, None)

        if not position:
            msg = "Cannot reserve shares that the trader does not own."
            raise KeyError(msg)

        held = position.qty

        if held < quantity:
            msg = "Insufficient shares to place sell order."
            raise ValueError(msg)

        trader.portfolio.positions[symbol].qty -= quantity

        prev_reserved = self._reserved_shares.get(order.order_id, 0)

        self._reserved_shares[order.order_id] = prev_reserved + quantity

        return

    def release_shares(self, trader_id: str, order: Order) -> None:
        """Release reserved shares back to the trader’s position.

        Returns the full reserved share quantity for the given sell order
        back to the trader’s position, removing the reservation record.

        Args:
            order (Order):
                A previously reserved sell order.

        Raises:
            KeyError:
                If the trader is not registered.

        """
        trader = self.traders.get(trader_id, None)
        if not trader:
            msg = f"Trader with id of {trader_id} does not exist."
            raise KeyError(msg)

        symbol = order.symbol
        position: Position | None = trader.portfolio.positions.get(symbol)
        reserved_quantity: int = self._reserved_shares.pop(order.order_id)

        if not position:
            msg = "Cannot unreserve the shares that the trader does not own."
            raise KeyError(msg)

        position.qty += reserved_quantity

        return

    def consume_quote(self, quote: MarketQuote) -> None:
        """SOME DOCSTRING"""  # TODO
        symbol = quote.symbol
        bid_price = quote.bid_price
        ask_price = quote.ask_price

        if not bid_price or not ask_price:
            return

        # Calculate mid price
        mid_price = (bid_price + ask_price) / 2

        if self.mid_histories.get(symbol, None) is None:
            self.mid_histories[symbol] = deque(maxlen=self.volatility_window)
        self.mid_histories[symbol].append(mid_price)

        return

    def estimate_market_buy_cost(self, symbol: str, quantity: int):
        """Estimate the total cost of a market-price buy order.

        Walks the sell-side order book until the requested quantity is covered,
        summing limit prices, then applies a slippage buffer.

        Args:
            symbol (str):
                The stock symbol to buy.
            quantity (int):
                The number of shares to estimate.

        Returns:
            float:
                Estimated cost including slippage buffer.

        Raises:
            ValueError:
                If book liquidity is insufficient to fill the request.

        """
        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book
        # Not the most efficient method. If later causes problems,
        # try to approximate n based of quantity and order_book statistics
        sell_orders = order_book.get_n_sell_orders()

        remaining = quantity
        expected_cost = 0.0

        for sell in sell_orders:
            # Market price sells dont contribute information
            if sell.limit_price is None:
                continue

            fill_quantity = min(remaining, sell.quantity)
            expected_cost += fill_quantity * sell.limit_price
            remaining -= fill_quantity

            if remaining <= 0:
                break

        if remaining > 0:
            msg = "Not enough market surplus liquidity to estimate cost."
            raise ValueError(msg)

        return expected_cost * (1 + self._compute_slippage_buffer(symbol))

    def _compute_slippage_buffer(self, symbol: str) -> float:
        """Compute a safety margin for market‐buy cost estimates.

        Calculates a slippage buffer based on baseline percentage, current
        volatility, and book depth.

        Args:
            symbol (str):
                The stock symbol for which to compute slippage.

        Returns:
            float: A slippage factor (e.g. between 0.01 and 0.05).

        """
        BASE_LINE = 0.01

        order_book = self.exchange.order_books.get(symbol, None)
        assert order_book

        realized_vol = self.volatility_estimator.realized_vol
        vol = realized_vol(self.mid_histories[symbol])

        # Scale depth to [0, 1]-ish range using log
        liquidity_penalty = 1 / (1 + log1p(order_book.sell_size()))
        slippage_buffer = BASE_LINE + vol * liquidity_penalty

        return min(slippage_buffer, 0.05)  # cap at 5%

    def get_reserved_shares(self, order_id: str) -> int:
        """Get the quantity of shares reserved for a given order ID.

        Args:
            order_id (str):
                The identifier of the sell order.

        Returns:
            int or None:
                Reserved share count, or None if no reservation exists.

        """
        return self._reserved_shares.get(order_id, 0)

    def get_reserved_cash(self, order_id: str) -> Optional[float]:
        """Get the amount of cash reserved for a given order ID.

        Args:
            order_id (str):
                The identifier of the buy order.

        Returns:
            float or None:
                Reserved cash amount, or None if no reservation exists.

        """
        return self._reserved_cash.get(order_id, None)

    def __repr__(self) -> str:
        cash_n = len(self._reserved_cash)
        share_n = len(self._reserved_shares)
        cash_sum = sum(self._reserved_cash.values())
        share_sum = sum(self._reserved_shares.values())

        return (
            f"<PowerLedger traders={len(self.traders)} "
            f"cash_orders={cash_n} cash_reserved={cash_sum:.2f} "
            f"share_orders={share_n} shares_reserved={share_sum} "
            f"exchange={getattr(self.exchange, 'name', 'Exchange')}>"
        )
