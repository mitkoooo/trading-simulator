import pytest
from cli.validation import validate_symbol, parse_order


def test_parse_order_valid():
    sym, q, p = parse_order(["AAPL", "10", "150"])
    assert sym == "AAPL" and q == 10 and p == 150.0


def test_parse_order_invalid_qty_price():
    sym, q, p = parse_order(["MTKO", "MTKO", "MTKO"])
    assert sym == "MTKO" and q == None and p == None


def test_parse_order_invalid_args_num():
    sym, q, p = parse_order(["AAPL", "10", "150", "42"])
    assert sym == None and q == None and p == None
