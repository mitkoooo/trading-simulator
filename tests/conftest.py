import pytest
from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock


@pytest.fixture
def sample_market(trader: Trader):
    data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
    ex = Exchange(market_data=data)
    ex.register_trader(trader)
    return ex


@pytest.fixture
def trader():
    return Trader(trader_id=1, starting_balance=1_000_000)
