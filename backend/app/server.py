
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.market_data import router as market_data_router
from app.routers.orders import router as orders_router
from app.routers.users import router as users_router
from scripts.bootstrap import bootstrap


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Manage FastAPI application startup and shutdown.

    Before the server starts, perform any necessary initialization.
    After the server stops, perform any cleanup or teardown tasks.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None: Control is yielded back to FastAPI to run the application.

    """
    ctx = await bootstrap()
    app.state.context = ctx

    try:
        yield
    finally:
        pass

app = FastAPI(title="GhostSwap API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routers = [market_data_router, users_router, orders_router]

for r in routers:
    app.include_router(r)
