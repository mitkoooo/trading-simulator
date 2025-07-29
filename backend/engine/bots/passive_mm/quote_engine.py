from typing import Tuple


class QuoteEngine:
    """SOME DOCSTRING"""  # TODO

    def __init__(self, alpha, beta, gamma, base_size):
        # α (alpha): how much extra spread you demand per unit of volatility.
        # γ (gamma): how much to widen your spread if the book is lopsided.
        # β (beta): how much to tilt your quotes so your existing inventory drifts back toward zero.
        # base_size: how many shares you quote on each side.

        self.alpha, self.beta, self.gamma = alpha, beta, gamma
        self.base_size = base_size

    def compute(
        self, mid: float, vol: float, depth_imb: float, inventory: int
    ) -> Tuple[float, float]:
        """SOME DOCSTRING"""  # TODO
        # Calculate base spread.
        # If prices are jumping around, you demand more compensation.
        # The spread grows in direct proportion to volatility.
        s0 = self.alpha * vol

        # Calculate adaptive spread.
        # If one side of the book is swollen (say lots of buys), you widen your spread further.
        # Liquidity droughts and floods both deserve extra caution.
        s = s0 * (1 + self.gamma * abs(depth_imb))

        # Calculate inventory skew
        # If you’re already long 1 000 shares, you’d rather sell than buy.
        # This term shifts both buy and sell downward when inventory is positive (and upward when negative),
        # gently nudging the market to help you unload.
        skew = self.beta * inventory * mid

        # You carve your spread equally around the midpoint, then shift both sides by the skew.
        # Rounding to two decimals pins you to standard price ticks.
        half_spread = s / 2
        bid = round(mid - half_spread - skew, 2)
        ask = round(mid + half_spread - skew, 2)

        return bid, ask
