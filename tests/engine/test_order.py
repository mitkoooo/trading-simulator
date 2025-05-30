from engine.order import Order


def test_order_constructor_invalid_qty():
    try:
        _ = Order(trader_id=1, symbol="AAPL", order_type="sell", quantity=-42)
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_price():
    try:
        _ = Order(
            trader_id=1, symbol="AAPL", order_type="sell", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_order_type():
    try:
        _ = Order(
            trader_id=1, symbol="AAPL", order_type="foo", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True
