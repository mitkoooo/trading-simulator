from datetime import date
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

    def _get_seed_price(symbol: str, i: int,
                        side: Literal["buy", "sell"]) -> float:
        sign = 1 if side == "sell" else -1
        day = date(2025, 8, 5)
        today_data = market_data_yml[day]
        symbol_data = today_data[symbol]

        open_price = symbol_data["open"]
        
        return open_price + sign * i * tick

    # 1. Core systems
    exchange = Exchange()
    bot_manager = BotManager()
    broker = Broker(exchange, mpid="BR01")
    logger = setup_logger()

    _register_instruments(market_data_yml=market_data_yml,
                          exchange=exchange)

    trs = _register_traders(broker)


    # 2. Load participants
    config = yaml.safe_load(open(participants_path))

    for ss in config["system_seed"]:
        _register_bots_from_yaml(exchange, ss)

    for mm in config["market_makers"]:
        _register_bots_from_yaml(exchange, mm)


        mm_settings: PassiveMMSettings = PassiveMMSettings()

        mm_settings.base_size = mm["base_size"]
        mm_settings.inv_limit = mm["inv_limit"]
        mm_settings.alpha = mm["alpha"]
        mm_settings.beta = mm["beta"]
        mm_settings.gamma = mm["gamma"]

        mm_bot = PassiveMM(symbol=mm["symbol"], exchange=exchange,
                        mpid=mm["mpid"], settings=mm_settings)

        bot_manager.register_bot(mm_bot)

    for rp in config["retail_bots"]:
        _register_bots_from_yaml(exchange, rp)

        rp_settings: RetailPoissonSettings = RetailPoissonSettings()

        rp_settings.limit_rate = rp["limit_rate"]
        rp_settings.market_rate = rp["market_rate"]
        rp_settings.quantity_range = rp["quantity_range"]
        rp_settings.tick_size = rp["tick_size"]
        rp_settings.market_probability = rp["market_probability"]

        rp_bot = RetailPoisson(symbol=rp["symbol"], exchange=exchange,
                            mpid=rp["mpid"], settings=rp_settings)
        
        bot_manager.register_bot(rp_bot)

    # SEED THE ORDER BOOKS WITH INITIAL ORDERS
    tick = 0.02
    for symbol in list(exchange.instruments):
        for i in range(1, 6):
            bid_price = _get_seed_price(symbol, i, "buy")
            ask_price = _get_seed_price(symbol, i, "sell")

            for _ in range(1, 100):
                bid = Order("SEED", symbol, "buy", 100, bid_price)
                ask = Order("SEED", symbol, "sell", 100, ask_price)

                await exchange.add_order(bid)
                await exchange.add_order(ask)

    exchange.start()
    bot_manager.start_all()

    traders = {"1": trs[0], "2": trs[1]}

    context = AppContext(Session(traders),broker, exchange,
                         bot_manager, logger)

    return context


def _register_instruments(market_data_yml: dict, exchange: Exchange) -> None:
    instruments = yaml.safe_load(open(Path(CONFIG_DIR / "instruments.yml")))

    for symbol in instruments["equity"]:
        stock = Stock(symbol, tick_size=1)
        exchange.register_instrument(stock)
        day = date(2025, 8, 5)
        today_data = market_data_yml[day]
        symbol_data = today_data[symbol]

        previous_close = symbol_data["previous_close"]
        exchange.order_books[symbol].last_trade_price = previous_close

def _register_traders(broker: Broker) -> list[Trader]:
    trader1 = Trader(trader_id="1", starting_balance=1_000_000)
    trader2 = Trader(trader_id="2", starting_balance=1_000_000)

    traders = [trader1, trader2]

    for tr in traders:
        broker.register_trader(tr)

    return traders
