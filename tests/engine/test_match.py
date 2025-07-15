import random
from datetime import timedelta
from typing import List

from app.context import AppContext
from engine.trader import Trader
from engine.position import Position
from engine.trade import Trade

def test_match_exact_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"
    
    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    o1 = sample_trader.create_order(SYMBOL, "sell", 10, 100)
    sample_broker.submit_order(o1)

    o2 = sample_trader2.create_order(SYMBOL, "buy", 10, 100)
    sample_broker.submit_order(o2)

    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 1
    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 0
    )


def test_match_partial_fill(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 10
    qty_buy = 42

    o1 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 100)
    sample_broker.submit_order(o1)
    o2 = sample_trader2.create_order(SYMBOL, "buy", qty_buy, 100)
    sample_broker.submit_order(o2)

    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 1
    assert sample_exchange.order_books[SYMBOL].peek_best_buy().quantity == (
        qty_buy - qty_sell
    )
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1
    assert sample_exchange.order_books[SYMBOL].sell_size() == 0


def test_match_multistep_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    o1 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 100)
    sample_broker.submit_order(o1)
    o2 = sample_trader2.create_order(SYMBOL, "buy", qty_buy, 100)
    sample_broker.submit_order(o2)

    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 1
    assert sample_exchange.order_books[SYMBOL].buy_size() == 1
    assert sample_exchange.order_books[SYMBOL].peek_best_buy().quantity == (
        qty_buy - qty_sell
    )
    assert sample_exchange.order_books[SYMBOL].sell_size() == 0

    o3 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 100)
    sample_broker.submit_order(o3)


    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 1
    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 0
    )


def test_match_no_match(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 10

    o1 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 120)
    sample_broker.submit_order(o1)
    o2 = sample_trader2.create_order(SYMBOL, "buy", qty_buy, 100)
    sample_broker.submit_order(o2)

    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 0
    assert (
        sample_exchange.order_books[SYMBOL].buy_size()
        == sample_exchange.order_books[SYMBOL].sell_size()
        == 1
    )


def test_match_price_time(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    qty_sell = 5
    qty_buy = 5

    o1 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 100)
    sample_broker.submit_order(o1)

    o2 = sample_trader2.create_order(SYMBOL, "buy", qty_buy, 100)
    sample_broker.submit_order(o2)

    o3 = sample_trader.create_order(SYMBOL, "sell", qty_sell, 100)
    o3.timestamp = o1.timestamp + timedelta(days=1)
    sample_broker.submit_order(o3)


    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)
        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    # Only one trade (5 shares) should occur, matching o1 (earlier) first
    assert len(trades) == 1

    # After matching, buy side is empty; one sell (o3) remains
    assert sample_exchange.order_books[SYMBOL].buy_size() == 0
    assert sample_exchange.order_books[SYMBOL].sell_size() == 1
    assert sample_exchange.order_books[SYMBOL].peek_best_sell() is o3

def test_match_market_price_buy(test_context: AppContext, sample_trader2: Trader):
    SYMBOL = "AAPL"

    sample_trader = test_context.session.active_trader
    assert sample_trader

    sample_broker = test_context.broker
    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=10)

    exec_qty = 5

    o1 = sample_trader.create_order(SYMBOL, "sell", exec_qty, 100)
    sample_broker.submit_order(o1)

    o2 = sample_trader2.create_order(SYMBOL, "buy", exec_qty)
    sample_broker.submit_order(o2)

    trades: List[Trade] = []

    while True:
        trade = sample_exchange.match_orders(SYMBOL)

        if not trade:
            break
        sample_broker.settle_trade(trade)
        trades.append(trade)

    assert len(trades) == 1 
    assert trades[0].price == 100

def test_market_price_fail_benchmark(test_context: AppContext, sample_trader2):
    pass

