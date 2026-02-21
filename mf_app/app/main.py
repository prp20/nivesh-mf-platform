from fastapi import FastAPI
from .routers import funds, navs, metrics, benchmarks, benchmark_navs
from .database import engine
from .models import Base
from sqlalchemy import text
import asyncio

app = FastAPI(
    title="Mutual Funds Analysis API",
    description="API for managing mutual fund data, NAV history, benchmarks, and performance metrics",
    version="1.0.0"
)

# Include all routers
app.include_router(funds.router)
app.include_router(metrics.router)
app.include_router(navs.router)
app.include_router(benchmarks.router)
app.include_router(benchmark_navs.router)

# Create tables on startup only if they don't exist
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        # Only create tables if they don't already exist
        await conn.run_sync(Base.metadata.create_all)


@app.get("/", tags=["root"])
async def root():
    """Health check endpoint"""
    return {
        "message": "Mutual Funds Analysis API",
        "status": "running",
        "documentation": "/docs"
    }

