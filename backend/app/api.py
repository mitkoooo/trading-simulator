from datetime import datetime
from typing import List, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from app.context import AppContext


class LoginRequest(BaseModel):
    trader_id: int


class QuoteSchema(BaseModel):
    symbol: str
    bid_price: float | None
    bid_size: int | None
    ask_price: float | None
    ask_size: int | None
    last: float | None
    timestamp: datetime


class OrderRequest(BaseModel):
    order_type: Literal["buy", "sell"]
    symbol: str
    quantity: int
    price: float | None


class OrderCancelRequest(BaseModel):
    order_id: str


router = APIRouter(prefix="/v1", tags=["core"])


# ---- Dependency to pull your context/service off the FastAPI app ----
def get_ctx(request: Request) -> AppContext:
    return request.app.state.context


# ——— HTTP Endpoints ———


@router.post("/login")
def login(data: LoginRequest, ctx: AppContext = Depends(get_ctx)):
    trader_id = data.trader_id

    id = str(trader_id)

    try:
        ctx.session.login(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "logged_in", "trader": id}


@router.post("/logout")
def logout(ctx: AppContext = Depends(get_ctx)):
    try:
        ctx.session.logout()
    except RuntimeError as e:
        raise HTTPException(status_code=204, detail=str(e))
    return {"status": "logged_out"}


@router.post("/order")
async def place_order(data: OrderRequest, ctx: AppContext = Depends(get_ctx)):
    order_type, symbol, quantity, price = (
        data.order_type,
        data.symbol,
        data.quantity,
        data.price,
    )

    try:
        trader = ctx.session.require_active()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        )

    try:
        exchange = ctx.exchange
        broker = ctx.broker

        exchange.verify_symbol(symbol)

        order = await broker.submit_order(
            trader.trader_id, symbol, order_type, quantity, price
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "order_placed", "order_id": order.order_id}


@router.post("/order/cancel")
async def order_cancel(
    data: OrderCancelRequest, ctx: AppContext = Depends(get_ctx)
):
    if not ctx.session.active_trader:
        raise HTTPException(status_code=401, detail="Not authenticated")

    order_id = data.order_id
    broker = ctx.broker

    try:
        await broker.cancel_order(order_id)
    except (KeyError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "order_cancelled", "order_id": order_id}


@router.get("/me")
def me(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return {"trader_id": ctx.session.active_trader.trader_id}


@router.get("/me/portfolio")
def me_portfolio(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    trader = ctx.session.active_trader
    quotes = ctx.exchange.quotes

    total_PnL = 0

    for symbol in trader.portfolio.positions:
        unrealized_pnl = trader.portfolio.calculate_unrealized_pl(
            symbol, quotes
        )
        if unrealized_pnl:
            total_PnL += unrealized_pnl

    return {
        "positions": list(trader.portfolio.positions.values()),
        "cash": trader.portfolio.cash,
        "value": trader.portfolio.value(ctx.exchange.quotes),
        "totalPnL": total_PnL,
    }


@router.get("/me/pending-orders")
def me_pending_orders(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    orders = list(ctx.session.active_trader.pending_orders.values())

    return jsonable_encoder(orders)


@router.get("/quotes", response_model=List[QuoteSchema])
def market_data(ctx: AppContext = Depends(get_ctx)):
    quotes = ctx.exchange.quotes

    print(list(ctx.session.active_trader.pending_orders.values()))
    print(f"ORDER BOOK QUEUE IS {ctx.exchange._book_queues['AAPL'].qsize()}")
    print(f"ORDER BOOK {ctx.exchange.order_books['AAPL']}")

    return [
        QuoteSchema(
            symbol=q.symbol,
            bid_price=q.bid_price,
            bid_size=q.bid_size,
            ask_price=q.ask_price,
            ask_size=q.ask_size,
            last=q.last_price,
            timestamp=q.timestamp,
        )
        for q in quotes.values()
    ]
