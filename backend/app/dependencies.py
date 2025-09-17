# ---- Dependency to pull your context/service off the FastAPI app ----
from datetime import date
from typing import Annotated, Literal

from fastapi import Depends, Query, Request

from app.context import AppContext
from services.daily_summary import DailySummary, get_daily_summary


def get_ctx(request: Request) -> AppContext:
    """Get Application context as route dependency.

    Args:
        request (Request):
            Raw request object.
            
    """
    return request.app.state.context

ContextDep = Annotated[AppContext, Depends(get_ctx)]

def order_status(
    status: Literal["pending",
                    "filled",
                    "partially_filled",
                    "cancelled"
                    ] = Query(
                        None,
        description="Filter orders by status",
    )
) -> str:
        """Dependency that validates and returns the `status` query-param."""
        return status

OrderStatusDep = Annotated[Literal["pending", "filled", "partially_filled",
                                    "cancelled"], Depends(order_status)]


def fetch_daily_summary(symbol: str) -> DailySummary | None:
    """Retrieve daily summary as a route dependency."""
    day = date(2025, 8, 5)
    summary = get_daily_summary(symbol, for_date=day)
    print(summary)
    return summary

SummaryDep = Annotated[str, Depends(fetch_daily_summary)]
