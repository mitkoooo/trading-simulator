from datetime import datetime
from engine.market_data.quote import MarketQuote
from engine.trader import Trader
from engine.position import Position
from engine.instruments.stock import Stock

from app.context import AppContext


def test_portfolio_value_pure_cash(test_context: AppContext):
    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_exchange = test_context.exchange

    assert (
        sample_trader.portfolio.value(sample_exchange.quotes)
        == sample_trader.portfolio.cash + sample_trader.portfolio.reserved_cash
    )


def test_portfolio_value_combined(test_context: AppContext):
    SYMBOL = "AAPL"
    SHARE_NUM = 50
    test_context.exchange.quotes[SYMBOL] = MarketQuote(symbol=SYMBOL, bid_price=None, bid_size=None, ask_price=None, ask_size=None, last_price=100, timestamp=datetime.now())

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_exchange = test_context.exchange

    sample_trader.portfolio.positions[SYMBOL] = Position(symbol=SYMBOL, qty=SHARE_NUM)
    assert sample_trader.portfolio.value(sample_exchange.quotes) == (
        sample_trader.portfolio.cash + sample_trader.portfolio.reserved_cash
    ) + (sample_exchange.quotes[SYMBOL].last_price * SHARE_NUM)


def test_portfolio_calculate_unrealized_pl_loss(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 1
    SYMBOL = "AAPL"
    test_context.exchange.quotes[SYMBOL] = MarketQuote(symbol=SYMBOL, bid_price=None, bid_size=None, ask_price=None, ask_size=None, last_price=AVG_PRICE - 1, timestamp=datetime.now())

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, test_context.exchange.quotes)

    assert pl == -(1 * POSITION_QTY)


def test_portfolio_calculate_unrealized_pl_profit(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 1
    SYMBOL = "AAPL"
    test_context.exchange.quotes[SYMBOL] = MarketQuote(symbol=SYMBOL, bid_price=None, bid_size=None, ask_price=None, ask_size=None, last_price=AVG_PRICE + 1, timestamp=datetime.now())

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, test_context.exchange.quotes)

    assert pl == +(1 * POSITION_QTY)


def test_portfolio_calculate_pl_unknown_ticket(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 50
    SYMBOL = "FOO"

    sample_trader: Trader = test_context.session.active_trader
    assert sample_trader

    sample_trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY, AVG_PRICE)

    try:
        pl = sample_trader.portfolio.calculate_unrealized_pl(SYMBOL, test_context.exchange.quotes)
        assert False
    except:
        assert True
