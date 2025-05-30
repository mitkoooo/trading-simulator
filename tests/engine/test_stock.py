from engine.stock import Stock


def test_tick_change_price():
    s = Stock("MTKO", 42.0)
    new = s.simulate_price_tick()

    assert isinstance(new, float)
    assert new != s.price


def test_tick_updates_value():
    s = Stock("MTKO", 42.0)
    s.update_price(50.0)

    assert s.price == 50.0
