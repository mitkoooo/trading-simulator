from datetime import datetime

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.dependencies import ContextDep
from engine.market_data.quote import MarketQuote


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

    """

    symbol: str
    bid_price: float | None
    bid_size: int | None
    ask_price: float | None
    ask_size: int | None
    last_price: float | None
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

router = APIRouter(prefix="/v1/quotes", tags=["core"])


# ——— HTTP Endpoints ———

@router.get("/")
def quotes(ctx: ContextDep) -> GetQuotesResponse:
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

    for i, q in enumerate(quotes):
        quotes[i] = QuoteDTO(symbol = q.symbol,
                             bid_price = q.bid_price,
                             bid_size = q.bid_size,
                             ask_price = q.ask_price,
                             ask_size = q.ask_size,
                             last_price= q.last_price,
                             timestamp=q.timestamp,
                )

    res = GetQuotesResponse(status=status.HTTP_200_OK,
                            quotes=quotes)

    return res 
