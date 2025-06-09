from engine.exchange import Exchange
from engine.trader import Trader
from engine.stock import Stock
from engine.position import Position
from engine.market_simulator import MarketSimulator
from view.render import display_portfolio
from cli.cli import CLI
from engine.order import Order

import argparse
from datetime import timedelta
from logging_config import setup_logger
from logging import Logger

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


def manual_loop(exchange: Exchange, logger: Logger):
    WELCOME_MESSAGE = """
YORK STOCK EXCHANGE TERMINAL

Please log in with your Trader ID before issuing any other commands.

    login      — Authenticate using your Trader ID
    help       — Display this menu
    next       — Refresh market data
    match      — Execute order matching
    portfolio  — View your portfolio holdings and P&L
    status     — Show pending orders
    buy        — Place a buy order
    sell       — Place a sell order
    quit       — Exit the terminal
"""

    print(WELCOME_MESSAGE)

    CLI(exchange, logger).run()


def main():
    parser = argparse.ArgumentParser(description="York Stock Exchange Simulator")
    parser.add_argument(
        "--auto",
        nargs="?",
        const="-1",
        default=None,
        metavar="N",
        help="run automatically for N steps (omit N for infinite); omit flag for manual",
    )
    args = parser.parse_args()

    logger = setup_logger()
    exchange = Exchange(market_data=MARKET_DATA)
    trader = Trader(trader_id=1, starting_balance=1000000)
    trader2 = Trader(trader_id=42, starting_balance=1000000)

    trader2.portfolio._positions["AAPL"] = Position(0, 150.0)
    trader2.portfolio._reserved_positions["AAPL"] = Position(999, 150.0)

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

    sim = MarketSimulator(exchange, tick_interval=timedelta(seconds=1))

    logger.info("York Stock Exchange CLI v1.0 starting up")

    if args.auto is not None:
        # args.auto == None means “no limit” (infinite); else run that many steps

        # --auto *was* used (with or without N)
        if args.auto == "-1":
            steps = None  # infinite
        else:
            steps = int(args.auto)  # the provided number
        sim.run(steps)
    else:
        manual_loop(exchange, logger)


if __name__ == "__main__":
    main()
