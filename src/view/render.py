from engine.exchange import Exchange
from engine.trader import Trader


def display_prices(exchange: Exchange):
    """
    Simulate a tick and print each stock’s updated price.

    Examples:
    >>> from engine.stock import Stock
    >>> from engine.exchange import Exchange
    >>> from view.render import display_prices
    >>> s = Stock("AAPL", 100.0)
    >>> ex = Exchange(market_data={"AAPL": s})
    >>> s.update_price(101.0)
    >>> display_prices(ex)  # doctest: +NORMALIZE_WHITESPACE
    AAPL: $101.00
    """

    print()
    for stock in exchange.market_data.values():
        print(f"{stock.symbol}: ${stock.price:.2f}")
    print()


def display_portfolio(trader: Trader):
    """
    Print the trader's cash balance and current holdings.

    Examples:
        >>> from engine.trader import Trader
        >>> from view.render   import display_portfolio
        >>> tr = Trader(trader_id=1, cash_balance=1000.0)
        >>> display_portfolio(tr)  # doctest: +NORMALIZE_WHITESPACE
        Cash balance: $1000.0
        Holdings: {}
    """
    print(f"\nCash balance: ${trader.cash_balance}")
    print(f"Holdings: {trader.holdings}\n")


def display_pending_orders(exchange: Exchange):
    """
    Print all pending buy/sell orders in the exchange.

    Examples:
        >>> from engine.stock    import Stock
        >>> from engine.exchange import Exchange
        >>> from engine.trader   import Trader
        >>> from view.render     import display_pending_orders
        >>> ex = Exchange(market_data={"AAPL": Stock("AAPL", 100.0)})
        >>> tr = Trader(trader_id=1, cash_balance=1000.0)
        >>> o = tr.place_order(symbol="AAPL", order_type="buy", quantity=1, price=100.0)
        >>> ex.add_order(o)
        >>> display_pending_orders(ex)  # doctest: +SKIP
    """
    for order_book in exchange.order_books.values():
        for heap in [order_book.sell_heap, order_book.buy_heap]:
            for order in heap:
                message = (
                    f"\n[{order.timestamp:%Y-%m-%d %H:%M:%S}] Pending {order.order_type.capitalize()} Order: "
                    f"{order.quantity} share{'s' if order.quantity != 1 else ''} of {order.symbol} "
                    f"at ${order.limit_price:,.2f}."
                )
                print(message)
