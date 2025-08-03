from datetime import datetime

from engine.bots.retail_poisson import RetailPoisson
from engine.exchange.exchange import Exchange
from engine.market_data.quote import MarketQuote


def test_update_mid_two_sided(sample_exchange: Exchange):
    symbol = "AAPL"
    expected = 11.0
    rp = RetailPoisson(sample_exchange, symbol, mpid="RP01")
    mq = MarketQuote(
        symbol=symbol,
        bid_price=10,
        bid_size=5,
        ask_price=12,
        ask_size=3,
        last_price=None,
        timestamp=datetime.now(),
    )
    rp.update_mid(mq)
    assert rp.current_mid == expected


def test_update_mid_ignores_when_empty_side(sample_exchange: Exchange):
    symbol = "AAPL"
    rp = RetailPoisson(sample_exchange, symbol, mpid="RP01")
    mq = MarketQuote(
        symbol,
        bid_price=10,
        bid_size=0,
        ask_price=12,
        ask_size=3,
        last_price=50,
        timestamp=datetime.now(),
    )
    rp.update_mid(mq)
    assert rp.current_mid is None


def test_update_mid_fallback_to_last_price(sample_exchange: Exchange):
    symbol = "AAPL"
    expected = 100
    rp = RetailPoisson(sample_exchange, symbol, mpid="RP01")
    mq = MarketQuote(
        symbol,
        bid_price=None,
        bid_size=5,
        ask_price=None,
        ask_size=5,
        last_price=100,
        timestamp=datetime.now(),
    )
    rp.update_mid(mq)
    assert rp.current_mid == expected
