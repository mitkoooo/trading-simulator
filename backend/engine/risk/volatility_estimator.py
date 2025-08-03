from collections import deque


class VolatilityEstimator:
    """Approximates volatility based of historical prices of an asset."""

    @staticmethod
    def realized_vol(mid_history: deque[float]) -> float:
        """Compute degree of variation of a trading price series over time.

        Calculated using the square root of the realized variance.

        Args:
            mid_history (deque[float]): Historical mid prices.

        Returns:
            (float): Realized volatility of a price.

        """
        # Guard clause against insufficient mid-price history
        # This gives us a tiny default spread on a stock rather than crashing
        min_len = 2

        if len(mid_history) < min_len:
            return (mid_history[-1] if mid_history else 0.0) * 1e-4

        # Compute returns (%Δ) on mid-price history
        def _compute_percentage_delta(old_val: float, new_val: float) -> float:
            return (new_val - old_val) / old_val

        returns = []
        n = len(mid_history)

        for i in range(1, n):
            old = mid_history[i]
            new = mid_history[i - 1]

            percentage_delta = _compute_percentage_delta(new, old)

            returns.append(percentage_delta)

        # Measure spread or variance of returns
        var = sum(r * r for r in returns) / len(returns)

        # Convert to volatility (std multiplied by latest mid-price)
        # Final volatility tells market-maker, "Prices are moving around by
        # about $X on average", so it can set its spread proportionally
        # larger when X is big and tighter when X is small.
        return (var**0.5) * mid_history[-1]
