class Stock:
    """Represent a tradable asset's price and history.

    Keeps track of a stock's symbol, its current price, and past prices
    so that other components (matching engine, analytics, UI) can replay
    or visualize its performance.

    Attributes:
      symbol (str): Ticker symbol (e.g. "AAPL").
      price (float): Latest market price.
      history (List[float]): Chronological list of previous prices.

    Example:
      >>> s = Stock("MTKO", 999.0)
      >>> next_price = s.simulate_price_tick()
      >>> s.update_price(next_price)
    """

    def __init__(self, symbol: str, price: float):
        self.symbol = symbol
        self.price = price
        self.history = [price]

    def update_price(self, new_price: float) -> None:
        """Update the stock's current price and append it to its history.

        Args:
          new_price (float): The new market price to set; must be non-negative.

        Returns:
          None

        Side-Effects:
          - Updates `self.price` to `new_price`.
          - Appends `new_price` to `self.history`.
        """

    def simulate_price_tick(self) -> float:
        """Returns the stock's next price

        Args:
          None

        Returns:
          float: The simulated next price (via random walk or historical data).
        """
