from engine.exchange import Exchange
from engine.trader import Trader
from engine.order import Order
from engine.position import Position


def test_portfolio_value_pure_cash(trader: Trader, sample_market: Exchange):
    assert (
        trader.portfolio.value(sample_market.market_data)
        == trader.portfolio.cash + trader.portfolio._reserved_cash
    )


def test_portfolio_value_combined(trader: Trader, sample_market: Exchange):
    SHARE_NUM = 50

    trader.portfolio._positions["AAPL"] = SHARE_NUM
    assert trader.portfolio.value(sample_market.market_data) == (
        trader.portfolio.cash + trader.portfolio._reserved_cash
    ) + (sample_market.market_data["AAPL"].price * SHARE_NUM)


def test_portfolio_reserve_assets_buy(trader: Trader):
    ORDER_QTY = 42
    ORDER_PRICE = 100.00
    TICKET = "AAPL"
    ORDER_TYPE = "buy"

    old_balance = trader.portfolio.cash

    o = Order(trader.trader_id, TICKET, ORDER_TYPE, ORDER_QTY, ORDER_PRICE)
    trader.portfolio.reserve_assets(o)
    assert trader.portfolio.cash == old_balance - ORDER_QTY * ORDER_PRICE
    assert trader.portfolio._reserved_cash == ORDER_QTY * ORDER_PRICE


def test_portfolio_reserve_assets_sell(trader: Trader):
    POSITION_QTY = 50
    ORDER_QTY = 42
    ORDER_PRICE = 100.00
    TICKET = "AAPL"
    ORDER_TYPE = "sell"
    p = Position(POSITION_QTY, ORDER_PRICE)
    old_qty = POSITION_QTY

    trader.portfolio._positions[TICKET] = p

    o = Order(trader.trader_id, TICKET, ORDER_TYPE, ORDER_QTY, ORDER_PRICE)

    trader.portfolio.reserve_assets(o)

    assert trader.portfolio.positions[TICKET].qty == old_qty - ORDER_QTY
