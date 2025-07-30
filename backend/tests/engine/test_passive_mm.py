from datetime import datetime

from engine.bots.passive_mm.passive_mm import PassiveMM
from engine.exchange.exchange import Exchange
from engine.market_data.quote import MarketQuote
from engine.order_book.order import Order
from engine.trade import Trade


def test_risk_breached_position(sample_exchange: Exchange):
    symbol = "AAPL"

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")
    passive_mm.inv_manager.inv_limit = 1000
    passive_mm.inv_manager.position = 1001

    assert passive_mm.inv_manager.risk_breached()


def test_risk_breached_pnl_limit(sample_exchange: Exchange):
    symbol = "AAPL"

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")
    passive_mm.inv_manager.pnl_limit = 1000
    passive_mm.inv_manager.realized_pnl = -1001

    assert passive_mm.inv_manager.risk_breached()


def test_update_inventory_on_trade_buy_order(sample_exchange: Exchange):
    symbol = "AAPL"
    trade_qty = 10
    trade_price = 100

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    order1 = Order("MM_TEST", symbol, "buy", 1, trade_price)
    order2 = Order("BR_TEST", symbol, "sell", 1, trade_price)
    trade = Trade(order1, order2, symbol, trade_qty, trade_price)

    sample_exchange.emit_trade(trade)

    assert passive_mm.inv_manager.position == trade_qty
    assert passive_mm.inv_manager.realized_pnl == -trade_qty * trade_price


def test_update_inventory_on_trade_sell_order(sample_exchange: Exchange):
    symbol = "AAPL"
    trade_qty = 10
    trade_price = 100

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    order1 = Order("BR_TEST", symbol, "buy", 1, trade_price)
    order2 = Order("MM_TEST", symbol, "sell", 1, trade_price)
    trade = Trade(order1, order2, symbol, trade_qty, trade_price)

    sample_exchange.emit_trade(trade)

    assert passive_mm.inv_manager.position == -trade_qty
    assert passive_mm.inv_manager.realized_pnl == trade_qty * trade_price


def test_get_mid_history(sample_exchange: Exchange):
    symbol = "AAPL"
    ts = datetime.now()

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    assert passive_mm.data_handler.get_mid_history() == []

    mq = MarketQuote(
        symbol,
        bid_price=None,
        bid_size=1,
        ask_price=None,
        ask_size=1,
        last_price=100,
        timestamp=ts,
    )

    passive_mm.data_handler.on_book_update(mq)

    assert passive_mm.data_handler.get_mid_history()


def test_on_book_update_mid_on_no_quote(sample_exchange: Exchange):
    symbol = "AAPL"
    ts = datetime.now()

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    mq = MarketQuote(
        symbol,
        bid_price=None,
        bid_size=1,
        ask_price=None,
        ask_size=1,
        last_price=None,
        timestamp=ts,
    )

    passive_mm.data_handler.on_book_update(mq)

    assert len(passive_mm.data_handler.get_mid_history()) == 0


def test_on_book_update_mid_on_quote_empty(sample_exchange: Exchange):
    symbol = "AAPL"
    ts = datetime.now()

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    mq = MarketQuote(
        symbol,
        bid_price=None,
        bid_size=0,
        ask_price=None,
        ask_size=0,
        last_price=None,
        timestamp=ts,
    )

    passive_mm.data_handler.on_book_update(mq)

    assert len(passive_mm.data_handler.get_mid_history()) == 0


def test_on_book_update_mid_on_quote(sample_exchange: Exchange):
    symbol = "AAPL"
    ts = datetime.now()
    expected = 100

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    mq = MarketQuote(
        symbol,
        bid_price=101,
        bid_size=1,
        ask_price=99,
        ask_size=1,
        last_price=None,
        timestamp=ts,
    )

    passive_mm.data_handler.on_book_update(mq)

    assert len(passive_mm.data_handler.get_mid_history()) == 1
    assert passive_mm.data_handler.get_mid_history()[0] == expected


def test_compute_quote(sample_exchange: Exchange):
    symbol = "AAPL"
    mid = (101 + 99) / 2  # 100
    vol = 2.0
    depth_imb = 10
    inventory = 100

    passive_mm = PassiveMM(sample_exchange, symbol, "MM_TEST")

    qe = passive_mm.quote_engine

    bid_price, ask_price = passive_mm.quote_engine.compute(
        mid, vol, depth_imb, inventory
    )

    assert bid_price and ask_price

    s0 = qe.alpha * vol
    s = s0 * (1 + qe.gamma * abs(depth_imb))
    skew = qe.beta * inventory * mid

    half_spread = s / 2
    bid = round(mid - half_spread - skew, 2)
    ask = round(mid + half_spread - skew, 2)

    assert bid_price == bid and ask_price == ask
