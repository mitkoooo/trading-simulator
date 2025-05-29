from engine.exchange import Exchange
from engine.trader import Trader


def display_prices(exchange: Exchange):
    print()
    for stock in exchange.market_data.values():
        print(f"{stock.symbol}: ${stock.price:.2f}")
    print()


def display_portfolio(trader: Trader):
    print(f"\nCash balance: ${trader.cash_balance}")
    print(f"Holdings: {trader.holdings}\n")


def display_pending_orders(exchange: Exchange):
    for order_book in exchange.order_books.values():
        for heap in [order_book.sell_heap, order_book.buy_heap]:
            for order in heap:
                message = (
                    f"\n[{order.timestamp:%Y-%m-%d %H:%M:%S}] Pending {order.order_type.capitalize()} Order: "
                    f"{order.quantity} share{'s' if order.quantity != 1 else ''} of {order.symbol} "
                    f"at ${order.limit_price:,.2f}."
                )
                print(message)
