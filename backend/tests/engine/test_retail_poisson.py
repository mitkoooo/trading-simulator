from datetime import datetime
from engine.bots.retail_poisson import RetailPoisson
from engine.exchange.exchange import Exchange
from engine.market_data.quote import MarketQuote


def test_update_mid_two_sided(sample_exchange: Exchange):
    SYMBOL = "AAPL"
    rp = RetailPoisson(sample_exchange, SYMBOL, mpid="RP01")
    mq = MarketQuote(symbol=SYMBOL, bid_price=10, bid_size=5, ask_price=12,
                     ask_size=3, last_price=None, timestamp=datetime.now())
    rp._update_mid(mq)
    assert rp.current_mid == 11.0


def test_update_mid_ignores_when_empty_side(sample_exchange: Exchange):
    SYMBOL = "AAPL"
    rp = RetailPoisson(sample_exchange, SYMBOL, mpid="RP01")
    mq = MarketQuote(SYMBOL, bid_price=10, bid_size=0, ask_price=12,
                     ask_size=3, last_price=50, timestamp=datetime.now())
    rp._update_mid(mq)
    assert rp.current_mid is None


def test_update_mid_fallback_to_last_price(sample_exchange: Exchange):
    SYMBOL = "AAPL"
    rp = RetailPoisson(sample_exchange, SYMBOL, mpid="RP01")
    mq = MarketQuote(SYMBOL, bid_price=None, bid_size=5, ask_price=None,
                     ask_size=5, last_price=100, timestamp=datetime.now())
    rp._update_mid(mq)
    assert rp.current_mid == 100
