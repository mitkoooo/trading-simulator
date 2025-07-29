import logging
from typing import List, Tuple

from config.logging_config import LOG_NAME
from engine.exchange.exchange import Exchange

logger = logging.getLogger(LOG_NAME)


def parse_order(args: List[str]) -> Tuple[str, int, float]:
    """Parse a list of CLI args into (symbol, qty, price).

    Args:
        args (List[str]): [symbol, qty, price] as strings.

    Returns:
        A tuple (symbol, quantity, price), where quantity and price
        are typed, or (symbol, None, None) if parsing fails.

    Examples:
        >>> parse_order(["AAPL","10","150"])
        ('AAPL', 10, 150.0)
        >>> parse_order(["AAPL","foo","150"])
        ('AAPL', None, None)

    """
    if args is None or len(args) != 3:
        return None, None, None

    symbol, quantity, price = args

    try:
        return symbol, int(quantity), float(price)
    except ValueError:
        return symbol, None, None


def validate_symbol(
    symbol: str, exchange: Exchange, cmd: str, args: List[str]
) -> bool:
    """Check that SYMBOL exists in exchange.market_data, else print and log warning.

    Args:
        symbol (str): ticket to validate
        exchange (Exchange): the Exchange instance
        cmd (str): the CLI command name (e.g. "BUY")
        args (List[str]): raw argv list

    Returns:
        True if valid, False (after printing usage) otherwise.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.stock import Stock
        >>> ex = Exchange(market_data={"AAPL": Stock("AAPL", 1.0)})
        >>> validate_symbol("AAPL", ex, "BUY", ["AAPL","1","1"])
        True
        >>> validate_symbol("FOO", ex, "BUY", ["FOO","1","1"])  # doctest: +SKIP
        False

    """
    if symbol not in exchange.instruments:
        valid = ", ".join(sorted(exchange.instruments.keys()))

        print(f"Unknown symbol. Please enter one of: {valid}")

        logger.warning(
            "%s command usage error: args=%r — unknown symbol", cmd, args
        )
        return False
    else:
        return True
