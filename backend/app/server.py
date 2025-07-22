import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scripts.bootstrap import bootstrap          
from app.api import router            


async def lifespan(app: FastAPI):
    # runs before the server starts accepting requests
    app.state.context = await bootstrap()
    yield
    # optional: cleanup on shutdown

app = FastAPI(title="GhostSwap API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
