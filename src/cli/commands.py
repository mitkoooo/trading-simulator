from cli.validation import parse_order, validate_symbol
from view.render import display_prices, display_portfolio, display_pending_orders
from engine.exchange import Exchange
from engine.trader import Trader
import logging
from logging_config import LOG_NAME

from typing import List

logger = logging.getLogger(LOG_NAME)


def handle_order(exchange: Exchange, trader: Trader, order_type: str, args: list[str]):
    symbol, quantity, price = parse_order(args)

    if not quantity or not price or not symbol:
        print("Usage: buy|sell SYMBOL QTY PRICE")
        logger.warning(
            "%s command usage error: args=%r — %s",
            order_type.upper(),
            args,
            "bad quantity or price",
        )
        return

    if validate_symbol(symbol, exchange, order_type.upper(), args) == False:
        return

    o = trader.place_order(
        symbol=symbol, order_type=order_type, quantity=quantity, price=price
    )
    exchange.add_order(o)
    print(f"\nOrder placed for {symbol}.")
    display_portfolio(trader)


def log_command(fn):
    def wrapper(*args, **kwargs):
        cmd = fn.__name__.replace("do_", "").upper()

        logger.info("%s command received: args=%r", cmd, args or kwargs)
        result = fn(*args, **kwargs)
        logger.info("%s command processed", cmd)
        return result

    return wrapper


@log_command
def do_next(exchange: Exchange, trader: Trader):
    exchange.process_tick()
    display_prices(exchange)
    display_portfolio(trader)


@log_command
def do_place_order(
    exchange: Exchange, trader: Trader, order_type: str, args: List[str]
):

    symbol, qty, price = parse_order(args)

    handle_order(exchange, trader, order_type, args)

    # only log if parsing succeeded
    if None not in (symbol, qty, price):
        logger.info(
            "%s order queued: symbol=%s, qty=%d, price=%.2f",
            order_type.upper(),
            symbol,
            qty,
            price,
        )


@log_command
def do_match(exchange: Exchange, args: List[str]):
    if not args or len(args) != 1:
        print("Usage: match SYMBOL")
        logger.warning(
            "%s command usage error: args=%r — %s",
            "MATCH",
            args,
            "bad symbol",
        )
        return

    symbol = args[0]

    if validate_symbol(symbol, exchange, "MATCH", args) == False:
        return

    trades = exchange.match_orders(symbol)

    if not trades:
        print("\nNo trades yet")
    else:
        for t in trades:
            print(f"TRADE: {t.symbol} {t.quantity} @ ${t.price:.2f}")


@log_command
def do_status(exchange: Exchange, trader: Trader):
    pending = sum(
        len(book.buy_heap) + len(book.sell_heap)
        for book in exchange.order_books.values()
    )
    if pending > 0:
        display_pending_orders(exchange)
    else:
        print("\nCurrently there are no pending orders on the exchange.")

    display_portfolio(trader)

    logger.info("STATUS viewed: %d pending orders", pending)


def log_quit():
    print("\nThank you for using York Stock Exchange.")
    logger.info("York Stock Exchange CLI shutting down")


COMMANDS = {
    "next": lambda args=None: do_next(),
    "buy": lambda args=[]: do_place_order("buy", args),
    "sell": lambda args=[]: do_place_order("sell", args),
    "match": lambda args=[]: do_match(args),
    "status": lambda args=None: do_status(),
}
