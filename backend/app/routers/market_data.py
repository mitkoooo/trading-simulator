from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from starlette.status import HTTP_404_NOT_FOUND

from app.dependencies import ContextDep, SummaryDep, fetch_daily_summary
from engine.market_data.quote import MarketQuote
from services.daily_summary import DailySummary


class QuoteDTO(BaseModel):
    """Schema for `MarketQuote`.

    Attributes:
        symbol (str):
            A ticker symbol (eg. AAPL or MSFT).

        bid_price (float or None):
            Currently highest bid price.

        bid_size (int or None):
            Current number of bid orders in order book.

        ask_price (float or None):
            Currently lowest ask price.

        ask_size (int or None):
            Current number of ask orders in order book.

        last_price (float or None):
            Latest price at which a stock or a commodity was traded.

        daily_vol (int or None):
            Current daily volume of shares traded so far.

    """

    symbol: str
    bid_price: float | None
    bid_size: int | None
    ask_price: float | None
    ask_size: int | None
    last_price: float | None
    daily_vol: int | None
    timestamp: datetime


class GetQuotesResponse(BaseModel):
    """Schema for get quotes response.

    Attributes:
        status (int):
            Outcome status of the operation, e.g., 200 (ok).
        quotes (list[QuoteDTO]):
            List of latest market quotes for each instrument.

    """

    status: int
    quotes: list[QuoteDTO]



class GetBulkSummaries(BaseModel):
    summaries: list[DailySummary]

router = APIRouter(prefix="/v1/market-data", tags=["core"])


# ——— HTTP Endpoints ———

@router.get("/quotes/{symbol:^[A-Z]+$}")
def get_quote(ctx: ContextDep, symbol: str):
    if symbol not in ctx.exchange.instruments:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND,
                            detail="Symbol not found.")

    quote = ctx.exchange.quotes[symbol]

    return QuoteDTO(symbol = quote.symbol,
                    bid_price = quote.bid_price,
                    bid_size = quote.bid_size,
                    ask_price = quote.ask_price,
                    ask_size = quote.ask_size,
                    last_price = quote.last_price,
                    daily_vol=quote.daily_vol,
                    timestamp = quote.timestamp)


@router.get("/quotes")
def get_quotes(ctx: ContextDep) -> GetQuotesResponse:
    """Fetch latest market quotes for all registered instruments.

    Args:
        ctx (ContextDep):
            Application context.

    Returns:
        (GetQuotesResponse):
            Pydantic model describing the returned object.
            (See GetQuotesResponse docstring)

    """
    quotes: list[MarketQuote] = list(ctx.exchange.quotes.values())

    quotes_res: list[QuoteDTO] = []

    for q in quotes:
        quotes_res.append(QuoteDTO(symbol = q.symbol,
                             bid_price = q.bid_price,
                             bid_size = q.bid_size,
                             ask_price = q.ask_price,
                             ask_size = q.ask_size,
                             last_price= q.last_price,
                             daily_vol= q.daily_vol,
                             timestamp=q.timestamp)
                          )

    res = GetQuotesResponse(status=status.HTTP_200_OK,
                            quotes=quotes_res)

    return res

@router.get("/daily-summary/{symbol:^[A-Z]+$}")
def get_daily_summary(symbol:str, daily_summary: SummaryDep):
    if summary is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,
                            detail="Unknown ticker symbol")

@router.get("/daily-summary/bulk")
def get_daily_summaries(ctx: ContextDep):

    exchange = ctx.exchange

    summaries = []


    for instrument in exchange.instruments:
        summary = fetch_daily_summary(instrument)
        summaries.append(summary)


    return GetBulkSummaries(summaries=summaries)

    
   
