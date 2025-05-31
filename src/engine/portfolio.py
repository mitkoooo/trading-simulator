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

    def apply_trade(self, trade: Trade) -> None:
        """Update cash and holdings based on a filled trade.

        Args:
            trade (Trade): Filled trade
        """
        # +TODO: After finishing Trade, finish this method

        # This method should:
        # 1. Deduct executed_qty * execution_price from cash for a BUY.
        # 2. Add executed_qty * execution_price to cash for a SELL.
        # 3. Increase (or decrease) positions[trade.symbol] accordingly.
        pass


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
