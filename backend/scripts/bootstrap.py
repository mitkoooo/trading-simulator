import asyncio
from pathlib import Path
from typing import Dict, Literal, Optional

import yaml

from app.context import AppContext
from app.session import Session
from config.logging_config import setup_logger
from engine.bots.passive_mm.passive_mm import PassiveMM
from engine.bots.retail_poisson import RetailPoisson
from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange
from engine.exchange.participant_info import ParticipantInfo
from engine.instruments.stock import Stock
from engine.order_book.order import Order
from engine.trader import Trader

# backend/bootstrap.py lives under backend/
BASE_DIR = Path(__file__).resolve().parents[1]  # -> <repo>/backend
CONFIG_DIR = (BASE_DIR / "config").resolve()


def register_bots_from_yaml(exchange: Exchange, bot: Dict):
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
    participants_path: Optional[str | Path] = None,
    market_data_path: Optional[str | Path] = None,
):
    participants_path = Path(
        participants_path or CONFIG_DIR / "participants.yml"
    )

    market_data_path = Path(market_data_path or CONFIG_DIR / "market_data.yml")

    market_data_yml = yaml.safe_load(open(market_data_path))

    def _get_seed_price(i, side: Literal["buy", "sell"]) -> float:
        sign = 1 if side == "sell" else -1
        return market_data_yml[symbol] + sign * i * tick

    # 1. Core systems
    exchange = Exchange()
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
        register_bots_from_yaml(exchange, ss)

    for mm in config["market_makers"]:
        register_bots_from_yaml(exchange, mm)

        categories = ["symbol", "base_size", "alpha", "beta", "gamma"]

        bot_kwargs = {k: mm[k] for k in categories}

        mm = PassiveMM(exchange, mpid=mm["mpid"], **bot_kwargs)

        asyncio.create_task(mm.run())

    for rp in config["retail_bots"]:
        register_bots_from_yaml(exchange, rp)

        categories = [
            "symbol",
            "limit_rate",
            "market_rate",
            "quantity_range",
            "tick_size",
            "market_probability",
        ]

        bot_kwargs = {k: rp[k] for k in categories}

        rp = RetailPoisson(exchange, mpid=rp["mpid"], **bot_kwargs)

        asyncio.create_task(rp.run())

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

    await exchange.start()

    traders = {"1": trader1, "2": trader2}

    context = AppContext(Session(traders), broker, exchange, logger)

    return context
