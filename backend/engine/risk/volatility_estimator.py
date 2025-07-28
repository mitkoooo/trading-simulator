from collections import deque


class VolatilityEstimator:
    """SOME DOCSTRING""" #TODO

    @staticmethod
    def realized_vol(mid_history: deque[float]):
        # Guard clause against insufficient mid-price history
        # This gives us a tiny default spread on a stock rather than crashing
        if len(mid_history) < 2:
            return (mid_history[-1] if mid_history else 0.0) * 1e-4
        
        # Compute returns (%Δ) on mid-price history
        returns = [(mid_history[i] - mid_history[i-1]) / mid_history[i-1] for i in range(1, len(mid_history))]

        # Measure spread or variance of returns 
        var = sum(r*r for r in returns) / len(returns)

        # Convert to volatility (std × latest mid-price)
        # Final volatility tells market‑maker, “Prices are moving around by about $X on average,” 
        # so it can set its spread proportionally larger when X is big and tighter when X is small.
        return (var**0.5) * mid_history[-1]


