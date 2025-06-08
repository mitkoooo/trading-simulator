from cli.validation import parse_order, validate_symbol
from view.render import display_prices, display_portfolio, display_pending_orders
from engine.exchange import Exchange
from engine.trader import Trader
import logging
from logging_config import LOG_NAME

from typing import List

logger = logging.getLogger(LOG_NAME)


def handle_order(exchange: Exchange, trader: Trader, order_type: str, args: list[str]):
    """
    Handle a buy or sell order: parse args, validate and enqueue the order, then show portfolio.

    Prints usage errors or order confirmation followed by the updated portfolio.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.trader import Trader
        >>> from engine.stock import Stock
        >>> ex = Exchange(market_data={"AAPL": Stock("AAPL", 100.0)})
        >>> tr = Trader(trader_id=1, starting_balance=1000.0)
        >>> handle_order(ex, tr, "buy", ["AAPL", "1", "100"]) # doctest: +SKIP
        Order placed for AAPL.
        Cash balance: $1000.0
        Holdings: {}
    """
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
    display_portfolio(exchange, trader)


def log_command(fn):
    """
    Decorator: log command invocation and completion at INFO level.

    Examples:
        >>> @log_command
        ... def my_func(x):
        ...     return x + 1
        >>> my_func(2)
        3
    """

    def wrapper(*args, **kwargs):
        cmd = fn.__name__.replace("do_", "").upper()

        logger.info("%s command received: args=%r", cmd, args or kwargs)
        result = fn(*args, **kwargs)
        logger.info("%s command processed", cmd)
        return result

    return wrapper


@log_command
def do_next(exchange: Exchange, trader: Trader):
    """
    Advance the market by one tick and display prices & portfolio.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.trader import Trader
        >>> from engine.stock import Stock
        >>> ex = Exchange({'AAPL': Stock('AAPL', 100.0)})
        >>> tr = Trader(1, 1000.0)
        >>> do_next(ex, tr) is None
        True
    """
    exchange.process_tick()
    display_prices(exchange)
    display_portfolio(exchange, trader)


@log_command
def do_place_order(
    exchange: Exchange, trader: Trader, order_type: str, args: List[str]
):
    """
    Enqueue a buy/sell order and log details if valid.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.trader import Trader
        >>> from engine.stock import Stock
        >>> ex = Exchange({'AAPL': Stock('AAPL', 100.0)})
        >>> tr = Trader(1, 1000.0)
        >>> do_place_order(ex, tr, 'sell', ['AAPL', '1', '100']) is None
        True
    """

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
    """
    Attempt to match orders for a given symbol and display results.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.stock import Stock
        >>> ex = Exchange({'AAPL': Stock('AAPL', 100.0)})
        >>> do_match(ex, ['AAPL'])
        No trades yet
    """
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
        print("\nNo trades yet\n")
    else:
        for t in trades:
            print(f"TRADE: {t.symbol} {t.quantity} @ ${t.price:.2f}")
            logger.info(
                "MATCH command status: trade symbol=%s processed @ qty=%d, price=%.2f",
                symbol,
                t.quantity,
                t.price,
            )


@log_command
def do_status(exchange: Exchange, trader: Trader):
    """
    Display pending orders and the trader's portfolio.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.trader import Trader
        >>> from engine.stock import Stock
        >>> ex = Exchange({'AAPL': Stock('AAPL', 100.0)})
        >>> tr = Trader(1, 1000.0)
        >>> do_status(ex, tr) # doctest: +NORMALIZE_WHITESPACE
        Currently there are no pending orders on the exchange.
        Cash balance: $1000.0
        Holdings: {}
    """
    pending = sum(
        len(book._buy_heap) + len(book._sell_heap)
        for book in exchange.order_books.values()
    )
    if pending > 0:
        display_pending_orders(exchange)
    else:
        print("\nCurrently there are no pending orders on the exchange.")

    display_portfolio(exchange, trader)

    logger.info("STATUS viewed: %d pending orders", pending)


def log_quit():
    """
    Print goodbye and log shutdown.

    Examples:
        >>> log_quit() # doctest: +NORMALIZE_WHITESPACE
        Thank you for using York Stock Exchange.
    """
    print("\nThank you for using York Stock Exchange.")
    logger.info("York Stock Exchange CLI shutting down")


COMMANDS = {
    "next": lambda args=None: do_next(),
    "buy": lambda args=[]: do_place_order("buy", args),
    "sell": lambda args=[]: do_place_order("sell", args),
    "match": lambda args=[]: do_match(args),
    "status": lambda args=None: do_status(),
}
