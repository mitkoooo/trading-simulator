from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.dependencies import ContextDep
from engine.broker.broker import Broker
from engine.order_book.order import Order
from engine.trader import Trader


class CreateOrderRequest(BaseModel):
    """Schema for creating new order data request.

    Attributes:
        order_type (Literal["buy", "sell"]):
            buy or sell. 

        symbol (str):
            A ticker symbol (e.g. AAPL or MSFT)

        quantity (int):
            Quantity of shares to acquire.

        limit_price (float | None):
            Limit price for limit orders, if market it is None.

    """

    order_type: Literal["buy", "sell"]
    symbol: str
    quantity: int
    limit_price: float | None

class CreateOrderResponse(BaseModel):
    """Schema for creating new order data response.

    Attributes:
        status (int):
            Outcome status of the creation order operation, e.g., 200 (ok).

        order_status (str):
            Status of the order (e.g. pending, partially filled or filled).

        order_id (str):
            Echoed order unique identifier.

    """

    status: int
    order_status: str
    order_id: str

class CancelOrderResponse(BaseModel):
    """Schema for order cancellation response.

    Attributes:
        status (int):
            Outcome status of the cancellation order operation, e.g., 200 (ok)
        
        order_status (str):
            Status of the order (e.g. cancelled)

        order_id (str):
            Echoed order unique identifier.

    """

router = APIRouter(prefix="/v1/orders") 

@router.post("/")
async def create_order(data: CreateOrderRequest,
                       ctx: ContextDep) -> CreateOrderResponse:
    """Place a new order for the authenticated trader.

    Args:
        data (CreateOrderRequest):  
            Payload containing order_type, symbol, quantity, and limit_price.

        ctx (ContextDep):  
            Dependency providing session, exchange, and broker contexts.

    Raises:
        HTTPException 401:  
            If the user is not logged in.

        HTTPException 404:  
            If the symbol is not registered or submission fails.

    """
    print(data)

    order_type, symbol, quantity, limit_price = (
        data.order_type,
        data.symbol,
        data.quantity,
        data.limit_price,
    )
    
    # Check if user logged in.
    try:
        trader = ctx.session.require_active()
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e

    try:
        exchange = ctx.exchange
        broker = ctx.broker

        if symbol not in exchange.instruments:
            msg = "This ticker symbol is not registered on the exchange."
            raise KeyError(msg)
        
        # Place order via broker.

        order: Order = await broker.submit_order(
            trader.trader_id, symbol, order_type, quantity, limit_price
        )
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    order_status = order.status
    order_id = order.order_id

    res = CreateOrderResponse(status=status.HTTP_200_OK,
                              order_status=order_status, order_id=order_id)
    
    print(res)

    return res 


@router.delete("/{order_id}")
async def cancel_order(order_id: str, ctx: ContextDep) -> CancelOrderResponse:
    """Cancel an existing order by its ID for the authenticated trader.

    Ensures an active session, then delegates cancellation to the broker.

    Args:
        order_id (str):  
            Identifier of the order to cancel.

        ctx (ContextDep):  
            Dependency providing session and broker contexts.

    Raises:
        HTTPException 401:  
            If the user is not logged in.

        HTTPException 404:  
            If the order is not found or cancellation fails.

    """
    if not ctx.session.active_trader:
        raise HTTPException(status_code=401, detail="Not authenticated")

    trader: Trader = ctx.session.active_trader
    broker: Broker = ctx.broker

    if broker.active_orders.get(order_id) != trader.trader_id:
        msg = "Cannot delete other trader's order."
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=msg)

    try:
        order: Order = await broker.cancel_order(order_id)
    except (KeyError, RuntimeError) as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    order_status = order.status
    order_id = order.order_id

    res = CancelOrderResponse(status = status.HTTP_200_OK,
                              order_status = order_status,
                              order_id = order_id)

    return res 

