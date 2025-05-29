import pytest
from cli.commands import validate_symbol
import logging


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
