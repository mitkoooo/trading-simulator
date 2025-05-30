import random
import math
from typing import List, Callable


class Stock:
    """Represents a tradable asset's price and history.

    Keeps track of a stock's symbol, its current price, and past prices
    so that other components (matching engine, analytics, UI) can replay
    or visualize its performance.

    Attributes:
      symbol (str): Ticker symbol (e.g. "AAPL").
      price (float): Latest market price.
      history (List[float]): Chronological list of previous prices.
      tick_model (Callable[["Stock"], float]): Function to simulate price change overtime (uniform stub; GBM in Week 8).
      volatility (float): Price's volatility rate.

    Examples:
      >>> s = Stock("MTKO", 999.0)
      >>> next_price = s.simulate_price_tick()
      >>> s.update_price(next_price)
    """

    def __init__(
        self,
        symbol: str,
        price: float,
        volatility: float = 0.01,
        tick_model: Callable[["Stock"], float] = None,
    ):
        """Initialize a Stock with a symbol, starting price, volatility, and optional model.

        Volatility is only used with GBM, and tick model is by default uniform ±1% random walk.
        """
        self.symbol = symbol
        self.price = price
        self.volatility = volatility
        self.history: List[float] = [price]
        self.tick_model = tick_model or self._uniform_stub

    def update_price(self, new_price: float) -> None:
        """Update the stock's current price and append it to its history.

        Args:
          new_price (float): The new market price to set; must be non-negative.

        Returns:
          None

        Side-Effects:
          - Updates `self.price` to `new_price`.
          - Appends `new_price` to `self.history`.

        Examples:
        >>> s = Stock("MTKO", 999.0)
        >>> old = s.price
        >>> s.update_price(new_price=1000.0)
        >>> new = s.price
        >>> old != new
        True
        """
        if new_price < 0:
            raise ValueError(
                f"Price must be non-negative. Computed negative price: {new_price}"
            )

        self.price = new_price
        self.history.append(new_price)

    def simulate_price_tick(self) -> float:
        """Delegate to the configured tick model and return the next price.

        Examples:
        >>> s = Stock("MTKO", 999.0)
        >>> old = s.price
        >>> next_price = s.simulate_price_tick()
        >>> s.update_price(next_price)
        >>> new = s.price
        >>> old != new
        True
        """

        return self.tick_model(self)

    @staticmethod
    def _uniform_stub(stock: "Stock") -> float:
        """Compute next price via uniform ±1% random walk.

        Week 1 stub.

        Args:
          stock (Stock): instance to simulate for.

        Returns:
          float: new price after ±1% move.

        Examples:
        >>> s = Stock("MTKO", 100.0, tick_model=Stock._uniform_stub)
        >>> new = Stock._uniform_stub(s)
        >>> isinstance(new, float)
        True
        """

        pct_change = random.uniform(-0.01, 0.01)
        return stock.price * (1 + pct_change)

    @staticmethod
    def gbm_model(stock: "Stock") -> float:
        """Compute next price via Gaussian GBM.

        Tick model that is used after week 8.

        Args:
          stock (Stock): The stock whose next price is to be determined

        Returns:
          float: The stock's next price based on Gaussian GBM model

        Examples:
        >>> s = Stock("MTKO", 999.0, tick_model=Stock.gbm_model)
        >>> old = s.price
        >>> next_price = s.simulate_price_tick()
        >>> s.update_price(next_price)
        >>> new = s.price
        >>> old != new
        True
        """
        sigma = stock.volatility
        z = random.gauss(0, 1)
        computed_price = stock.price * math.exp(sigma * z - 0.5 * sigma**2)

        return max(0.0, computed_price)
