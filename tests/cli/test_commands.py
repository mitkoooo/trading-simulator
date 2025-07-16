import logging

from cli.commands import (
    validate_symbol,
    handle_order,
    do_next,
    do_place_order,
    do_match,
)

from app.context import AppContext
from engine.order_book.order import Order

def test_validate_symbol_known(test_context: AppContext, caplog):
    test_logger = test_context.logger
    sample_exchange = test_context.exchange

    caplog.set_level(logging.WARNING, logger=test_logger.name)


    ok = validate_symbol("AAPL", sample_exchange, "BUY", ["AAPL", "1", "100"])
    assert ok
    assert "usage error" not in caplog.text

def test_validate_symbol_unknown(test_context: AppContext, caplog):
    test_logger = test_context.logger
    sample_exchange = test_context.exchange

    caplog.set_level(logging.WARNING, logger=test_logger.name)

    ok = validate_symbol("MTKO", sample_exchange, "BUY", ["MTKO", "1", "100"])
    assert not ok
    assert "BUY command usage error" in caplog.text


def test_handle_order_invalid_args_num(test_context: AppContext, caplog):
    test_logger = test_context.logger
    sample_exchange = test_context.exchange
    sample_trader = test_context.session.active_trader

    caplog.set_level(logging.WARNING, logger=test_logger.name)

    o = Order(trader_id=sample_trader.trader_id, symbol="AAPL", order_type="buy", quantity=42)

    handle_order(
        test_context,
        order_type=o.order_type,
        args=["AAPL", "42"],
    )

    assert "BUY command usage error" in caplog.text
    assert sample_exchange.order_books["AAPL"].buy_size() == 0


def test_handle_order_adds_order(test_context: AppContext):

    sample_trader = test_context.session.active_trader 

    o = Order(
        trader_id=sample_trader.trader_id,
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

    assert test_context.exchange.order_books["AAPL"].buy_size() == 1


def test_do_next_updates_prices(test_context: AppContext):
    sample_exchange = test_context.exchange
    old_p = 100.0
    do_next(test_context)
    assert sample_exchange.market_data.get("AAPL").price != old_p


def test_do_next_updates_time(test_context: AppContext):
    sample_exchange = test_context.exchange

    old_time = test_context.exchange.current_time
    do_next(test_context)
    assert sample_exchange.current_time != old_time


def test_do_place_order_places_order(test_context: AppContext):
    sample_exchange = test_context.exchange

    do_place_order(test_context, "buy", ["AAPL", "1", "100"])

    assert sample_exchange.order_books.get("AAPL").buy_size() == 1
    assert sample_exchange.order_books.get("AAPL").peek_best_buy().quantity == 1
    assert sample_exchange.order_books.get("AAPL").peek_best_buy().limit_price == 100.00


def test_do_match_invalid_args_num(test_context: AppContext, caplog):
    test_logger = test_context.logger

    caplog.set_level(logging.WARNING, logger=test_logger.name)

    do_match(test_context, [])

    assert "MATCH command usage error" in caplog.text
