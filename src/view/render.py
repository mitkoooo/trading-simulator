from engine.exchange import Exchange
from engine.trader import Trader


def display_prices(exchange: Exchange):
    """
    Simulate a tick and print each stock's updated price.

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
    for stock in exchange.market_data.values():
        print(f"{stock.symbol:<5} | ${stock.price:.2f}")


def display_portfolio(trader: Trader):
    """
    Print the trader's cash balance and current holdings in a Bloomberg‐style box.

    Examples:
        >>> from engine.trader import Trader
        >>> from view.render import display_portfolio
        >>> tr = Trader(trader_id=1, starting_balance=1000.0)
        >>> display_portfolio(tr)  # doctest: +NORMALIZE_WHITESPACE
        ┌────────────────────────────────┐
        │           PORTFOLIO            │
        ├────────────────────────────────┤
        │ Cash: $1000.0                  │
        │ Holdings:                      │
        │   None                         │
        └────────────────────────────────┘
    """
    box_width = 32
    inner_width = box_width - 2
    top = "┌" + "─" * inner_width + "┐"
    title = "│" + "PORTFOLIO".center(inner_width) + "│"
    sep = "├" + "─" * inner_width + "┤"
    cash_line = f"│ Cash: ${trader.portfolio.cash}".ljust(inner_width + 1) + "│"
    holdings_header = "│ Holdings:".ljust(inner_width + 1) + "│"

    print()
    print(top)
    print(title)
    print(sep)
    print(cash_line)
    print(holdings_header)

    holdings = trader.portfolio.holdings
    if not holdings:
        none_line = f"│    None".ljust(inner_width + 1) + "│"
        print(none_line)
    else:
        for symbol, qty in holdings.items():
            line = f"│    {symbol}: {qty}".ljust(inner_width + 1) + "│"
            print(line)

    bottom = "└" + "─" * inner_width + "┘"
    print(bottom)
    print()


def display_pending_orders(exchange: Exchange):
    """
    Print all pending buy/sell orders in the exchange.

    Examples:
        >>> from engine.stock    import Stock
        >>> from engine.exchange import Exchange
        >>> from engine.trader   import Trader
        >>> from view.render     import display_pending_orders
        >>> ex = Exchange(market_data={"AAPL": Stock("AAPL", 100.0)})
        >>> tr = Trader(trader_id=1, starting_balance=1000.0)
        >>> o = tr.place_order(symbol="AAPL", order_type="buy", quantity=1, price=100.0)
        >>> ex.add_order(o)
        >>> display_pending_orders(ex)  # doctest: +SKIP
    """
    for order_book in exchange.order_books.values():
        for order in order_book.get_buy_orders() + order_book.get_sell_orders():
            message = (
                f"\n[{order.timestamp:%Y-%m-%d %H:%M:%S}] Pending {order.order_type.capitalize()} Order: "
                f"{order.quantity} share{'s' if order.quantity != 1 else ''} of {order.symbol} "
                f"@ ${order.limit_price:,.2f}."
            )
            print(message)
