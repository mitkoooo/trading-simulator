import pytest

from app.context import AppContext
from engine.position import Position
from engine.trader import Trader


@pytest.mark.asyncio
async def test_match_exact_match(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=10)

    await broker.submit_order(tid1, symbol, "sell", 10, 100)
    await broker.submit_order(tid2, symbol, "buy", 10, 100)
    await exchange._book_queues[symbol].join()

    assert (
        exchange.order_books[symbol].buy_size()
        == exchange.order_books[symbol].sell_size()
        == 0
    )


@pytest.mark.asyncio
async def test_match_partial_fill(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=10)

    qty_sell = 10
    qty_buy = 42

    await broker.submit_order(tid1, symbol, "sell", qty_sell, 100)
    await broker.submit_order(tid2, symbol, "buy", qty_buy, 100)

    await exchange._book_queues[symbol].join()

    best_buy = exchange.order_books[symbol].peek_best_buy()
    assert best_buy

    assert best_buy.quantity == qty_buy - qty_sell
    assert exchange.order_books[symbol].buy_size() == 1
    assert exchange.order_books[symbol].sell_size() == 0


@pytest.mark.asyncio
async def test_match_multistep_match(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=10)

    qty_sell = 5
    qty_buy = 10

    await broker.submit_order(tid1, symbol, "sell", qty_sell, 100)
    await broker.submit_order(tid2, symbol, "buy", qty_buy, 100)
    await test_context.exchange._book_queues[symbol].join()

    best_buy = exchange.order_books[symbol].peek_best_buy()
    assert best_buy

    assert exchange.order_books[symbol].buy_size() == 1
    assert best_buy.quantity == (qty_buy - qty_sell)
    assert exchange.order_books[symbol].sell_size() == 0

    await broker.submit_order(tid1, symbol, "sell", qty_sell, 100)
    await test_context.exchange._book_queues[symbol].join()

    assert (
        exchange.order_books[symbol].buy_size()
        == exchange.order_books[symbol].sell_size()
        == 0
    )


@pytest.mark.asyncio
async def test_match_no_match(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=10)

    qty_sell = 5
    qty_buy = 10

    await broker.submit_order(tid1, symbol, "sell", qty_sell, 120)
    await broker.submit_order(tid2, symbol, "buy", qty_buy, 100)
    await exchange._book_queues[symbol].join()

    assert (
        exchange.order_books[symbol].buy_size()
        == exchange.order_books[symbol].sell_size()
        == 1
    )


@pytest.mark.asyncio
async def test_match_price_time(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=10)

    qty_sell = 5
    qty_buy = 5

    await broker.submit_order(tid1, symbol, "sell", qty_sell, 100)
    await broker.submit_order(tid2, symbol, "buy", qty_buy, 100)
    await broker.submit_order(tid1, symbol, "sell", qty_sell, 100)
    await test_context.exchange._book_queues[symbol].join()

    assert exchange.order_books[symbol].buy_size() == 0
    assert exchange.order_books[symbol].sell_size() == 1


@pytest.mark.asyncio
async def test_match_market_price_buy(
    test_context: AppContext, sample_trader2: Trader
):
    symbol = "AAPL"

    trader1 = test_context.session.active_trader
    assert trader1
    tid1 = trader1.trader_id

    trader2 = sample_trader2
    tid2 = trader2.trader_id

    broker = test_context.broker
    exchange = test_context.exchange

    trader1.portfolio.positions[symbol] = Position(symbol=symbol, qty=999)

    exec_qty = 5

    await broker.submit_order(tid1, symbol, "sell", exec_qty, 100)
    await exchange._book_queues["AAPL"].join()

    await broker.submit_order(tid2, symbol, "buy", exec_qty, limit_price=None)
    await test_context.exchange._book_queues["AAPL"].join()

    assert test_context.exchange.order_books[symbol].buy_size() == 0
    assert test_context.exchange.order_books[symbol].sell_size() == 0


def test_market_price_fail_benchmark(test_context: AppContext,
                                     sample_trader2: Trader):
    pass
