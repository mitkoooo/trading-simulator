from typing import Dict

from .trade import Trade
from .stock import Stock
from .order import Order
from .position import Position


class Portfolio:
    """
    Tracks a trader's positions and cash balance.

    Responsibilities (to be implemented in Week 2):
      - apply_trade(trade: Trade) → None
    """

    def __init__(self, starting_balance: float):
        """Create a Portfolio with starting cash and no positions.

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
        self._positions: Dict[str, Position] = {}  # e.g. {"AAPL": 100, "GOOG": 50}
        self._reserved_positions: Dict[str, Position] = {}

    @property
    def cash(self) -> float:
        """
        Returns current cash balance.
        """
        return self._cash

    @property
    def positions(self) -> Dict[str, Position]:
        """
        Returns a copy of the current positions dictionary.
        """
        return self._positions

    def apply_trade(self, trade: Trade, trader_id) -> None:
        """Update cash and positions based on a filled trade.

        Args:
            trade (Trade): Filled trade
        """
        price, qty, symbol = trade.price, trade.quantity, trade.symbol

        # Ensure we have keys in _positions / _reserved_positions
        pos = self._positions.setdefault(symbol, Position())
        reserved_pos = self._reserved_positions.setdefault(symbol, Position())

        # ===== BUY SIDE =====
        if trader_id == trade.buy_order.trader_id:
            # Grab original reservation details
            original_qty = trade.orig_buy_qty
            original_price = trade.buy_order.limit_price
            # Total cash originally set aside:
            old_reservation = original_qty * original_price

            # Unreserve the cash
            self._reserved_cash -= old_reservation

            # Calculate the actual cost
            actual_cost = qty * price

            # Refund unused reserved cash
            refund_amount = old_reservation - actual_cost
            if refund_amount > 0:
                self._cash += refund_amount

            # Deduct the actual cost
            self._cash -= actual_cost

            # Get old values to update the running avg
            old_qty, old_avg = pos.qty, pos.avg_price
            # Add the shares in
            pos.qty += qty
            # Calculate new avg
            pos.avg_price = (old_avg * old_qty + qty * price) / pos.qty

            remaining_qty = original_qty - qty
            # If partially filled, re-reserve the remaining cash
            if remaining_qty > 0:
                new_reservation = remaining_qty * original_price
                self._reserved_cash += new_reservation
                self._cash -= new_reservation

        # ===== SELL SIDE =====
        if trader_id == trade.sell_order.trader_id:
            # Needed to unreserve the holdings and refund unused ones
            original_qty = trade.orig_sell_qty
            remaining_qty = original_qty - qty

            # Unreserve the shares
            reserved_pos.qty -= original_qty

            proceeds = qty * price
            self._cash += proceeds

            # If partially filled, re-reserve the remaining shares
            if remaining_qty > 0:
                reserved_pos.qty = reserved_pos.qty + remaining_qty

        return

    def value(self, market_data: Dict[str, Stock]) -> float:
        """
        Compute total portfolio value: cash + Σ(position_qty x current_price).

        Args:
            market_data (Dict[str, Stock]): A mapping from symbol -> Stock object(which knows its current price).

        Returns:
            float: Total value of portfolio.
        """

        total = self._cash + self._reserved_cash

        # Add value of free positions
        for symbol, qty in self.positions.items():
            stock = market_data.get(symbol)
            price = stock.price if (stock is not None) else 0.0
            total += qty * price

        # Add value of reserved positions
        for symbol, qty in self._reserved_positions.items():
            stock = market_data.get(symbol)
            price = stock.price if (stock is not None) else 0.0
            total += qty * price

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
            self._reserved_cash += cost_estimate

        elif order.order_type == "sell":
            held = self._positions.get(sym, 0)
            if held < qty:
                raise ValueError("Insufficient shares to place sell order.")
            # Reserve shares
            self._positions[sym] = held - qty
            self._reserved_positions[sym] = self._reserved_positions.get(sym, 0) + qty

        else:
            raise ValueError(f"Unknown order_type: {order.order_type}")

    def calculate_unrealized_pl(
        self, symbol: str, market_data: Dict[str, Stock]
    ) -> float:
        """
        Compute unrealized P/L for the given symbol.

        Args:
            symbol (str): ticker symbol for the position
            market_data (Dict[str, Stock]): map from symbol to current Stock

        Returns:
            float: unrealized profit (positive) or loss (negative);
                   zero if you hold no position in symbol
        """

        pos = self._positions.get(symbol, Position())

        return (market_data[symbol].price - pos.avg_price) * pos.qty
