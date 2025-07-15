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

        self.cash: float = starting_balance
        self.reserved_cash: float = 0.0
        self.positions: Dict[str, Position] = {}  # e.g. {"AAPL": 100, "GOOG": 50}
        self.reserved_positions: Dict[str, Position] = {}


    def value(self, market_data: Dict[str, Stock]) -> float:
        """
        Compute total portfolio value: cash + Σ(position_qty x current_price).

        Args:
            market_data (Dict[str, Stock]): A mapping from symbol -> Stock object(which knows its current price).

        Returns:
            float: Total value of portfolio.
        """

        total = self.cash + self.reserved_cash

        # Add value of free positions
        for symbol, position in self.positions.items():
            stock = market_data.get(symbol)
            price = stock.price if (stock is not None) else 0.0
            total += position.qty * price

        # Add value of reserved positions
        for symbol, position in self.reserved_positions.items():
            stock = market_data.get(symbol)
            price = stock.price if (stock is not None) else 0.0
            total += position.qty * price

        return total




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

        if symbol not in market_data:
            raise ValueError(
                f"Cannot calculate unrealized P/L for a nonexistent symbol (Got {symbol})."
            )

        pos = self.positions.get(symbol, Position())

        return (market_data[symbol].price - pos.avg_price) * pos.qty
