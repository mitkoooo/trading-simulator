import pytest

from engine.order_book.order import Order
from app.context import AppContext


def test_order_constructor_invalid_qty():
    try:
        _ = Order(mpid="1", symbol="AAPL", order_type="sell", quantity=-42)
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_price():
    try:
        _ = Order(
            mpid="1", symbol="AAPL", order_type="sell", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True


def test_order_constructor_invalid_order_type():
    try:
        _ = Order(
            mpid="1", symbol="AAPL", order_type="foo", quantity=42, limit_price=-100
        )
        assert False
    except ValueError:
        assert True

@pytest.mark.asyncio
async def test_cancel_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42 
    PRICE = 42.00

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker 
    sample_exchange = test_context.exchange

    # Add an order
    o = await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "buy", QUANTITY, PRICE)

    await sample_exchange._book_queues[SYMBOL].join()
    # Check the prequisites
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    await sample_broker.cancel_order(o.order_id)
    await sample_exchange._book_queues[SYMBOL].join()

    assert sample_exchange.order_lookup[o.order_id].status == "cancelled"

    assert sample_exchange.order_books[SYMBOL].buy_size() == 0

@pytest.mark.asyncio
async def test_cancel_order_invalid_id(test_context: AppContext):
    sample_exchange = test_context.exchange

    try:
        await sample_exchange.cancel_order("fake_order_id")
    except Exception as e:
        assert type(e) == KeyError
        return

    # Assert false if error not returned
    assert False    

@pytest.mark.asyncio
async def test_cancel_fulfilled_order(test_context: AppContext):
    SYMBOL = "AAPL"
    QUANTITY = 42 
    PRICE = 42.00

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker 
    sample_exchange = test_context.exchange

    # Add an order
    o = await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "buy", QUANTITY, PRICE)
    await sample_exchange._book_queues[SYMBOL].join()


    # Mutate order's status to fulfilled 
    sample_exchange.order_lookup[o.order_id].status = "filled"

    # Check the prequisites
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1

    # Cancel an order
    assert not await sample_exchange.cancel_order(o.order_id)





