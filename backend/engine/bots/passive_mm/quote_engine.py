class QuoteEngine:
    """Computes bid and ask prices given market and position metrics.

    Uses volatility to set a base spread, adjusts for order-book imbalance,
    and skews quotes based on current inventory.
    """

    def __init__(self, alpha: float, beta: float,
                 gamma: float, base_size: int) -> None:
        """Initialize a QuoteEngine.
        
        Args:
            alpha (float):
                How much extra spread you demand per unit of volatility.

            beta (float):
                How much to tilt your quotes so your existing inventory 
                drifts back toward zero.

            gamma (float):
                How much to widen your spread if the book is lopsided.

            base_size (int):
                How many shares you quote on each side.

        """
        self.alpha, self.beta, self.gamma = alpha, beta, gamma
        self.base_size = base_size

    def compute(
        self, mid: float, vol: float, depth_imb: float, inventory: int
    ) -> tuple[float, float]:
        """Compute next bid and ask prices to quote.

        Args:
            mid (float):
                Last mid price quoted on the exchange.
            
            vol (float):
                Realized volatility of the asset.

            depth_imb (float):
                Difference between sizes of bid and ask `OrderBook` queues.

            inventory (int):
                Number of shares currently hold by Bot.
        
        Returns:
            (tuple[float, float]): Bid price and ask price in this order.

        """
        # Calculate base spread.
        # If prices are jumping around, you demand more compensation.
        # The spread grows in direct proportion to volatility.
        s0 = self.alpha * vol

        # Calculate adaptive spread.
        # If one side of the book is swollen (say lots of buys),
        # you widen your spread further.
        # Liquidity droughts and floods both deserve extra caution.
        s = s0 * (1 + self.gamma * abs(depth_imb))

        # Calculate inventory skew
        # If you're already long 1,000 shares, you'd rather sell than buy.
        # The term shifts both buy and sell downward when inventory is positive
        # gently nudging the market to help you unload.
        skew = self.beta * inventory * mid

        # You carve your spread equally around the midpoint,
        # then shift both sides by the skew.
        # Rounding to two decimals pins you to standard price ticks.
        half_spread = s / 2
        bid = round(mid - half_spread - skew, 2)
        ask = round(mid + half_spread - skew, 2)

        return bid, ask
