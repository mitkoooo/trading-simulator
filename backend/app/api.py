from app.context import AppContext
from engine.order_book.order import Order
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, WebSocket, status, Depends, Request
from fastapi.encoders import jsonable_encoder
from typing import Literal

class LoginRequest(BaseModel):
    trader_id: int


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

    print(id)

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


@router.post("/next_tick")
def next_tick(ctx: AppContext = Depends(get_ctx)):
    exchange = ctx.exchange
    exchange.process_tick()

    return exchange.market_data


@router.post("/order")
def place_order(data: OrderRequest, ctx: AppContext = Depends(get_ctx)):

    order_type, symbol, quantity, price = (
        data.order_type,
        data.symbol,
        data.quantity,
        data.price,
    )

    try:
        trader = ctx.session.require_active()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    try:
        exchange = ctx.exchange
        broker = ctx.broker

        exchange.verify_symbol(symbol)
        order = Order(trader.trader_id, symbol, order_type, quantity, price)
        
        broker.submit_order(order)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "order_placed", "order_id": order.order_id}

@router.post("/order/cancel")
def order_cancel(data: OrderCancelRequest, ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=401, detail="Not authenticated"
        )

    order_id = data.order_id
    broker = ctx.broker

    try:
        broker.cancel_order(order_id)
    except (KeyError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "order_cancelled", "order_id": order_id}

@router.get("/match-orders")
def match_orders(ctx: AppContext = Depends(get_ctx)):
    order_books = ctx.exchange.order_books

    for symbol in order_books:
        while True:
            trade = ctx.exchange.match_orders(symbol)
            print(trade) 
            if not trade:
                break

    return


@router.get("/me")
def me(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return {"trader_id": ctx.session.active_trader.trader_id}


@router.get("/me/portfolio")
def me_portfolio(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    trader = ctx.session.active_trader
    market_data = ctx.exchange.market_data

    total_PnL = 0

    for symbol in trader.portfolio.positions:
        total_PnL += trader.portfolio.calculate_unrealized_pl(symbol, market_data)

    return {
        "positions": list(trader.portfolio.positions.values()),
        "cash": trader.portfolio.cash,
        "value": trader.portfolio.value(ctx.exchange.market_data),
        "totalPnL": total_PnL,
    }


@router.get("/me/pending-orders")
def me_pending_orders(ctx: AppContext = Depends(get_ctx)):
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    orders = list(ctx.session.active_trader.pending_orders.values())

    return jsonable_encoder(orders)


@router.get("/market-data")
def market_data(ctx: AppContext = Depends(get_ctx)):
    return {"market_data": ctx.exchange.market_data}


@router.get("/market-data/next")
def market_data_next(ctx: AppContext = Depends(get_ctx)):

    ctx.exchange.process_tick()

    return {"market_data": ctx.exchange.market_data}


# ——— WebSocket for real-time ticks ———
async def market_ws(ws: WebSocket, ctx: AppContext = Depends(get_ctx)):
    await ws.accept()
    while True:
        ctx.exchange.process_tick()
        await ws.send_json(ctx.exchange.market_data)
