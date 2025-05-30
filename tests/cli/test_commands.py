import pytest
import logging

from cli.commands import validate_symbol, handle_order, do_next

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


def test_handle_order_invalid_args_num(sample_market: Exchange, caplog):
    caplog.set_level(logging.WARNING)

    t = Trader(trader_id=1, cash_balance=100_000_000)

    o = Order(trader_id=t.trader_id, symbol="AAPL", order_type="buy", quantity=42)

    handle_order(
        exchange=sample_market,
        trader=t,
        order_type=o.order_type,
        args=["AAPL", "42"],
    )

    assert "BUY command usage error" in caplog.text
    assert len(sample_market.order_books["AAPL"].buy_heap) == 0


def test_handle_order_adds_order(sample_market: Exchange):
    t = Trader(trader_id=1, cash_balance=100_000_000)

    o = Order(
        trader_id=t.trader_id,
        symbol="AAPL",
        order_type="buy",
        quantity=42,
        limit_price=100.00,
    )

    handle_order(
        exchange=sample_market,
        trader=t,
        order_type=o.order_type,
        args=["AAPL", "42", "100.00"],
    )

    assert len(sample_market.order_books["AAPL"].buy_heap) == 1


def test_do_next_updates_prices(sample_market: Exchange):
    old_p = 100.0
    t = Trader(1, 1000.0)
    do_next(sample_market, t)
    assert sample_market.market_data.get("AAPL").price != old_p


def test_do_next_updates_time(sample_market: Exchange):
    old_time = sample_market.current_time
    t = Trader(1, 1000.0)
    do_next(sample_market, t)
    assert sample_market.current_time != old_time
