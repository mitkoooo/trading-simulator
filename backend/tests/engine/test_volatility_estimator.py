from collections import deque

import pytest

from engine.risk.volatility_estimator import VolatilityEstimator


@pytest.mark.parametrize(
    "history, expected",
    [
        (deque(), 0.0),  # empty → 0 * 1e-4
        (deque([100.0]), 100.0 * 1e-4),  # single → price * 1e-4
    ],
)
def test_realized_vol_insufficient(history: deque[float], expected: float):
    """Guard clause when <2 data points."""
    result = VolatilityEstimator.realized_vol(history)
    assert result == pytest.approx(expected)


def test_realized_vol_two_points():
    """With two mid-prices [100, 105]:
    returns = [(105 - 100) / 100] = [0.05]
    var = 0.05^2 / 1 = 0.0025
    std = 0.05
    vol = std * latest_mid = 0.05 * 105 = 5.25
    """
    history = deque([100.0, 105.0])
    result = VolatilityEstimator.realized_vol(history)
    assert result == pytest.approx(5.25)


def test_realized_vol_multiple_points():
    """With three mid-prices [100, 110, 121]:
    returns = [0.10, 0.10]
    var = (0.01 + 0.01) / 2 = 0.01
    std = 0.1
    vol = 0.1 * 121 = 12.1
    """
    history = deque([100.0, 110.0, 121.0])
    result = VolatilityEstimator.realized_vol(history)
    assert result == pytest.approx(12.1)


def test_realized_vol_with_varying_returns():
    """A more varied history [100, 90, 99]:
    returns = [-0.10, 0.10]
    var = (0.01 + 0.01) / 2 = 0.01
    std = 0.1
    vol = 0.1 * 99 = 9.9
    """
    history = deque([100.0, 90.0, 99.0])
    result = VolatilityEstimator.realized_vol(history)
    assert result == pytest.approx(9.9)
