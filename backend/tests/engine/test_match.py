import pytest

from app.context import AppContext

from engine.trader import Trader
from engine.position import Position


@pytest.mark.asyncio
async def test_match_exact_match(test_context: AppContext,
                                 sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    await broker.submit_order(tid1, SYMBOL, "sell", 10, 100)
    await broker.submit_order(tid2, SYMBOL, "buy", 10, 100)
    await exchange._book_queues[SYMBOL].join()

    assert (
        exchange.order_books[SYMBOL].buy_size()
        == exchange.order_books[SYMBOL].sell_size()
        == 0
    )


@pytest.mark.asyncio
async def test_match_partial_fill(test_context: AppContext,
                                  sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 10
    qty_buy = 42

    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 100)
    await broker.submit_order(tid2, SYMBOL, "buy", qty_buy, 100)

    await exchange._book_queues[SYMBOL].join()

    best_buy = exchange.order_books[SYMBOL].peek_best_buy()
    assert best_buy

    assert best_buy.quantity == qty_buy - qty_sell
    assert exchange.order_books[SYMBOL].buy_size() == 1
    assert exchange.order_books[SYMBOL].sell_size() == 0


@pytest.mark.asyncio
async def test_match_multistep_match(test_context: AppContext,
                                     sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 100)
    await broker.submit_order(tid2, SYMBOL, "buy", qty_buy, 100)
    await test_context.exchange._book_queues[SYMBOL].join()

    best_buy = exchange.order_books[SYMBOL].peek_best_buy()
    assert best_buy

    assert exchange.order_books[SYMBOL].buy_size() == 1
    assert best_buy.quantity == (
        qty_buy - qty_sell
    )
    assert exchange.order_books[SYMBOL].sell_size() == 0

    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    assert (
        exchange.order_books[SYMBOL].buy_size()
        == exchange.order_books[SYMBOL].sell_size()
        == 0
    )


@pytest.mark.asyncio
async def test_match_no_match(test_context: AppContext,
                              sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 120)
    await broker.submit_order(tid2, SYMBOL, "buy", qty_buy, 100)
    await exchange._book_queues["AAPL"].join()

    assert (
        exchange.order_books[SYMBOL].buy_size()
        == exchange.order_books[SYMBOL].sell_size()
        == 1
    )


@pytest.mark.asyncio
async def test_match_price_time(test_context: AppContext,
                                sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 5

    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 100)
    await broker.submit_order(tid2, SYMBOL, "buy", qty_buy, 100)
    await broker.submit_order(tid1, SYMBOL, "sell", qty_sell, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    assert exchange.order_books[SYMBOL].buy_size() == 0
    assert exchange.order_books[SYMBOL].sell_size() == 1


@pytest.mark.asyncio
async def test_match_market_price_buy(test_context: AppContext,
                                      sample_trader2: Trader):
    SYMBOL = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=999)

    exec_qty = 5

    await broker.submit_order(tid1, SYMBOL, "sell", exec_qty, 100)
    await exchange._book_queues["AAPL"].join()

    await broker.submit_order(tid2, SYMBOL, "buy", exec_qty, limit_price=None)
    await test_context.exchange._book_queues["AAPL"].join()

    assert test_context.exchange.order_books[SYMBOL].buy_size() == 0
    assert test_context.exchange.order_books[SYMBOL].sell_size() == 0


def test_market_price_fail_benchmark(test_context: AppContext, sample_trader2):
    pass
