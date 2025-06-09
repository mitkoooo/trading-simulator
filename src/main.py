from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock
from engine.position import Position
from view.render import display_portfolio
from cli.cli import CLI
from engine.order import Order

from logging_config import setup_logger

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


def main():
    logger = setup_logger()
    exchange = Exchange(market_data=MARKET_DATA)
    trader = Trader(trader_id=1, starting_balance=1000000)
    trader2 = Trader(trader_id=42, starting_balance=1000000)
    trader2.portfolio._positions["AAPL"] = Position(999, 150.0)

    exchange.add_order(
        Order(
            trader_id=42,
            symbol="AAPL",
            order_type="sell",
            quantity=999,
            limit_price=150,
        )
    )
    exchange.register_trader(trader)
    exchange.register_trader(trader2)

    logger.info("York Stock Exchange CLI v1.0 starting up")

    WELCOME_MESSAGE = """Welcome to York Stock Exchange. To continue please enter one of the following commands:

    next      -   update stock prices
    match     -   match orders
    portfolio -   display trader's portfolio
    status    -   display pending orders
    buy       -   buy a stock
    sell      -   sell a stock
    quit      -   exit York Stock Exchange
"""

    print(WELCOME_MESSAGE)
    display_portfolio(exchange, trader)

    CLI(exchange, trader, logger).run()


if __name__ == "__main__":
    main()
