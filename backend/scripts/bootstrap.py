from pathlib import Path
from typing import Literal

import yaml

from app.context import AppContext
from app.session import Session
from config.logging_config import setup_logger
from engine.bots.bot_manager import BotManager
from engine.bots.passive_mm.passive_mm import PassiveMM, PassiveMMSettings
from engine.bots.retail_poisson import RetailPoisson, RetailPoissonSettings
from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange
from engine.exchange.participant_info import ParticipantInfo
from engine.instruments.stock import Stock
from engine.order_book.order import Order
from engine.trader import Trader

# backend/bootstrap.py lives under backend/
BASE_DIR = Path(__file__).resolve().parents[1]  # -> <repo>/backend
CONFIG_DIR = (BASE_DIR / "config").resolve()


def _register_bots_from_yaml(exchange: Exchange, bot: dict) -> None:
    categories = [
        "mpid",
        "display_name",
        "ptype",
        "margin_category",
        "allowed_symbols",
        "price_band_limit",
        "max_order_size",
        "max_notional_per_minute",
        "max_msgs_per_second",
        "clearing_member_id",
        "settlement_account",
        "initial_cash",
        "initial_positions",
    ]

    kwargs = {k: bot[k] for k in categories}

    info = ParticipantInfo(**kwargs)

    exchange.register_participant(bot["mpid"], info)


async def bootstrap(
    participants_path: str | Path | None = None,
    market_data_path: str | Path | None = None,
) -> AppContext:
    """Bootstrap App's state with default settings.
        
    Args:
        participants_path (Path):
            Path to YAML file with info about market participants.

        market_data_path (Path):
            Path to YAML file with initial prices for tickers.
    
    Returns:
        (AppContext): Application context of the simulator.

    """
    participants_path = Path(
        participants_path or CONFIG_DIR / "participants.yml"
    )

    market_data_path = Path(market_data_path or CONFIG_DIR / "market_data.yml")

    market_data_yml = yaml.safe_load(open(market_data_path))

    def _get_seed_price(i: int, side: Literal["buy", "sell"]) -> float:
        sign = 1 if side == "sell" else -1
        return market_data_yml[symbol] + sign * i * tick

    # 1. Core systems
    exchange = Exchange()
    bot_manager = BotManager()
    broker = Broker(exchange, mpid="BR01")
    logger = setup_logger()

    for symbol in market_data_yml:
        stock = Stock(symbol, tick_size=1)
        exchange.register_instrument(stock)
        exchange.order_books[symbol].last_trade_price = market_data_yml[symbol]

    # 2. Register traders
    trader1 = Trader(trader_id="1", starting_balance=1_000_000)
    trader2 = Trader(trader_id="2", starting_balance=1_000_000)
    for tr in (trader1, trader2):
        broker.register_trader(tr)

    # 2. Load participants
    config = yaml.safe_load(open(participants_path))

    for ss in config["system_seed"]:
        _register_bots_from_yaml(exchange, ss)

    for mm in config["market_makers"]:
        _register_bots_from_yaml(exchange, mm)


        settings: PassiveMMSettings = PassiveMMSettings

        settings.base_size = mm["base_size"]
        settings.inv_limit = mm["inv_limit"]
        settings.alpha = mm["alpha"]
        settings.beta = mm["beta"]
        settings.gamma = mm["gamma"]

        bot = PassiveMM(symbol=mm["symbol"], exchange=exchange,
                        mpid=mm["mpid"], settings=settings)

        bot_manager.register_bot(bot)

    for rp in config["retail_bots"]:
        _register_bots_from_yaml(exchange, rp)

        settings: RetailPoissonSettings = RetailPoissonSettings

        settings.limit_rate = rp["limit_rate"]
        settings.market_rate = rp["market_rate"]
        settings.quantity_range = rp["quantity_range"]
        settings.tick_size = rp["tick_size"]
        settings.market_probability = rp["market_probability"]

        bot = RetailPoisson(symbol=rp["symbol"], exchange=exchange,
                            mpid=rp["mpid"], settings=settings)
        
        bot_manager.register_bot(bot)

    # SEED THE ORDER BOOKS WITH INITIAL ORDERS
    tick = 0.02
    for symbol in list(exchange.instruments):
        for i in range(1, 6):
            bid_price = _get_seed_price(i, "buy")
            ask_price = _get_seed_price(i, "sell")

            bid = Order("SEED", symbol, "buy", 100, bid_price)
            ask = Order("SEED", symbol, "sell", 100, ask_price)

            await exchange.add_order(bid)
            await exchange.add_order(ask)

    exchange.start()
    bot_manager.start_all()

    traders = {"1": trader1, "2": trader2}

    context = AppContext(Session(traders),broker, exchange,
                         bot_manager, logger)

    return context
