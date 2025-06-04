import pytest
from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock


@pytest.fixture
def sample_market():
    data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
    return Exchange(market_data=data)


@pytest.fixture
def trader(sample_market: Exchange):
    tr = Trader(trader_id=1, starting_balance=1_000_000)
    sample_market.register_trader(tr)
    return tr


@pytest.fixture
def trader2(sample_market: Exchange):
    tr = Trader(trader_id=2, starting_balance=1_000_000)
    sample_market.register_trader(tr)
    return tr
