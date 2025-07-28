from typing import List, Literal, LiteralString

from app.context import AppContext

from cli.validation import parse_order, validate_symbol

from engine.trade import Trade
from cli.render import (
    display_prices,
    display_portfolio,
    display_pending_orders,
    display_help_menu,
)


async def handle_order(context: AppContext, order_type: Literal["buy", "sell"], args: list[str]):
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
    exchange, session, logger, broker = context.exchange, context.session, context.logger, context.broker

    try:
        trader = session.require_active()

    except:
        print("\nYou must log in to use this command. Please use login <trader_id>.\n")
        logger.warning(
            "%s command usage error: args=%r — %s",
            order_type.upper(),
            args,
            "user not logged in",
        )
        return

    symbol, quantity, price = parse_order(args)

    if not quantity or not price or not symbol:
        print(f"\nUsage: {order_type.lower()} <SYMBOL> <QTY> <PRICE>\n")
        logger.warning(
            "%s command usage error: args=%r — %s",
            order_type.upper(),
            args,
            "bad quantity or price",
        )
        return

    if validate_symbol(symbol, exchange, order_type.upper(), args) == False:
        return

    await broker.submit_order(trader.trader_id, symbol, order_type, quantity, price) 

    print(f"\nOrder placed for {symbol}.\n")


def do_next(context: AppContext):
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
    exchange = context.exchange

    print()
    display_prices(exchange)
    print()


async def do_place_order(context: AppContext, order_type: Literal["buy", "sell"], args: List[str]):
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

    logger = context.logger

    symbol, qty, price = parse_order(args)

    await handle_order(context, order_type, args)

    # only log if parsing succeeded
    if None not in (symbol, qty, price):
        logger.info(
            "%s order queued: symbol=%s, qty=%d, price=%.2f",
            order_type.upper(),
            symbol,
            qty,
            price,
        )


async def do_cancel_order(context: AppContext):
    logger = context.logger

    try:
        trader = context.session.require_active()

    except:
        print("\nYou must log in to use this command. Please use login <trader_id>.\n")
        logger.warning(
            "%s command usage error: %s",
            "CANCEL",
            "user not logged in",
        )
        return

    trader = context.session.active_trader
    broker = context.broker

    pending_orders = list(trader.pending_orders.values())

    if not pending_orders:
        print("\n Currently you have no pending orders that you can cancel.\n")
        return

    print(
        "\nTo cancel an order, please choose an order number to cancel from your pending orders:\n"
    )

    for index, order in enumerate(pending_orders):
        print(
            f"{index + 1}: Order for {order.quantity} {order.symbol} shares at ${order.limit_price}\n"
        )

    print("Alternatively, you can cancel the operation by writing 'q'\n")

    while True:
        try:
            raw = input(">>> ")
        except EOFError:
            break

        if raw.strip() == "q":
            print("\nThe operation was cancelled.\n")
            break

        if not raw.strip() or not raw.isdigit() or int(raw) not in range(1, len(pending_orders) + 1):
            print(
                "\nPlease choose an order number to cancel or cancel the operation by writing 'q'\n"
                )
        else:
            order_id = pending_orders[int(raw) - 1].order_id
            await broker.cancel_order(order_id)
            print("\nThe order has been successfully cancelled.\n")
            break
            



def do_match(context: AppContext, args: List[str]):
    """
    Attempt to match orders for a given symbol and display results.

    Examples:
        >>> from engine.exchange import Exchange
        >>> from engine.stock import Stock
        >>> ex = Exchange({'AAPL': Stock('AAPL', 100.0)})
        >>> do_match(ex, ['AAPL'])
        No trades yet
    """
    logger = context.logger
    exchange = context.exchange
    broker = context.broker

    if not args or len(args) != 1:
        print("\nUsage: match <SYMBOL>\n")
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

    trades: List[Trade] = []

    while True:
        trade = exchange.match_orders(symbol)
        if not trade:
            break
        broker.settle_trade(trade)
        trades.append(trade)
    

    if not trades:
        print("\nNo trades yet\n")
    else:
        for t in trades:
            print(f"\nTRADE: {t.quantity}×{t.symbol} @ ${t.price:.2f}")
            logger.info(
                "MATCH command status: trade symbol=%s processed @ qty=%d, price=%.2f",
                symbol,
                t.quantity,
                t.price,
            )
        print()


def do_portfolio(context: AppContext):

    session, logger, exchange, broker = context.session, context.logger, context.exchange, context.broker

    try:
        trader = session.require_active()
    except:
        print("\nYou must log in to use this command. Please use login <trader_id>.\n")
        logger.warning(
            "%s command usage error: %s",
            "PORTFOLIO",
            "user not logged in",
        )
        return

    logger.info("PORTFOLIO viewed")
    display_portfolio(exchange, broker.traders[trader.trader_id])


def do_status(context: AppContext):
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
    logger, exchange = context.logger, context.exchange

    pending = sum(
        book.total_size
        for book in exchange.order_books.values()
    )
    if pending > 0:
        display_pending_orders(exchange)
    else:
        print("\nCurrently there are no pending orders on the exchange.\n")


    logger.info("STATUS viewed: %d pending orders", pending)


def do_login(context: AppContext, args):
    logger, session = context.logger, context.session

    if args is None or len(args) != 1 or args[0].isnumeric() == False:
        print("\nUsage: login <trader_id>\n")
        logger.warning(
            "%s command usage error: args=%r — %s",
            "LOGIN",
            args,
            "bad trader_id",
        )
        return

    trader_id = str(args[0])

    try:
        session.login(trader_id)
        print(f"\n Logged in as trader {session.active_trader.trader_id}\n")
    except:
        print("\nUnknown trader_id. Please try again.\n")
        logger.warning(
            "%s command usage error: args=%r — %s",
            "LOGIN",
            args,
            "unknown trader_id",
        )
        return


def do_logout(context: AppContext):
    session, logger = context.session, context.logger

    try:
        session.logout()
        print("\nYou have successfully logged out.\n")
    except:
        print("\nYou cannot log out if you are currently not logged in.\n")
        logger.warning(
            "%s command usage error: %s",
            "LOGOUT",
            "no active trader logged in",
        )


def do_help(context: AppContext):
    display_help_menu()


def log_quit(context: AppContext):
    """
    Print goodbye and log shutdown.

    Examples:
        >>> log_quit() # doctest: +NORMALIZE_WHITESPACE
        Thank you for using York Stock Exchange.
    """
    logger = context.logger

    print("\nThank you for using York Stock Exchange.")
    logger.info("York Stock Exchange CLI shutting down")
