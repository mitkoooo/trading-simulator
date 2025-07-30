
from engine.market_data.quote import MarketQuote

from .position import Position


class Portfolio:
    """Tracks a trader's positions and cash balance."""

    def __init__(self, starting_balance: float) -> None:
        """Create a Portfolio with starting cash and no positions.

        Args:
            starting_balance (float): Initial cash to deposit

        Raises:
            ValueError: If starting_balance < 0

        """
        if starting_balance < 0:
            msg = f"""starting_balance must be nonnegative.
                      Starting balance provided: {starting_balance}"""

            raise ValueError(msg)

        self.cash: float = starting_balance
        self.reserved_cash: float = 0.0
        self.positions: dict[str, Position] = {}
        self.reserved_positions: dict[str, Position] = {}

    def value(self, quotes: dict[str, MarketQuote]) -> float:
        """Compute total portfolio value.
            
        Total value = cash + Σ(position_qty x current_price).

        Args:
            quotes (Dict[str, MarketQuote]):
                A mapping from symbol -> MarketQuote.

        Returns:
            float: Total value of portfolio.

        """
        total = self.cash + self.reserved_cash

        # Add value of free positions
        for symbol, position in self.positions.items():
            quote = quotes.get(symbol)

            if quote is not None and quote.last_price is not None:
                price = quote.last_price
            else:
                price = 0.0

            total += position.qty * price

        # Add value of reserved positions
        for symbol, position in self.reserved_positions.items():
            quote = quotes.get(symbol)

            if quote is not None and quote.last_price is not None:
                price = quote.last_price
            else:
                price = 0.0

            total += position.qty * price

        return total

    def calculate_unrealized_pl(
        self, symbol: str, quotes: dict[str, MarketQuote]
    ) -> float | None:
        """Compute unrealized P/L for the given symbol.

        Args:
            symbol (str): ticker symbol for the position
            quotes (Dict[str, MarketQuote]): map from symbol to its quote.

        Returns:
            float: unrealized profit (positive) or loss (negative);
                   zero if you hold no position in symbol

        """
        if symbol not in quotes:
            msg = f"""Cannot calculate unrealized P/L
                        for a nonexistent symbol (Got {symbol})."""

            raise ValueError(msg)

        pos = self.positions.get(symbol, Position())

        last = quotes[symbol].last_price

        if not last:
            return None

        return (last - pos.avg_price) * pos.qty
