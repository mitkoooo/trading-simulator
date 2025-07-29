import pytest

from app.context import AppContext
from engine.position import Position
from engine.trader import Trader


@pytest.mark.asyncio
async def test_broker_reserves_cash_on_order(test_context: AppContext):
    SYMBOL = "AAPL"
    ORDER_TYPE = "buy"
    QUANTITY = 10
    LIMIT_PRICE = 10
    notional = QUANTITY * LIMIT_PRICE

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    old_cash = trader.portfolio.cash

    broker = test_context.broker

    await broker.submit_order(tid, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)
    assert trader.portfolio.cash == old_cash - notional


@pytest.mark.asyncio
async def test_broker_reserves_shares_on_order(test_context: AppContext):
    SYMBOL = "AAPL"
    ORDER_TYPE = "sell"
    old_quantity = 10
    QUANTITY = 10
    LIMIT_PRICE = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    trader.portfolio.positions[SYMBOL] = Position(
        qty=old_quantity, avg_price=10
    )

    tid = trader.trader_id

    broker = test_context.broker

    await broker.submit_order(tid, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)

    assert trader.portfolio.positions[SYMBOL].qty == old_quantity - QUANTITY


@pytest.mark.asyncio
async def test_broker_release_cash_on_cancel(test_context: AppContext):
    SYMBOL = "AAPL"
    ORDER_TYPE = "buy"
    QUANTITY = 10
    LIMIT_PRICE = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    old_cash = trader.portfolio.cash

    broker = test_context.broker

    o = await broker.submit_order(
        tid, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE
    )
    await broker.cancel_order(o.order_id)

    assert trader.portfolio.cash == old_cash


@pytest.mark.asyncio
async def test_broker_release_shares_on_cancel(test_context: AppContext):
    SYMBOL = "AAPL"
    ORDER_TYPE = "sell"
    old_quantity = 10
    QUANTITY = 10
    LIMIT_PRICE = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    trader.portfolio.positions[SYMBOL] = Position(
        qty=old_quantity, avg_price=10
    )

    broker = test_context.broker

    o = await broker.submit_order(
        tid, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE
    )

    await broker.cancel_order(o.order_id)

    assert trader.portfolio.positions[SYMBOL].qty == old_quantity


@pytest.mark.asyncio
async def test_broker_reserves_cash_on_partial_fill(
    test_context: AppContext, sample_trader2: Trader
):
    SYMBOL = "AAPL"
    old_cash = sample_trader2.portfolio.cash
    QUANTITY = 10
    LIMIT_PRICE = 10
    NOTIONAL = QUANTITY * LIMIT_PRICE

    trader1 = test_context.session.active_trader
    assert trader1
    trader1.portfolio.positions[SYMBOL] = Position(qty=10, avg_price=10)

    trader2 = sample_trader2

    ask_id = trader1.trader_id
    bid_id = trader2.trader_id

    broker = test_context.broker

    await broker.submit_order(
        ask_id, SYMBOL, "sell", QUANTITY - 5, LIMIT_PRICE
    )
    await broker.submit_order(bid_id, SYMBOL, "buy", QUANTITY, LIMIT_PRICE)

    assert trader2.portfolio.cash == old_cash - NOTIONAL
