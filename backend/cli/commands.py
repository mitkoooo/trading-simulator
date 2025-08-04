from typing import Literal

from app.context import AppContext
from cli.render import (
    display_help_menu,
    display_pending_orders,
    display_portfolio,
    display_prices,
)
from cli.validation import parse_order, validate_symbol
from engine.trade import Trade
from engine.trader import Trader


async def handle_order(
    context: AppContext, order_type: Literal["buy", "sell"], args: list[str]
) -> None:
    """Handle a buy or sell order.

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
    exchange, session, logger, broker = (
        context.exchange,
        context.session,
        context.logger,
        context.broker,
    )

    assert logger

    try:
        trader = session.require_active()

    except RuntimeError:
        msg = ("\nYou must log in to use this command." +
               "Please use login <trader_id>.\n")

        print(msg)
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

    if not validate_symbol(symbol, exchange, order_type.upper(), args):
        return

    await broker.submit_order(
        trader.trader_id, symbol, order_type, quantity, price
    )

    print(f"\nOrder placed for {symbol}.\n")


def do_next(context: AppContext) -> None:
    """Advance the market by one tick and display prices & portfolio.

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


async def do_place_order(
    context: AppContext, order_type: Literal["buy", "sell"], args: list[str]
) -> None:
    """Enqueue a buy/sell order and log details if valid.

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
    assert logger

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


async def do_cancel_order(context: AppContext) -> None:
    """Cancel a pending order."""
    logger = context.logger
    assert logger

    try:
        context.session.require_active()
    except RuntimeError:
        msg = ("\nYou must log in to use this command." +
               "Please use login <trader_id>.\n")
        print(msg)

        logger.warning(
            "%s command usage error: %s",
            "CANCEL",
            "user not logged in",
        )
        return

    trader: Trader | None = context.session.active_trader
    assert trader
    broker = context.broker

    pending_orders = list(trader.pending_orders.values())

    if not pending_orders:
        print("\n Currently you have no pending orders that you can cancel.\n")
        return

    msg = ("\nTo cancel an order, please choose an order number" + 
           "to cancel from your pending orders:\n")
    print(msg)

    for index, order in enumerate(pending_orders):
        msg = (f"{index + 1}: Order for {order.quantity}" +
        f"{order.symbol} shares at ${order.limit_price}\n")
        print(msg)

    print("Alternatively, you can cancel the operation by writing 'q'\n")

    while True:
        try:
            raw = input(">>> ")
        except EOFError:
            break

        if raw.strip() == "q":
            print("\nThe operation was cancelled.\n")
            break

        if (
            not raw.strip()
            or not raw.isdigit()
            or int(raw) not in range(1, len(pending_orders) + 1)
        ):  
            msg = ("\nPlease choose an order number to cancel" + 
                   " or cancel the operation by writing 'q'\n")
            print(msg)
        else:
            order_id = pending_orders[int(raw) - 1].order_id
            await broker.cancel_order(order_id)
            print("\nThe order has been successfully cancelled.\n")
            break


def do_match(context: AppContext, args: list[str]) -> None:
    """Attempt to match orders for a given symbol and display results.

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

    assert logger

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

    if not validate_symbol(symbol, exchange, "MATCH", args):
        return

    trades: list[Trade] = []

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
            print(f"\nTRADE: {t.quantity}x{t.symbol} @ ${t.price:.2f}")
            logger.info(
                """MATCH command status:
                   trade symbol=%s processed @ qty=%d, price=%.2f""",
                symbol,
                t.quantity,
                t.price,
            )
        print()


def do_portfolio(ctx: AppContext) -> None:
    """Display trader's cash balance and shares owned.
    
    Args:
        ctx (AppContext):
            Application context containing `Session`.

    """
    session, logger, exchange, broker = (
        ctx.session,
        ctx.logger,
        ctx.exchange,
        ctx.broker,
    )
    assert logger

    try:
        trader = session.require_active()
    except RuntimeError:
        msg = ("\nYou must log in to use this command." +
               "Please use login <trader_id>.\n")
        print(msg)
        logger.warning(
            "%s command usage error: %s",
            "PORTFOLIO",
            "user not logged in",
        )
        return

    logger.info("PORTFOLIO viewed")
    display_portfolio(exchange, broker.traders[trader.trader_id])

def do_status(ctx: AppContext) -> None:
    """Display pending orders and the trader's portfolio.

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
    logger, exchange = ctx.logger, ctx.exchange
    assert logger

    pending = sum(book.total_size for book in exchange.order_books.values())
    if pending > 0:
        display_pending_orders(exchange)
    else:
        print("\nCurrently there are no pending orders on the exchange.\n")

    logger.info("STATUS viewed: %d pending orders", pending)


def do_login(ctx: AppContext, args: list[str]) -> None:
    """Log in the user into the active session.

    Args:
        ctx (AppContext):
            Application context containing `Session`.

        args (list[str]):
            Arguments to `login` command.

    """
    logger, session = ctx.logger, ctx.session
    assert logger

    if args is None or len(args) != 1 or not args[0].isnumeric():
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
        assert session.active_trader
        print(f"\n Logged in as trader {session.active_trader.trader_id}\n")
    except KeyError:
        print("\nUnknown trader_id. Please try again.\n")
        logger.warning(
            "%s command usage error: args=%r — %s",
            "LOGIN",
            args,
            "unknown trader_id",
        )
        return


def do_logout(ctx: AppContext) -> None:
    """Log out the user from the active session.

    Args:
        ctx (AppContext):
            Application context containing `Session`.

    """
    session, logger = ctx.session, ctx.logger
    assert logger

    try:
        session.logout()
        print("\nYou have successfully logged out.\n")
    except RuntimeError:
        print("\nYou cannot log out if you are currently not logged in.\n")
        logger.warning(
            "%s command usage error: %s",
            "LOGOUT",
            "no active trader logged in",
        )


def do_help(_: AppContext) -> None:
    """Display help menu."""
    display_help_menu()


def log_quit(ctx: AppContext) -> None:
    """Print goodbye and log shutdown.

    Examples:
        >>> log_quit() # doctest: +NORMALIZE_WHITESPACE
        Thank you for using York Stock Exchange.

    """
    logger = ctx.logger
    assert logger

    print("\nThank you for using York Stock Exchange.")
    logger.info("York Stock Exchange CLI shutting down")
