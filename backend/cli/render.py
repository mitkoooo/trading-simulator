from engine.exchange.exchange import Exchange
from engine.trader import Trader

HELP_MENU = """
    login      — Authenticate using your Trader ID
    logout     - Log out the trader
    help       — Display this menu
    next       — Refresh market data
    match      — Execute order matching
    portfolio  — View your portfolio holdings and P&L
    status     — Show pending orders
    buy        — Place a buy order
    sell       — Place a sell order
    cancel     - Cancel an order
    quit       — Exit the terminal
    """

WELCOME_MESSAGE = f"""
GHOSTSWAP TERMINAL

Please log in with your Trader ID before issuing any other commands.
{HELP_MENU}"""


def display_prices(exchange: Exchange) -> None:
    """Simulate a tick and print each stock's updated price.

    Examples:
    >>> from engine.stock import Stock
    >>> from engine.exchange import Exchange
    >>> from view.render import display_prices
    >>> s = Stock("AAPL", 100.0)
    >>> ex = Exchange(market_data={"AAPL": s})
    >>> s.update_price(101.0)
    >>> display_prices(ex)  # doctest: +NORMALIZE_WHITESPACE
    AAPL  | $101.00

    """
    for symbol, order_book in exchange.order_books.items():
        print(f"{symbol:<5} | ${order_book.last_trade_price:.2f}")


def display_portfolio(exchange: Exchange, trader: Trader) -> None:
    """Print `Trader` cash balance and current positions.

    Examples:
        >>> from engine.trader import Trader
        >>> from view.render import display_portfolio
        >>> tr = Trader(trader_id=1, starting_balance=1000.0)
        >>> display_portfolio(tr)  # doctest: +SKIP
    ┌──────────────────────────────────────────────────────────────┐
    │                          PORTFOLIO                           │
    ├──────────────────────────────────────────────────────────────┤
    │  Cash: $998800.00                                            │
    │  Positions:                                                  │
    │    AAPL: 4 @ $150.72  (avg $150.00, unrealized P/L +$0.88)   │
    └──────────────────────────────────────────────────────────────┘

    """
    box_width = 64
    inner_width = box_width - 2
    top = "┌" + "─" * inner_width + "┐"
    title = "│" + "PORTFOLIO".center(inner_width) + "│"
    sep = "├" + "─" * inner_width + "┤"
    cash_line = (
        f"│ Cash: ${trader.portfolio.cash}".ljust(inner_width + 1) + "│"
    )
    positions_header = "│ Positions:".ljust(inner_width + 1) + "│"

    print()
    print(top)
    print(title)
    print(sep)
    print(cash_line)
    print(positions_header)

    positions = trader.portfolio.positions
    if not positions:
        none_line = "│    None".ljust(inner_width + 1) + "│"
        print(none_line)
    else:
        for symbol, pos in positions.items():
            pnl = trader.portfolio.calculate_unrealized_pl(symbol,
                                                           exchange.quotes)
            s = symbol
            p = pos.avg_price
            q = pos.qty

            line = (
                f"│    {s}: {q} @ ${p}, unrealized P/L +${pnl:,.2f}".ljust(
                    inner_width + 1
                )
                + "│"
            )
            print(line)

    bottom = "└" + "─" * inner_width + "┘"
    print(bottom)
    print()


def display_pending_orders(exchange: Exchange) -> None:
    """Print all pending buy/sell orders in the exchange.

    Examples:
        >>> from engine.stock    import Stock
        >>> from engine.exchange import Exchange
        >>> from engine.trader   import Trader
        >>> from view.render     import display_pending_orders
        >>> ex = Exchange(market_data={"AAPL": Stock("AAPL", 100.0)})
        >>> tr = Trader(trader_id=1, starting_balance=1000.0)
        >>> o = tr.place_order(symbol="AAPL", order_type="buy",
        >>>                    quantity=1, price=100.0)
        >>> ex.add_order(o)
        >>> display_pending_orders(ex)  # doctest: +SKIP

    """
    message = ""

    for order_book in exchange.order_books.values():
        for order in (
            order_book.get_n_buy_orders() + order_book.get_n_sell_orders()
        ):
            if order.status == "cancelled":
                continue

            ts = order.timestamp
            order_type = order.order_type.capitalize()
            s = order.symbol
            q = order.quantity

            message += (
                f"\n[{ts:%Y-%m-%d %H:%M:%S}] Pending {order_type} Order: "
                f"{q} share{'s' if q != 1 else ''} of {s} "
                f"@ ${order.limit_price:,.2f}."
            )
    if not message:
        print("\n Currently no active orders on the exchange.\n")
        return
    print(message)
    print()


def display_welcome() -> None:
    """Display welcome message in CLI."""
    print(WELCOME_MESSAGE)


def display_help_menu() -> None:
    """Display help menu in CLI."""
    print(HELP_MENU)
