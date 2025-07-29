import logging

import pytest

from app.context import AppContext
from cli.commands import (
    do_match,
    do_place_order,
    handle_order,
    validate_symbol,
)
from engine.exchange.exchange import Exchange
from engine.order_book.order import Order


def test_validate_symbol_known(sample_exchange: Exchange):
    ok = validate_symbol("AAPL", sample_exchange, "BUY", ["AAPL", "1", "100"])
    assert ok


def test_validate_symbol_unknown(sample_exchange: Exchange):
    ok = validate_symbol("MTKO", sample_exchange, "BUY", ["MTKO", "1", "100"])
    assert not ok


@pytest.mark.asyncio
async def test_handle_order_invalid_args_num(test_context: AppContext, caplog):
    test_logger = test_context.logger
    assert test_logger
    exchange = test_context.exchange

    trader = test_context.session.active_trader
    assert trader
    tid = trader.trader_id

    caplog.set_level(logging.WARNING, logger=test_logger.name)

    o = Order(tid, symbol="AAPL", order_type="buy", quantity=42)

    await handle_order(
        test_context,
        order_type=o.order_type,
        args=["AAPL", "42"],
    )

    await test_context.exchange._book_queues["AAPL"].join()
    assert "BUY command usage error" in caplog.text
    assert exchange.order_books["AAPL"].buy_size() == 0


@pytest.mark.asyncio
async def test_handle_order_adds_order(test_context: AppContext):
    sample_trader = test_context.session.active_trader
    assert sample_trader

    o = Order(
        mpid=sample_trader.trader_id,
        symbol="AAPL",
        order_type="buy",
        quantity=42,
        limit_price=100.00,
    )

    await handle_order(
        test_context,
        order_type=o.order_type,
        args=["AAPL", "42", "100.00"],
    )

    await test_context.exchange._book_queues["AAPL"].join()
    assert test_context.exchange.order_books["AAPL"].buy_size() == 1


@pytest.mark.asyncio
async def test_do_place_order_places_order(test_context: AppContext):
    sample_exchange = test_context.exchange

    await do_place_order(test_context, "buy", ["AAPL", "1", "100"])

    await test_context.exchange._book_queues["AAPL"].join()
    order_book = sample_exchange.order_books.get("AAPL")
    assert order_book
    best_buy = order_book.peek_best_buy()
    assert best_buy

    assert order_book.buy_size() == 1
    assert best_buy.quantity == 1
    assert best_buy.limit_price == 100.00


@pytest.mark.asyncio
async def test_do_match_invalid_args_num(test_context: AppContext, caplog):
    test_logger = test_context.logger
    assert test_logger

    caplog.set_level(logging.WARNING, logger=test_logger.name)

    do_match(test_context, [])

    assert "MATCH command usage error" in caplog.text
