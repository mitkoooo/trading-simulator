from engine.exchange import Exchange
from engine.trader import Trader


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
