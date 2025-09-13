from datetime import datetime

from app.context import AppContext
from engine.market_data.quote import MarketQuote
from engine.position import Position


def test_portfolio_value_pure_cash(test_context: AppContext):
    trader = test_context.session.active_trader
    assert trader

    exchange = test_context.exchange

    total_cash = trader.portfolio.cash + trader.portfolio.reserved_cash
    portfolio_value = trader.portfolio.value(exchange.quotes)

    assert portfolio_value == total_cash


def test_portfolio_value_combined(test_context: AppContext):
    symbol = "AAPL"
    share_num = 50
    ts = datetime.now()

    quotes = {
        symbol: MarketQuote(
            symbol,
            bid_price=None,
            bid_size=0,
            ask_price=None,
            ask_size=0,
            last_price=100,
            daily_vol=None,
            timestamp=ts,
        )
    }

    quote = quotes[symbol]
    assert quote and quote.last_price

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[symbol] = Position(symbol, share_num)

    total_for_cash = trader.portfolio.cash + trader.portfolio.reserved_cash
    total_for_shares = quote.last_price * share_num
    portfolio_value = trader.portfolio.value(quotes)

    assert portfolio_value == total_for_cash + total_for_shares


def test_portfolio_calculate_unrealized_pl_loss(test_context: AppContext):
    avg_price = 150.00
    position_qty = 1
    symbol = "AAPL"
    last = avg_price - 1
    ts = datetime.now()

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[symbol] = Position(
        symbol, position_qty, avg_price
    )

    quotes = {
        symbol: MarketQuote(
            symbol=symbol,
            bid_price=None,
            bid_size=0,
            ask_price=None,
            ask_size=0,
            last_price=last,
            daily_vol=None,
            timestamp=ts,
        )
    }

    quote = quotes[symbol]
    assert quote and quote.last_price

    pl = trader.portfolio.calculate_unrealized_pl(symbol, quotes)
    loss = -(1 * position_qty)

    assert pl == loss


def test_portfolio_calculate_unrealized_pl_profit(test_context: AppContext):
    avg_price = 150.00
    position_qty = 1
    symbol = "AAPL"
    last = avg_price + 1
    ts = datetime.now()

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[symbol] = Position(
        symbol, position_qty, avg_price
    )

    quotes = {
        symbol: MarketQuote(
            symbol=symbol,
            bid_price=None,
            bid_size=0,
            ask_price=None,
            ask_size=0,
            last_price=last,
            daily_vol=None,
            timestamp=ts,
        )
    }

    quote = quotes[symbol]
    assert quote and quote.last_price

    pl = trader.portfolio.calculate_unrealized_pl(symbol, quotes)
    profit = 1 * position_qty

    assert pl == profit


def test_portfolio_calculate_pl_unknown_ticker(test_context: AppContext):
    avg_price = 150.00
    position_qty = 50
    symbol = "AAPL"

    trader = test_context.session.active_trader
    assert trader
    trader.portfolio.positions[symbol] = Position(
        symbol, position_qty, avg_price
    )

    quotes = test_context.exchange.quotes

    try:
        trader.portfolio.calculate_unrealized_pl(symbol, quotes)
        raise AssertionError("Should not calculate P&L for unknown ticker")
    except ValueError:
        assert True
