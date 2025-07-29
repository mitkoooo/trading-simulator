from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from scripts.bootstrap import bootstrap

app = FastAPI(title="GhostSwap API")


@app.on_event("startup")
async def on_startup():
    ctx = await bootstrap()
    app.state.context = ctx


@app.on_event("shutdown")
async def on_shutdown():
    await app.state.context.exchange.stop()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
