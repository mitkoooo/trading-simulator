from engine.exchange import Exchange
from engine.trader import Trader

from typing import List, Tuple
import logging
from logging_config import LOG_NAME

logger = logging.getLogger(LOG_NAME)


def parse_order(args: List[str]) -> Tuple[str, int, float]:
    if len(args) != 3:
        return None, None, None

    symbol, quantity, price = args

    try:
        return symbol, int(quantity), float(price)
    except ValueError:
        return symbol, None, None


def validate_symbol(symbol: str, exchange: Exchange, cmd: str, args: List[str]) -> bool:
    if symbol not in exchange.market_data:
        valid = ", ".join(sorted(exchange.market_data.keys()))

        print(f"Unknown symbol. Please enter one of: {valid}")

        logger.warning("%s command usage error: args=%r — unknown symbol", cmd, args)
        return False
    else:
        return True
