from engine.exchange import Exchange
from engine.trader import Trader
from engine.order import Order
from engine.position import Position
from engine.stock import Stock

from app.context import AppContext


def test_portfolio_value_pure_cash(test_context: AppContext):
    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_exchange = test_context.exchange

    assert (
        sample_trader.portfolio.value(sample_exchange.market_data)
        == sample_trader.portfolio.cash + sample_trader.portfolio.reserved_cash
    )


def test_portfolio_value_combined(test_context: AppContext):    
    SHARE_NUM = 50

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions["AAPL"] = Position(symbol="AAPL", qty=SHARE_NUM)
    assert sample_trader.portfolio.value(sample_exchange.market_data) == (
        sample_trader.portfolio.cash + sample_trader.portfolio.reserved_cash
    ) + (sample_exchange.market_data["AAPL"].price * SHARE_NUM)


def test_portfolio_calculate_unrealized_pl_loss(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 50
    SYMBOL = "AAPL"
    MARKET_DATA = {"AAPL": Stock(SYMBOL, AVG_PRICE - 1)}

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, MARKET_DATA)

    assert pl == -(1 * POSITION_QTY)


def test_portfolio_calculate_unrealized_pl_profit(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 50
    SYMBOL = "AAPL"
    MARKET_DATA = {"AAPL": Stock(SYMBOL, AVG_PRICE + 1)}

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, MARKET_DATA)

    assert pl == +(1 * POSITION_QTY)


def test_portfolio_calculate_pl_unknown_ticket(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 50
    SYMBOL = "FOO"
    MARKET_DATA = {"AAPL": Stock(SYMBOL, AVG_PRICE + 1)}

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    try:
        pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, MARKET_DATA)
        assert False
    except:
        assert True
