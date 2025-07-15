import pytest
import logging

from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock
from engine.broker.broker import Broker

from app.session import Session
from app.context import AppContext


@pytest.fixture
def sample_exchange():
    data = {sym: Stock(sym, 100.0) for sym in ("AAPL", "MSFT")}
    return Exchange(market_data=data)

@pytest.fixture
def sample_broker(sample_exchange: Exchange):
    broker = Broker(exchange=sample_exchange)
    return broker


@pytest.fixture
def sample_trader(sample_broker: Broker):
    trader = Trader(trader_id=1, starting_balance=1_000_000)
    sample_broker.register_trader(trader)
    return trader


@pytest.fixture
def sample_trader2(sample_broker: Broker):
    trader = Trader(trader_id=2, starting_balance=1_000_000)
    sample_broker.register_trader(trader)
    return trader


@pytest.fixture
def test_context(sample_exchange: Exchange, sample_broker: Broker, sample_trader: Trader):
    session = Session(sample_broker.traders)
    session.login(sample_trader.trader_id)

    test_logger: logging.Logger = logging.getLogger("test")
    test_logger.propagate = True
    test_logger.setLevel(logging.INFO)

    return AppContext(exchange=sample_exchange, broker=sample_broker, session=session, logger=test_logger)
