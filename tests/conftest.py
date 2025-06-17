import pytest

import logging

from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock

from app.session import Session
from app.context import AppContext


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


@pytest.fixture
def test_context(sample_market: Exchange, trader: Trader, caplog):
    session = Session(sample_market.traders)
    session.login(trader.trader_id)

    test_logger = logging.getLogger("test")
    test_logger.propagate = True
    test_logger.setLevel(logging.INFO)

    # 2) tell caplog to capture that logger at INFO
    caplog.set_level(logging.INFO, logger="test")

    return AppContext(exchange=sample_market, session=session, logger=test_logger)
