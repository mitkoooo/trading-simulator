from engine.exchange import Exchange
from engine.trader import Trader


def test_add_order_and_match_stub(sample_market: Exchange, trader: Trader):
    o = trader.place_order("AAPL", "buy", 42, 42.0)
    sample_market.add_order(o)
    trades = sample_market.match_orders("AAPL")
    assert trades == []  # still a stub
