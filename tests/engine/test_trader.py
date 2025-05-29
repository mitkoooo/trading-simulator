import pytest
from engine.trader import Trader
from engine.order import Order


def test_place_order_returns_order(trader: Trader):
    o = trader.place_order("AAPL", "sell", 42, 100.0)
    assert isinstance(o, Order)
    assert o.symbol == "AAPL"
    assert o.order_type == "sell"
    assert o.quantity == 42
    assert o.limit_price == 100.0
