from cli.validation import parse_order


def test_parse_order_valid():
    q_expected = 10 
    p_expected = 150.0
    sym, q, p = parse_order(["AAPL", "10", "150"])
    assert sym == "AAPL" and q == q_expected and p == p_expected


def test_parse_order_invalid_qty_price():
    sym, q, p = parse_order(["MTKO", "MTKO", "MTKO"])
    assert sym == "MTKO" and q is None and p is None


def test_parse_order_invalid_args_num():
    sym, q, p = parse_order(["AAPL", "10", "150", "42"])
    assert sym is None and q is None and p is None
