from fastapi import FastAPI
from .routers import funds, navs
from .database import engine
from .models import Base
import asyncio

app = FastAPI(title="Mutual Funds API")

app.include_router(funds.router)
app.include_router(navs.router)

# Optional: create tables on startup (for dev only)
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
