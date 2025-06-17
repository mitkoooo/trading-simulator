import logging

from cli.commands import (
    validate_symbol,
    handle_order,
    do_next,
    do_place_order,
    do_match,
    do_status,
)

from app.context import AppContext
from app.session import Session

from engine.exchange import Exchange
from engine.order import Order
from engine.trader import Trader
from engine.stock import Stock


def test_validate_symbol_known(sample_market, caplog):
    caplog.set_level(logging.WARNING)

    ok = validate_symbol("AAPL", sample_market, "BUY", ["AAPL", "1", "100"])
    assert ok
    assert "usage error" not in caplog.text


def test_validate_symbol_unknown(sample_market, caplog):
    caplog.set_level(logging.WARNING)

    ok = validate_symbol("MTKO", sample_market, "BUY", ["MTKO", "1", "100"])
    assert not ok
    assert "BUY command usage error" in caplog.text


def test_handle_order_invalid_args_num(
    sample_market: Exchange, caplog, trader: Trader, test_context: AppContext
):
    caplog.set_level(logging.WARNING)

    session = Session(sample_market.traders)
    session.login(trader.trader_id)

    o = Order(trader_id=trader.trader_id, symbol="AAPL", order_type="buy", quantity=42)

    handle_order(
        test_context,
        order_type=o.order_type,
        args=["AAPL", "42"],
    )

    assert "BUY command usage error" in caplog.text
    assert len(sample_market.order_books["AAPL"]._buy_heap) == 0


def test_handle_order_adds_order(test_context: AppContext, trader: Trader):

    o = Order(
        trader_id=trader.trader_id,
        symbol="AAPL",
        order_type="buy",
        quantity=42,
        limit_price=100.00,
    )

    handle_order(
        test_context,
        order_type=o.order_type,
        args=["AAPL", "42", "100.00"],
    )

    assert len(test_context.exchange.order_books["AAPL"]._buy_heap) == 1


def test_do_next_updates_prices(test_context: AppContext):
    ex = test_context.exchange
    old_p = 100.0
    do_next(test_context)
    assert ex.market_data.get("AAPL").price != old_p


def test_do_next_updates_time(test_context: AppContext):
    ex = test_context.exchange

    old_time = test_context.exchange.current_time
    do_next(test_context)
    assert ex.current_time != old_time


def test_do_place_order_places_order(test_context: AppContext, trader: Trader):
    ex = test_context.exchange

    do_place_order(test_context, "buy", ["AAPL", "1", "100"])

    assert ex.order_books.get("AAPL").buy_size() == 1
    assert ex.order_books.get("AAPL").peek_best_buy().quantity == 1
    assert ex.order_books.get("AAPL").peek_best_buy().limit_price == 100.00


def test_do_match_invalid_args_num(test_context: AppContext, caplog):

    caplog.set_level(logging.WARNING)

    do_match(test_context, [])

    assert "MATCH command usage error" in caplog.text
