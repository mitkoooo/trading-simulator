import asyncio
import logging
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio

from app.context import AppContext
from app.session import Session
from engine.bots.bot_manager import BotManager
from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange
from engine.exchange.participant_info import (
    MarginCategory,
    ParticipantInfo,
    ParticipantType,
)
from engine.instruments.stock import Stock
from engine.trader import Trader


@pytest.fixture(scope="session")
def event_loop():
    """Create a session-scoped event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_exchange():
    exchange = Exchange()

    for symbol in ("AAPL", "MSFT"):
        stock = Stock(symbol=symbol, tick_size=1)
        exchange.register_instrument(stock)

        exchange.order_books[symbol].last_trade_price = 100

    return exchange


@pytest.fixture
def sample_broker(sample_exchange: Exchange):
    broker = Broker(exchange=sample_exchange, mpid="test_broker")
    return broker


@pytest.fixture
def sample_trader(sample_broker: Broker):
    trader = Trader(trader_id="1", starting_balance=1_000_000)
    sample_broker.register_trader(trader)
    return trader


@pytest.fixture
def sample_trader2(sample_broker: Broker):
    trader = Trader(trader_id="2", starting_balance=1_000_000)
    sample_broker.register_trader(trader)
    return trader


@pytest_asyncio.fixture
async def test_context(
    sample_exchange: Exchange, sample_broker: Broker, sample_trader: Trader
) -> AsyncGenerator[AppContext]:
    pi = ParticipantInfo(
        mpid="BR_TEST",
        display_name="Test Broker Alpha",
        ptype=ParticipantType.DIRECT_MEMBER,
        margin_category=MarginCategory.STANDARD_EQUITY,
        price_band_limit=None,
        allowed_symbols=["*"],
        max_order_size={},  # or {"AAPL": 5000, ...}
        max_notional_per_minute=1_000_000,
        max_msgs_per_second=200,
        clearing_member_id="TESTCLR1",
        settlement_account="TEST-ACCT-001",
        initial_cash=5_000_000.0,
        initial_positions={},
    )

    sample_exchange.register_participant(sample_broker.mpid, pi)
    
    bot_manager = BotManager()

    session = Session(sample_broker.traders)
    session.login(sample_trader.trader_id)

    test_logger: logging.Logger = logging.getLogger("test")
    test_logger.propagate = True
    test_logger.setLevel(logging.INFO)

    sample_exchange.start()

    yield AppContext(session, sample_broker, sample_exchange,
                     bot_manager, test_logger)

    await sample_exchange.stop()
