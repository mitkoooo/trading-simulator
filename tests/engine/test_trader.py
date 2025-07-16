from engine.order_book.order import Order

from app.context import AppContext


def test_place_order_returns_order(test_context: AppContext):
    sample_trader = test_context.session.active_trader

    o = sample_trader.create_order("AAPL", "buy", 42, 100.0)
    assert isinstance(o, Order)
    assert o.symbol == "AAPL"
    assert o.order_type == "buy"
    assert o.quantity == 42
    assert o.limit_price == 100.0
