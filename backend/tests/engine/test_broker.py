import pytest

from app.context import AppContext
from engine.position import Position
from engine.trader import Trader


@pytest.mark.asyncio
async def test_broker_reserves_cash_on_order(test_context: AppContext):
    symbol = "AAPL"
    order_type = "buy"
    quantity = 10
    limit_price = 10
    notional = quantity * limit_price

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    old_cash = trader.portfolio.cash

    broker = test_context.broker

    await broker.submit_order(tid, symbol, order_type, quantity, limit_price)
    assert trader.portfolio.cash == old_cash - notional


@pytest.mark.asyncio
async def test_broker_reserves_shares_on_order(test_context: AppContext):
    symbol = "AAPL"
    order_type = "sell"
    old_quantity = 10
    quantity = 10
    limit_price = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    trader.portfolio.positions[symbol] = Position(
        qty=old_quantity, avg_price=10
    )

    tid = trader.trader_id

    broker = test_context.broker

    await broker.submit_order(tid, symbol, order_type, quantity, limit_price)

    assert trader.portfolio.positions[symbol].qty == old_quantity - quantity


@pytest.mark.asyncio
async def test_broker_release_cash_on_cancel(test_context: AppContext):
    symbol = "AAPL"
    order_type = "buy"
    quantity = 10
    limit_price = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    old_cash = trader.portfolio.cash

    broker = test_context.broker

    o = await broker.submit_order(
        tid, symbol, order_type, quantity, limit_price
    )
    await broker.cancel_order(o.order_id)

    assert trader.portfolio.cash == old_cash


@pytest.mark.asyncio
async def test_broker_release_shares_on_cancel(test_context: AppContext):
    symbol = "AAPL"
    order_type = "sell"
    old_quantity = 10
    quantity = 10
    limit_price = 10

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id
    trader.portfolio.positions[symbol] = Position(
        qty=old_quantity, avg_price=10
    )

    broker = test_context.broker

    o = await broker.submit_order(
        tid, symbol, order_type, quantity, limit_price
    )

    await broker.cancel_order(o.order_id)

    assert trader.portfolio.positions[symbol].qty == old_quantity


@pytest.mark.asyncio
async def test_broker_reserves_cash_on_partial_fill(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"
    old_cash = sample_trader2.portfolio.cash
    quantity = 10
    limit_price = 10
    notional = quantity * limit_price

    trader1 = test_context.session.active_trader
    assert trader1
    trader1.portfolio.positions[symbol] = Position(qty=10, avg_price=10)

    trader2 = sample_trader2

    ask_id = trader1.trader_id
    bid_id = trader2.trader_id

    broker = test_context.broker

    await broker.submit_order(
        ask_id, symbol, "sell", quantity - 5, limit_price
    )
    await broker.submit_order(bid_id, symbol, "buy", quantity, limit_price)

    assert trader2.portfolio.cash == old_cash - notional

@pytest.mark.asyncio
async def test_cancel_order(test_context: AppContext):
    symbol = "AAPL"
    quantity = 42
    price = 42.00

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    # Add an order
    o = await broker.submit_order(tid, symbol, "buy", quantity, price)

    await exchange._book_queues[symbol].join()
    # Check the prequisites
    assert exchange.order_books[symbol].buy_size() == 1

    # Cancel an order
    await broker.cancel_order(o.order_id)
    await exchange._book_queues[symbol].join()

    assert exchange.order_lookup[o.order_id].status == "cancelled"

    assert exchange.order_books[symbol].buy_size() == 0


@pytest.mark.asyncio
async def test_cancel_order_invalid_id(test_context: AppContext):
    sample_exchange = test_context.exchange

    try:
        await sample_exchange.cancel_order("fake_order_id")
    except KeyError:
        assert True
        return

    # Raise AssertionError if error not returned
    raise AssertionError("Should not cancel an order with nonexistent id")


@pytest.mark.asyncio
async def test_cancel_fulfilled_order(test_context: AppContext):
    symbol = "AAPL"
    quantity = 42
    price = 42.00

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    # Add an order
    o = await broker.submit_order(tid, symbol, "buy", quantity, price)
    await exchange._book_queues[symbol].join()

    # Mutate order's status to fulfilled
    exchange.order_lookup[o.order_id].status = "filled"

    # Check the prequisites
    assert exchange.order_books[symbol].buy_size() == 1

    # Cancel an order
    assert not await exchange.cancel_order(o.order_id)
