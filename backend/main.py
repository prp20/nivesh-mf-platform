from fastapi import FastAPI
from backend.models import Base  # noqa: F401

from backend.core.config import settings
from backend.api.funds import router as funds_router

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# Routers
app.include_router(funds_router, prefix="/api/funds", tags=["Funds"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
