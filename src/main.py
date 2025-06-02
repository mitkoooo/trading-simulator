from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock
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
    exchange.register_trader(trader)

    logger.info("York Stock Exchange CLI v1.0 starting up")

    WELCOME_MESSAGE = """
      Welcome to York Stock Exchange. To continue please enter one of the following commands:

          next - To update stock prices
          match - To match orders
          status - To display pending orders
          buy - To buy a stock
          sell - To sell a stock
          quit - to exit York Stock Exchange
      """

    print(WELCOME_MESSAGE)
    display_portfolio(trader)

    CLI(exchange, trader, logger).run()


if __name__ == "__main__":
    main()
