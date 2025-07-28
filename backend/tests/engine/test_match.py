import pytest
from typing import List

from app.context import AppContext
from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange
from engine.trader import Trader
from engine.position import Position

@pytest.mark.asyncio
async def test_match_exact_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"
    
    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", 10, 100)

    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", 10, 100)

    await test_context.exchange._book_queues["AAPL"].join()

    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 0
    )

@pytest.mark.asyncio
async def test_match_partial_fill(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 10
    qty_buy = 42

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 100)
    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", qty_buy, 100)

    await test_context.exchange._book_queues["AAPL"].join()

    best_buy = sample_exchange.order_books[SYMBOL].peek_best_buy()
    assert best_buy

    assert best_buy.quantity == (
        qty_buy - qty_sell
    )
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1
    assert sample_exchange.order_books[SYMBOL].sell_size() == 0


@pytest.mark.asyncio
async def test_match_multistep_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 100)
    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", qty_buy, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    best_buy = sample_exchange.order_books[SYMBOL].peek_best_buy()
    assert best_buy

    assert sample_exchange.order_books[SYMBOL].buy_size() == 1
    assert best_buy.quantity == (
        qty_buy - qty_sell
    )
    assert sample_exchange.order_books[SYMBOL].sell_size() == 0

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 0
    )


@pytest.mark.asyncio
async def test_match_no_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 120)
    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", qty_buy, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 1
    )

@pytest.mark.asyncio
async def test_match_price_time(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 5

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 100)
    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", qty_buy, 100)
    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", qty_sell, 100)
    await test_context.exchange._book_queues["AAPL"].join()

    assert sample_exchange.order_books[SYMBOL].buy_size() == 0
    assert sample_exchange.order_books[SYMBOL].sell_size() == 1

@pytest.mark.asyncio
async def test_match_market_price_buy(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=999)

    exec_qty = 5

    await sample_broker.submit_order(sample_trader.trader_id, SYMBOL, "sell", exec_qty, 100)
    await sample_exchange._book_queues["AAPL"].join()

    await sample_broker.submit_order(sample_trader2.trader_id, SYMBOL, "buy", exec_qty, limit_price=None)
    await test_context.exchange._book_queues["AAPL"].join()
    
    assert test_context.exchange.order_books[SYMBOL].buy_size() == 0
    assert test_context.exchange.order_books[SYMBOL].sell_size() == 0



def test_market_price_fail_benchmark(test_context: AppContext, sample_trader2):
    pass


@pytest.mark.asyncio
async def test_sell_lower_than_buy_filled(sample_exchange: Exchange, sample_broker: Broker, sample_trader: Trader, sample_trader2: Trader):
    #SYMBOL = "AAPL"

    #buy_trader_id = sample_trader.trader_id
    #sell_trader_id = sample_trader2.trader_id

    #sample_trader2.portfolio.positions[SYMBOL] = Position(qty=10, avg_price=148)

    #await sample_broker.submit_order(buy_trader_id, SYMBOL, "buy", 10, 150)
    #await sample_broker.submit_order(sell_trader_id, SYMBOL, "sell", 10, 148)
    #await sample_exchange._book_queues["AAPL"].join()
    pass
    



    
