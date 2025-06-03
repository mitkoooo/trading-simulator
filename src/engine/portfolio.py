from typing import Dict

from .trade import Trade
from .stock import Stock
from .order import Order


class Portfolio:
    """
    Tracks a trader's holdings and cash balance.

    Responsibilities (to be implemented in Week 2):
      - apply_trade(trade: Trade) → None
      - get_position(symbol: str) → int
    """

    def __init__(self, starting_balance: float):
        """Create a Portfolio with starting cash and no holdings.

        Args:
            starting_balance (float): Initial cash to deposit

        Raises:
            ValueError: If starting_balance < 0

        """
        if starting_balance < 0:
            raise ValueError(
                f"starting_balance must be nonnegative. Starting balance provided: {starting_balance}"
            )

        self._cash: float = starting_balance
        self._reserved_cash: float = 0.0
        self._holdings: Dict[str, int] = {}  # e.g. {"AAPL": 100, "GOOG": 50}
        self._reserved_holdings: Dict[str, int] = {}

    @property
    def cash(self) -> float:
        """
        Returns current cash balance.
        """
        return self._cash

    @property
    def holdings(self) -> Dict[str, int]:
        """
        Returns a copy of the current holdings dictionary.
        """
        return self._holdings

    def apply_trade(self, trade: Trade, trader_id) -> None:
        """Update cash and holdings based on a filled trade.

        Args:
            trade (Trade): Filled trade
        """

        price, qty, symbol = trade.price, trade.quantity, trade.symbol

        # Ensure we have keys in _holdings / _reserved_holdings
        if symbol not in self.portfolio._holdings:
            self._holdings[symbol] = 0
        if symbol not in self.portfolio._reserved_holdings:
            self._reserved_holdings[symbol] = 0

        # ===== BUY SIDE =====
        if trader_id == trade.buy_order.trader_id:
            original_qty = trade.orig_buy_qty
            original_price = trade.buy_order.limit_price
            old_reservation = original_qty * original_price
            actual_cost = qty * price
            remaining_qty = original_qty - qty

            self._reserved_cash -= old_reservation

            refund_amount = old_reservation - actual_cost
            if refund_amount > 0:
                self._cash += refund_amount

            self._cash -= actual_cost

            self._holdings[symbol] += qty

            # If partially filled, re-reserve the remaining cash
            if remaining_qty > 0:
                new_reservation = remaining_qty * original_price
                self._reserved_cash += new_reservation
                self._cash -= new_reservation

        # ===== SELL SIDE =====
        if trader_id == trade.sell_order.trader_id:
            original_qty = trade.orig_sell_qty
            remaining_qty = original_qty - qty

            self._reserved_holdings[symbol] -= original_qty

            proceeds = qty * price
            self._cash += proceeds

            # If partially filled, re-reserve the remaining shares
            if remaining_qty > 0:
                self._reserved_holdings[symbol] = (
                    self._reserved_holdings.get(symbol, 0) + remaining_qty
                )

        return

    def value(self, market_data: Dict[str, Stock]) -> float:
        """
        Compute total portfolio value: cash + Σ(position_qty x current_price).

        Args:
            market_data (Dict[str, Stock]): A mapping from symbol -> Stock object(which knows its current price).

        Returns:
            float: Total value of portfolio.
        """

        total = self._cash

        for symbol, qty in self._holdings.items():
            current_price = market_data.get(symbol, None)

            if current_price is not None:
                current_price = current_price.price
            else:
                current_price = 0.0

            total += qty * current_price

        return total

    def reserve_assets(self, order: Order) -> None:
        """Reserve required cash or shares for a new buy/sell order."""
        qty = order.quantity
        price = order.limit_price
        sym = order.symbol

        if order.order_type == "buy":
            cost_estimate = qty * price
            if self.cash < cost_estimate:
                raise ValueError("Insufficient available cash to place buy order.")
            # Reserve cash
            self._cash -= cost_estimate
            self._cash_reserved += cost_estimate

        elif order.order_type == "sell":
            held = self._holdings.get(sym, 0)
            if held < qty:
                raise ValueError("Insufficient shares to place sell order.")
            # Reserve shares
            self._holdings[sym] = held - qty
            self._reserved_shares[sym] = self._reserved_shares.get(sym, 0) + qty

        else:
            raise ValueError(f"Unknown order_type: {order.order_type}")
