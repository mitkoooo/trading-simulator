from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, WebSocket, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from typing import Dict, Literal

from logging_config import setup_logger

from engine.stock import Stock
from engine.exchange import Exchange
from engine.trader import Trader
from engine.position import Position
from engine.broker.broker import Broker

from app.session import Session
from app.context import AppContext


class LoginRequest(BaseModel):
    trader_id: int


class OrderRequest(BaseModel):
    order_type: Literal["buy", "sell"]
    symbol: str
    quantity: int
    price: float

class OrderCancelRequest(BaseModel):
    order_id: str


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
    "NVDA": Stock("NVDA", 670.15),
    "INTC": Stock("INTC", 42.30),
}

logger = setup_logger()
exchange: Exchange = Exchange(MARKET_DATA)
broker: Broker = Broker(exchange)

trader = Trader(trader_id=1, starting_balance=1000000)
trader2 = Trader(trader_id=42, starting_balance=1000000)
broker.register_trader(trader)
broker.register_trader(trader2)

trader2.portfolio.positions["AAPL"] = Position("AAPL", 999, 150.0)
order = trader2.create_order("AAPL", "sell", 999, 150)
broker.submit_order(order)

session: Session = Session(broker.traders)

app_context = AppContext(session, broker, exchange, logger)

# ——— HTTP Endpoints ———


@app.post("/login")
def login(data: LoginRequest):
    trader_id = data.trader_id

    id = int(trader_id)

    try:
        app_context.session.login(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"status": "logged_in", "trader": id}


@app.post("/logout")
def logout():
    try:
        app_context.session.logout()
    except RuntimeError as e:
        raise HTTPException(status_code=204, detail=str(e))
    return {"status": "logged_out"}


@app.post("/next_tick")
def next_tick():
    exchange = app_context.exchange
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
        exchange = app_context.exchange
        broker = app_context.broker

        exchange.verify_symbol(symbol)
        order = trader.create_order(symbol, order_type, quantity, price)
        
        broker.submit_order(order)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"status": "order_placed", "order_id": order.order_id}

@app.post("/order/cancel")
def order_cancel(data: OrderCancelRequest):
    if not app_context.session.active_trader:
        raise HTTPException(
            status_code=401, detail="Not authenticated"
        )

    order_id = data.order_id

    try:
        status = broker.cancel_order(order_id)
        if not status:
            raise RuntimeError("Unable to delete the order")

    except (KeyError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {"status": "order_cancelled", "order_id": order_id}

@app.get("/match-orders")
def match_orders():
    order_books = app_context.exchange.order_books

    for symbol in order_books:
        while True:
            trade = app_context.exchange.match_orders(symbol)
            
            if not trade:
                break
            app_context.broker.settle_trade(trade) 

    return


@app.get("/me")
def me():
    if not app_context.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return {"trader_id": session.active_trader.trader_id}


@app.get("/me/portfolio")
def me_portfolio():
    if not app_context.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    trader = app_context.session.active_trader

    total_PnL = 0

    for symbol in trader.portfolio.positions:
        total_PnL += trader.portfolio.calculate_unrealized_pl(symbol, MARKET_DATA)

    return {
        "positions": list(trader.portfolio.positions.values()),
        "cash": trader.portfolio.cash,
        "value": trader.portfolio.value(app_context.exchange.market_data),
        "totalPnL": total_PnL,
    }


@app.get("/me/pending-orders")
def me_pending_orders():
    if not app_context.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    orders = list(app_context.session.active_trader.pending_orders.values())

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
        app_context.exchange.process_tick()
        await ws.send_json(exchange.market_data)
