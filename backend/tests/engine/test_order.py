import pytest

from engine.order_book.order import Order
from app.context import AppContext


def test_order_constructor_invalid_qty():
    try:
        Order("BR01", "AAPL", "sell", -42)
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_price():
    try:
        Order("BR01", "AAPL", "sell", 42, -100)
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_order_type():
    try:
        Order("BR01", "AAPL", "foo_type", 42, 100)
        assert False
    except ValueError:
        assert True


@pytest.mark.asyncio
async def test_cancel_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42
    PRICE = 42.00

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    # Add an order
    o = await broker.submit_order(tid, SYMBOL, "buy", QUANTITY, PRICE)

    await exchange._book_queues[SYMBOL].join()
    # Check the prequisites
    assert exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    await broker.cancel_order(o.order_id)
    await exchange._book_queues[SYMBOL].join()

    assert exchange.order_lookup[o.order_id].status == "cancelled"

    assert exchange.order_books[SYMBOL].buy_size() == 0


@pytest.mark.asyncio
async def test_cancel_order_invalid_id(test_context: AppContext):
    sample_exchange = test_context.exchange

    try:
        await sample_exchange.cancel_order("fake_order_id")
    except KeyError:
        assert True
        return

    # Assert false if error not returned
    assert False


@pytest.mark.asyncio
async def test_cancel_fulfilled_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42
    PRICE = 42.00

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    # Add an order
    o = await broker.submit_order(tid, SYMBOL, "buy", QUANTITY, PRICE)
    await exchange._book_queues[SYMBOL].join()

    # Mutate order's status to fulfilled
    exchange.order_lookup[o.order_id].status = "filled"

    # Check the prequisites
    assert exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    assert not await exchange.cancel_order(o.order_id)
