from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock

from typing import List, Tuple
import logging

logger = logging.getLogger("york_exchange")
logger.setLevel(logging.INFO)
logger.propagate = False

handler = logging.FileHandler("trading.log", encoding="utf-8")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)-5s | %(message)s")
handler.setFormatter(formatter)

logger.addHandler(handler)

# Dummy initial prices for Day 3 CLI setup
MARKET_DATA = {
    "AAPL": Stock("AAPL", 150.00),
    "MSFT": Stock("MSFT", 295.50),
    "GOOG": Stock("GOOG", 2830.75),
    "AMZN": Stock("AMZN", 3505.20),
    "TSLA": Stock("TSLA", 720.25),
    "NFLX": Stock("NFLX", 505.60),
    "FB": Stock("FB", 355.45),
}


def display_prices(exchange: Exchange):
    print("")
    for stock in exchange.market_data.values():
        nxt = stock.simulate_price_tick()
        stock.update_price(nxt)
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


def parse_order(args: List[str]) -> Tuple[str, int, float]:
    if len(args) != 3:
        return None, None, None

    symbol, quantity, price = args

    try:
        return symbol, int(quantity), float(price)
    except ValueError:
        return symbol, None, None


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

    if symbol not in exchange.market_data:
        valid = ", ".join(sorted(exchange.market_data.keys()))

        print(f"Unknown symbol. Please enter one of: {valid}")

        logger.warning(
            "%s command usage error: args=%r — unknown symbol", order_type.upper(), args
        )
        return

    o = trader.place_order(
        symbol=symbol, order_type=order_type, quantity=quantity, price=price
    )
    exchange.add_order(o)
    print(f"\nOrder placed for {symbol}.")
    display_portfolio(trader)


def main():
    logger.info("York Stock Exchange CLI v1.0 starting up")

    exchange = Exchange(market_data=MARKET_DATA)
    trader = Trader(trader_id=1, cash_balance=1000000)

    print(
        """
      Welcome to York Stock Exchange. To continue please enter one of the following commands:

          next - To update stock prices
          status - To display pending orders
          buy - To buy a stock
          sell - To sell a stock
          quit - to exit York Stock Exchange
      """
    )
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
    def do_next():
        display_prices(exchange)
        display_portfolio(trader)

    @log_command
    def do_place_order(order_type: str, args: List[str]):

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
    def do_status():
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

    commands = {
        "next": lambda args=None: do_next(),
        "buy": lambda args=[]: do_place_order("buy", args),
        "sell": lambda args=[]: do_place_order("sell", args),
        "status": lambda args=None: do_status(),
    }

    while True:
        try:
            tokens = input(">>> ").split()
        except EOFError:
            # end‐of‐input (e.g. in a smoke‐test), so exit gracefully
            log_quit()
            break

        if not tokens:
            print()
            continue

        cmd, *args = tokens
        action = commands.get(cmd)
        if action:
            action(args) if args else action()
        elif cmd == "quit":
            log_quit()
            break
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()
