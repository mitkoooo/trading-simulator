from datetime import timedelta

from engine.trader import Trader
from engine.order import Order
from engine.exchange import Exchange
from engine.position import Position


def test_match_exact_match(sample_market: Exchange, trader: Trader, trader2: Trader):
    SYMBOL = "AAPL"
    trader.portfolio._positions[SYMBOL] = Position(qty=10, avg_price=150.0)

    o1, o2 = trader.place_order(SYMBOL, "sell", 10, 100), trader2.place_order(
        SYMBOL, "buy", 10, 100
    )

    sample_market.add_order(o1)
    sample_market.add_order(o2)

    trades = sample_market.match_orders(SYMBOL)
    assert len(trades) == 1
    assert (
        sample_market.order_books[SYMBOL].buy_size()
        == sample_market.order_books[SYMBOL].sell_size()
        == 0
    )


def test_match_partial_fill(sample_market: Exchange, trader: Trader, trader2: Trader):
    SYMBOL = "AAPL"
    trader.portfolio._positions[SYMBOL] = Position(qty=10)

    qty_sell = 10
    qty_buy = 42
    o1, o2 = trader.place_order(SYMBOL, "sell", qty_sell, 100), trader2.place_order(
        SYMBOL, "buy", qty_buy, 100
    )

    sample_market.add_order(o1)
    sample_market.add_order(o2)

    trades = sample_market.match_orders(SYMBOL)
    assert len(trades) == 1
    assert sample_market.order_books[SYMBOL].buy_size() == 1
    assert sample_market.order_books[SYMBOL].peek_best_buy().quantity == (
        qty_buy - qty_sell
    )
    assert sample_market.order_books[SYMBOL].sell_size() == 0


def test_match_multistep_match(
    sample_market: Exchange, trader: Trader, trader2: Trader
):
    SYMBOL = "AAPL"
    trader.portfolio._positions[SYMBOL] = Position(qty=10)

    qty_sell = 5
    qty_buy = 10
    o1, o2 = trader.place_order(SYMBOL, "sell", qty_sell, 100), trader2.place_order(
        SYMBOL, "buy", qty_buy, 100
    )

    sample_market.add_order(o1)
    sample_market.add_order(o2)

    trades = sample_market.match_orders(SYMBOL)

    assert len(trades) == 1
    assert sample_market.order_books[SYMBOL].buy_size() == 1
    assert sample_market.order_books[SYMBOL].peek_best_buy().quantity == (
        qty_buy - qty_sell
    )
    assert sample_market.order_books[SYMBOL].sell_size() == 0

    o3 = trader.place_order(SYMBOL, "sell", qty_sell, 100)

    sample_market.add_order(o3)

    trades = sample_market.match_orders(SYMBOL)

    assert len(trades) == 1
    assert (
        sample_market.order_books[SYMBOL].buy_size()
        == sample_market.order_books[SYMBOL].sell_size()
        == 0
    )


def test_match_no_match(sample_market: Exchange, trader: Trader, trader2: Trader):
    SYMBOL = "AAPL"
    trader.portfolio._positions[SYMBOL] = Position(qty=10)

    qty_sell = 5
    qty_buy = 10
    o1, o2 = trader.place_order(SYMBOL, "sell", qty_sell, 120), trader2.place_order(
        SYMBOL, "buy", qty_buy, 100
    )
    sample_market.add_order(o1)
    sample_market.add_order(o2)
    trades = sample_market.match_orders(SYMBOL)

    assert len(trades) == 0
    assert (
        sample_market.order_books[SYMBOL].buy_size()
        == sample_market.order_books[SYMBOL].sell_size()
        == 1
    )


def test_match_price_time(sample_market: Exchange, trader: Trader, trader2: Trader):
    SYMBOL = "AAPL"
    trader.portfolio._positions[SYMBOL] = Position(qty=10)

    qty_sell = 5
    qty_buy = 5
    o1 = trader.place_order(SYMBOL, "sell", qty_sell, 100)
    o2 = trader2.place_order(SYMBOL, "buy", qty_buy, 100)
    o3 = trader.place_order(SYMBOL, "sell", qty_sell, 100)

    o3.timestamp = o1.timestamp + timedelta(days=1)

    sample_market.add_order(o1)
    sample_market.add_order(o3)
    sample_market.add_order(o2)

    trades = sample_market.match_orders(SYMBOL)

    # Only one trade (5 shares) should occur, matching o1 (earlier) first
    assert len(trades) == 1

    # After matching, buy side is empty; one sell (o3) remains
    assert sample_market.order_books[SYMBOL].buy_size() == 0
    assert sample_market.order_books[SYMBOL].sell_size() == 1
    assert sample_market.order_books[SYMBOL].peek_best_sell() is o3
