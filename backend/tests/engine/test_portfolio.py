from datetime import datetime
from engine.market_data.quote import MarketQuote
from engine.position import Position

from app.context import AppContext


def test_portfolio_value_pure_cash(test_context: AppContext):
    trader = test_context.session.active_trader
    assert trader

    exchange = test_context.exchange

    total_cash = trader.portfolio.cash + trader.portfolio.reserved_cash
    portfolio_value = trader.portfolio.value(exchange.quotes)

    assert portfolio_value == total_cash


def test_portfolio_value_combined(test_context: AppContext):
    SYMBOL = "AAPL"
    SHARE_NUM = 50
    ts = datetime.now()

    quotes = {SYMBOL: MarketQuote(SYMBOL, bid_price=None, bid_size=0,
                                  ask_price=None, ask_size=0, last_price=100,
                                  timestamp=ts)}

    quote = quotes[SYMBOL]
    assert quote and quote.last_price

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[SYMBOL] = Position(SYMBOL, SHARE_NUM)

    total_for_cash = trader.portfolio.cash + trader.portfolio.reserved_cash
    total_for_shares = quote.last_price * SHARE_NUM
    portfolio_value = trader.portfolio.value(quotes)

    assert portfolio_value == total_for_cash + total_for_shares


def test_portfolio_calculate_unrealized_pl_loss(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 1
    SYMBOL = "AAPL"
    last = AVG_PRICE - 1
    ts = datetime.now()

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY,
                                                  AVG_PRICE)

    quotes = {SYMBOL: MarketQuote(symbol=SYMBOL, bid_price=None, bid_size=0,
                                  ask_price=None, ask_size=0, last_price=last,
                                  timestamp=ts)}

    quote = quotes[SYMBOL]
    assert quote and quote.last_price

    pl = trader.portfolio.calculate_unrealized_pl(SYMBOL, quotes)
    loss = -(1 * POSITION_QTY)

    assert pl == loss


def test_portfolio_calculate_unrealized_pl_profit(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 1
    SYMBOL = "AAPL"
    last = AVG_PRICE + 1
    ts = datetime.now()

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY,
                                                  AVG_PRICE)

    quotes = {SYMBOL: MarketQuote(symbol=SYMBOL, bid_price=None, bid_size=0,
                                  ask_price=None, ask_size=0, last_price=last,
                                  timestamp=ts)}

    quote = quotes[SYMBOL]
    assert quote and quote.last_price

    pl = trader.portfolio.calculate_unrealized_pl(SYMBOL, quotes)
    profit = (1 * POSITION_QTY)

    assert pl == profit


def test_portfolio_calculate_pl_unknown_ticket(test_context: AppContext):
    AVG_PRICE = 150.00
    POSITION_QTY = 50
    SYMBOL = "AAPL"

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[SYMBOL] = Position(SYMBOL, POSITION_QTY,
                                                  AVG_PRICE)

    quotes = test_context.exchange.quotes

    try:
        trader.portfolio.calculate_unrealized_pl(SYMBOL, quotes)
        assert False
    except ValueError:
        assert True
