from datetime import datetime
from typing import Literal

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.dependencies import ContextDep, OrderStatusDep
from engine.order_book.order import Order
from engine.order_info import OrderInfo
from engine.position import Position
from engine.trader import Trader


class OrderDTO(BaseModel):
    """Schem for order to buy or sell shares on the exchange.

    Attributes:
        mpid (str):
            ID of market participant owning `Order`.
        symbol (str):
            Stock ticker (e.g. "AAPL").
        order_type (Literal["buy", "sell"]):
            Direction of the order.
        status Literal["pending", "partially_filled", "filled", "cancelled"]:
            Status of the order.
        quantity (int):
            Number of shares; must be > 0.
        limit_price (float or None):
            Limit price; None for market orders.
        order_id (str):
            Unique ID, auto-generated if omitted.
        timestamp (datetime):
            Creation time of the order.

    """

    mpid: str
    symbol: str
    order_type: Literal["buy", "sell"]
    status: Literal["pending", "partially_filled", "filled", "cancelled"]
    quantity: int
    limit_price: float | None
    order_id: str
    timestamp: datetime

class OrderInfoDTO(BaseModel):
    mpid: str
    symbol: str
    order_type: Literal["buy", "sell"]
    status: Literal["pending", "partially_filled", "filled", "cancelled"]
    fill_qty: int
    avg_fill_price: float | None
    order_id: str
    timestamp: datetime



class LoginRequest(BaseModel):
    """Schema for login request data.

    Attributes:
        trader_id (str):
            Unique identifier for the trader.

    """

    trader_id: str

class LoginResponse(BaseModel):
    """Schema for login response data.

    Attributes:
        status (int):
            Outcome status of the login operation, e.g., 200 (ok).
        trader_id (str):
            Echoed trader identifier upon successful login.

    """

    status: int
    trader_id: str

class LogoutResponse(BaseModel):
    """Schema for logout response data.
    
    Attributes:
        status (int):
            Outcome status of the logout operation, e.g., 200 (ok).

    """

    status: int

class MeResponse(BaseModel):
    """Schema for me response data.

    Attributes:
        status (int):
            Outcome status of the `me` operation, e.g., 200 (ok).

        trader_id (str):
            Echoed trader indentifier.
    
    """

    status: int
    trader_id: str

class GetOrdersResponse(BaseModel):
    """Schema for get order response data.

    Attributes:
        status (int):
            Outcome status of the operation, e.g. 200 (ok).

        orders (list[OrderDTO]):
            List of queried orders.

    """

    status: int
    orders: list[OrderDTO]

class GetPortfolioResponse(BaseModel):
    """Schema for get portfolio response data.

    Attributes:
        status (int):
            Outcome status of the operation, e.g., 200 (ok)

        positions (list[PositionDTO]):
            List of trader's all positions.

        cash (float):
            Trader's cash balance.

        value (float):
            Total evaluation of trader's portfolio.

        realized_pnl (float):
            Trader's total realized P&L.

    """
    
    status: int
    positions: list[Position]
    cash: float
    value: float
    realized_pnl: float

class GetHistoryResponse(BaseModel):
    history: list[OrderInfoDTO]

router = APIRouter(prefix="/v1/users", tags=["users"])

@router.post("/login")
def login(data: LoginRequest, ctx: ContextDep) -> LoginResponse:
    """Authenticate a trader and establish a session.

    This endpoint accepts a trader's credentials and attempts to
    log them into the system via the provided ContextDep session.

    Args:
        data (LoginRequest):
            Pydantic model containing the trader ID.

        ctx (ContextDep):
            Injected dependency managing session context.

    Returns:
        LoginResponse:
            Pydantic model confirming successful login.

    Raises:
        HTTPException:
            If fails, returns status code 400 with message.

    """
    trader_id = data.trader_id

    id = str(trader_id)

    try:
        ctx.session.login(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    res = LoginResponse(status=status.HTTP_200_OK, trader_id=id)

    return res

@router.post("/logout")
def logout(ctx: ContextDep) -> LogoutResponse:
    """Terminate the current trader session.

    This endpoint logs out the active trader by invoking the
    logout method on the session context.

    Args:
        ctx (ContextDep):
            Injected dependency managing session context.

    Returns:
        LogoutResponse:
            HTTP status code indicating successful logout.

    Raises:
        HTTPException: If fails, returns status code 400
            with error message.

    """
    try:
        ctx.session.logout()
    except RuntimeError as e:
        raise HTTPException(status_code=204, detail=str(e)) from e

    res = LogoutResponse(status = status.HTTP_200_OK)

    return res

@router.get("/me")
def me(ctx: ContextDep) -> MeResponse:
    """Retrieve the currently logged-in trader's information.

    This endpoint checks if a trader session is active and returns
    the trader's ID if authenticated.

    Args:
        ctx (ContextDep):
            Injected dependency managing session context.

    Returns:
        MeResponse:
            Model containing the trader ID.

    Raises:
        HTTPException:
            If no active session, returns 401 Unauthorized.

    """
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    tid = ctx.session.active_trader.trader_id

    return MeResponse(status = status.HTTP_200_OK, trader_id = tid) 

@router.get("/{trader_id}/orders/history")
def get_order_history(trader_id: str, ctx: ContextDep) -> GetHistoryResponse:
    if not ctx.session.active_trader:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

    trader = ctx.session.active_trader

    if trader_id not in ctx.session.traders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trader id not found."
            )

    if trader_id != trader.trader_id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this trader's orders."
            )

    order_history: list[OrderInfo] = list(trader.transaction_log.values())

    history = list()

    for o_info in order_history:
        history.append(OrderInfoDTO(mpid=o_info.mpid,
                                order_type=o_info.order_type,
                                symbol=o_info.symbol,
                                status=o_info.status,
                                fill_qty=o_info.fill_qty,
                                avg_fill_price=o_info.avg_fill_price,
                                order_id=o_info.order_id,
                                timestamp=o_info.timestamp,
                                ))
    return GetHistoryResponse(history=history)


@router.get("/{trader_id}/orders")
def get_trader_orders(trader_id: str, order_status: OrderStatusDep,
                         ctx: ContextDep) -> GetOrdersResponse:
    """Retrieve pending orders for the given user.

    Args:
        trader_id (str):
            Identifier of the trader whose orders to fetch.

        order_status (OrderStatusDep):
            Injected dependency managing order status.

        ctx (ContextDep):
            Injected dependency managing session context.

    Returns:
        GetOrdersResponse: List of that user's pending orders.

    Raises:
        HTTPException 401:
            If the caller is not authenticated.

        HTTPException 403:
            If the caller isn't allowed to view this user's data.

        HTTPException 404:
            If the trader_id doesn't exist.

    """
    order_status_list = ["pending", "filled", "partially_filled", "cancelled"]

    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    if trader_id not in ctx.session.traders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader id not found."
        )

    if order_status and order_status not in order_status_list:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order status not found."
            )

    trader: Trader = ctx.session.active_trader

    if trader_id != trader.trader_id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this trader's orders."
            )

    if order_status == "pending":
        orders: dict[str, Order] = trader.pending_orders
        orders_filtered = orders.values()
    else:
        orders: dict[str, Order] = trader.transaction_log

        if order_status:
            orders_filtered = [o for o in orders.values() if
                               o.status == order_status]
        else:
            orders_filtered = orders.values()
    
    orders_res: list[OrderDTO] = []

    for o in orders_filtered:
        orders_res.append(OrderDTO(mpid=o.mpid, symbol=o.symbol,
                                   order_type=o.order_type, status=o.status,
                                   quantity=o.quantity,
                                   limit_price=o.limit_price,
                                   order_id=o.order_id, timestamp=o.timestamp))

    res = GetOrdersResponse(status=status.HTTP_200_OK,
                            orders=orders_res)
    return res

@router.get("/{trader_id}/portfolio")
def get_trader_portfolio(trader_id: str,
                         ctx: ContextDep) -> GetPortfolioResponse:
    """Retrieve a trader's portfolio.

    Args:
        trader_id (str):
            Identifier of the trader whose portfolio is requested.
        ctx (ContextDep):
            Dependency providing the current session and exchange contexts.

    Raises:
        (HTTPException):
            Code 401, there is no active session (user not authenticated).

        (HTTPException):
            Code 404, the given trader_id does not exist.

        (HTTPException):
            Code 403, the user attempts to view another trader's portfolio.

    Returns:
        (GetPortfolioResponse):
            Pydantic BaseModel. (See GetPortfolioResponse)

    """
    if not ctx.session.active_trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    trader = ctx.session.active_trader

    if trader_id not in ctx.session.traders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader id not found."
        )

    if trader_id != trader.trader_id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to view this trader's portfolio."
            )


    positions = list(trader.portfolio.positions.values())
    cash = trader.portfolio.cash
    value = trader.portfolio.value(ctx.exchange.quotes)
    realized_pnl = trader.portfolio.realized_pnl
    
    res = GetPortfolioResponse(status=status.HTTP_200_OK,
                               positions=positions,
                               cash=cash,
                               value=value,
                               realized_pnl=realized_pnl)

    return res 

        



