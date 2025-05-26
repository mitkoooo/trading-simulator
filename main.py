from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock

from typing import List, Tuple

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
    for stock in exchange.market_data.values():
        nxt = stock.simulate_price_tick()
        stock.update_price(nxt)
        print(f"   {stock.symbol}: ${stock.price:.2f}")
    print()


def display_portfolio(trader: Trader):
    print(f"   Cash balance: ${trader.cash_balance}")
    print(f"   Holdings: {trader.holdings}\n")


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
        return

    if symbol not in exchange.market_data:
        print(f"Unknown symbol. Please enter one of: {exchange.market_data.keys()}")
        return

    o = trader.place_order(
        symbol=symbol, order_type=order_type, quantity=quantity, price=price
    )
    exchange.add_order(o)
    print(f"\nOrder placed for {symbol}.\n")
    display_portfolio(trader)


def main():
    market = Exchange(market_data=MARKET_DATA)
    trader = Trader(trader_id=1, cash_balance=1000000)

    print(
        """
      Welcome to York Stock Exchange. To continue please enter one of the following commands:

          next - To update stock prices
          buy - To buy a stock
          sell - To sell a stock
          quit - to exit York Stock Exchange
      """
    )
    display_portfolio(trader)

    commands = {
        "next": lambda: (display_prices(market), display_portfolio(trader)),
        "buy": lambda args=[]: (handle_order(market, trader, "buy", args)),
        "sell": lambda args=[]: (handle_order(market, trader, "sell", args)),
    }

    while True:
        tokens = input(">>> ").split()
        if not tokens:
            continue
        cmd, *args = tokens
        action = commands.get(cmd)
        if action:
            action(args) if args else action()
        elif cmd == "quit":
            print("\nThank you for using York Stock Exchange.")
            break
        else:
            print("Unknown command. Please try again.")


if __name__ == "__main__":
    main()
