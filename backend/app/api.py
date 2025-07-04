from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from typing import Dict, Optional, Literal

from logging_config import setup_logger

from engine.stock import Stock
from engine.exchange import Exchange
from engine.trader import Trader
from engine.order import Order
from engine.position import Position

from app.session import Session
from app.context import AppContext


class LoginRequest(BaseModel):
    trader_id: int


class OrderRequest(BaseModel):
    order_type: Literal["buy", "sell"]
    symbol: str
    quantity: int
    price: float


app = FastAPI(title="York Stock Exchange")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # my front-end origin
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # or ["*"]
    allow_headers=["*"],
)

MARKET_DATA: Dict[str, Stock] = {
    "AAPL": Stock("AAPL", 150.00),
    "MSFT": Stock("MSFT", 295.50),
    "GOOG": Stock("GOOG", 2830.75),
    "AMZN": Stock("AMZN", 3505.20),
    "TSLA": Stock("TSLA", 720.25),
    "NFLX": Stock("NFLX", 505.60),
    "FB": Stock("FB", 355.45),
}

logger = setup_logger()
exchange: Exchange = Exchange(MARKET_DATA)
trader = Trader(trader_id=1, starting_balance=1000000)
trader2 = Trader(trader_id=42, starting_balance=1000000)

trader2.portfolio._positions["AAPL"] = Position(999, 150.0)
order = trader2.place_order("AAPL", "sell", 999, 150)
exchange.add_order(order)
exchange.register_trader(trader)
exchange.register_trader(trader2)

session: Session = Session(exchange.traders)

app_context = AppContext(session, exchange, logger)

# ——— HTTP Endpoints ———


@app.post("/login")
def login(data: LoginRequest):
    trader_id = data.trader_id

    id = int(trader_id)

    try:
        session.login(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "logged_in", "trader": id}


@app.post("/logout")
def logout():
    try:
        session.logout()
    except RuntimeError as e:
        raise HTTPException(status_code=204, detail=str(e))
    return {"status": "logged_out"}


@app.post("/next_tick")
def next_tick():
    exchange.process_tick()
    return exchange.market_data


@app.post("/order")
def place_order(data: OrderRequest):

    order_type, symbol, quantity, price = (
        data.order_type,
        data.symbol,
        data.quantity,
        data.price,
    )

    try:
        trader = app_context.session.require_active()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    try:
        app_context.exchange.verify_symbol(symbol)
        order = trader.place_order(symbol, order_type, quantity, price)
        app_context.exchange.add_order(order)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "order_placed", "order_id": order.order_id}


@app.get("/match-orders")
def match_orders():
    order_books = app_context.exchange.order_books

    if len(order_books) == 0:
        return

    for symbol in order_books:
        app_context.exchange.match_orders(symbol)

    return


@app.get("/portfolio")
def portfolio():
    try:
        trader = session.require_active()
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    safe: dict = jsonable_encoder(trader.portfolio)

    return safe


@app.get("/me")
def me():
    if not session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return {"trader_id": session.active_trader.trader_id}


@app.get("/me/portfolio")
def me_portfolio():
    if not session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    trader_id = session.active_trader.trader_id

    trader = exchange.traders.get(trader_id, None)

    if not trader:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Trader not found")

    return {
        "portfolio": {
            "positions": trader.portfolio.positions,
            "cash": trader.portfolio.cash,
            "value": trader.portfolio.value(app_context.exchange.market_data),
        }
    }


@app.get("/me/pending-orders")
def me_pending_orders():
    if not session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    orders = session.active_trader.pending_orders

    return jsonable_encoder(orders)


@app.get("/market-data")
def market_data():
    return {"market_data": app_context.exchange.market_data}


@app.get("/market-data/next")
def market_data_next():

    app_context.exchange.process_tick()

    return market_data()


# ——— WebSocket for real-time ticks ———
async def market_ws(ws: WebSocket):
    await ws.accept()
    while True:
        exchange.process_tick()
        await ws.send_json(exchange.market_data.dict())
