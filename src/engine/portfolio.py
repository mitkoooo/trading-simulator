from typing import Dict

from .trade import Trade
from .stock import Stock


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
        self._holdings: Dict[str, int] = {}  # e.g. {"AAPL": 100, "GOOG": 50}

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
        # This method should:
        #  - If this trader was the buyer: deduct (trade.quantity x trade.price) from cash, and increase holdings[trade.symbol] by trade.quantity.
        #  - If this trader was the seller: add (trade.quantity x trade.price) to cash, and decrease holdings[trade.symbol] by trade.quantity.
        price, qty, symbol = trade.price, trade.quantity, trade.symbol

        if symbol not in self.holdings:
            self._holdings[symbol] = 0

        if trader_id == trade.buy_order.trader_id:
            self._cash -= qty * price
            self._holdings[symbol] += qty

        if trader_id == trade.sell_order.trader_id:
            self._cash += qty * price
            self._holdings[symbol] -= qty


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
