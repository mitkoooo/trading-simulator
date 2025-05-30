import pytest
from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock


@pytest.fixture
def sample_market():
    data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
    return Exchange(market_data=data)


@pytest.fixture
def trader():
    return Trader(trader_id=1, cash_balance=1_000_000)
