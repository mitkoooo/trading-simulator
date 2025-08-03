from engine.order_book.order import Order


def test_order_constructor_invalid_qty():
    try:
        Order("BR01", "AAPL", "sell", -42)
        raise AssertionError("Order must not have negative quantity")
    except ValueError:
        assert True


def test_order_constructor_invalid_price():
    try:
        Order("BR01", "AAPL", "sell", 42, -100)
        raise AssertionError("Order must not have negative price")
    except ValueError:
        assert True
