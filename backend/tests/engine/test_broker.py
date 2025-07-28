import pytest

from engine.broker.broker import Broker
from engine.exchange.exchange import Exchange
from engine.position import Position
from engine.trader import Trader

@pytest.mark.asyncio
async def test_broker_reserves_cash_on_order(sample_broker: Broker, sample_trader: Trader):
    trader_id = sample_trader.trader_id
    old_cash = sample_trader.portfolio.cash
    SYMBOL = "AAPL"
    ORDER_TYPE = "buy"
    QUANTITY = 10
    LIMIT_PRICE = 10
    notional = QUANTITY * LIMIT_PRICE

    await sample_broker.submit_order(trader_id, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)
    assert sample_trader.portfolio.cash == old_cash - notional

@pytest.mark.asyncio
async def test_broker_reserves_shares_on_order(sample_broker: Broker, sample_trader: Trader):
    SYMBOL = "AAPL"
    ORDER_TYPE = "sell"
    old_quantity = 10
    QUANTITY = 10
    LIMIT_PRICE = 10

    sample_trader.portfolio.positions[SYMBOL] = Position(qty=old_quantity, avg_price=10)

    trader_id = sample_trader.trader_id
    

    await sample_broker.submit_order(trader_id, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)

    assert sample_trader.portfolio.positions[SYMBOL].qty == old_quantity - QUANTITY


@pytest.mark.asyncio
async def test_broker_release_cash_on_cancel(sample_broker: Broker, sample_trader: Trader):
    trader_id = sample_trader.trader_id
    old_cash = sample_trader.portfolio.cash
    SYMBOL = "AAPL"
    ORDER_TYPE = "buy"
    QUANTITY = 10
    LIMIT_PRICE = 10

    o = await sample_broker.submit_order(trader_id, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)
    await sample_broker.cancel_order(o.order_id)

    assert sample_trader.portfolio.cash == old_cash


@pytest.mark.asyncio
async def test_broker_release_shares_on_cancel(sample_broker: Broker, sample_trader: Trader):
    SYMBOL = "AAPL"
    ORDER_TYPE = "sell"
    old_quantity = 10
    QUANTITY = 10
    LIMIT_PRICE = 10

    sample_trader.portfolio.positions[SYMBOL] = Position(qty=old_quantity, avg_price=10)

    trader_id = sample_trader.trader_id
    

    o = await sample_broker.submit_order(trader_id, SYMBOL, ORDER_TYPE, QUANTITY, LIMIT_PRICE)
    await sample_broker.cancel_order(o.order_id)

    assert sample_trader.portfolio.positions[SYMBOL].qty == old_quantity


@pytest.mark.asyncio
async def test_broker_reserves_cash_on_partial_fill(sample_exchange: Exchange, sample_broker: Broker, sample_trader: Trader, sample_trader2: Trader):
    SYMBOL = "AAPL"
    old_cash = sample_trader2.portfolio.cash
    QUANTITY = 10
    LIMIT_PRICE = 10
    notional = QUANTITY * LIMIT_PRICE

    sample_trader.portfolio.positions[SYMBOL] = Position(qty=10, avg_price=10)

    sell_trader_id = sample_trader.trader_id
    buy_trader_id = sample_trader2.trader_id


    await sample_broker.submit_order(sell_trader_id, SYMBOL, "sell", QUANTITY - 5, LIMIT_PRICE)
    await sample_broker.submit_order(buy_trader_id, SYMBOL, "buy", QUANTITY, LIMIT_PRICE)

    assert sample_trader2.portfolio.cash == old_cash - notional 




