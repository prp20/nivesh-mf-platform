from fastapi import FastAPI

# force model registration
from backend.models import Base  # noqa

from backend.api.v1.funds import router as funds_router
from backend.api.v1.fund_managers import router as fund_managers_router
from backend.api.v1.fund_manager_mapping import router as mapping_router
from backend.api.v1.nav import router as nav_router
from backend.api.v1.benchmarks import router as benchmark_router
from backend.api.v1.metrics import router as metrics_router
from backend.api.v1.compare import router as compare_router
from backend.api.v1.recommend import router as recommend_router
from backend.api.v1.metrics_read import router as metrics_read_router

app = FastAPI(title="Nivesh MF Analytics")

app.include_router(funds_router, prefix="/api/v1/funds", tags=["Funds"])
app.include_router(
    fund_managers_router,
    prefix="/api/v1/fund-managers",
    tags=["Fund Managers"],
)
app.include_router(mapping_router, prefix="/api/v1", tags=["Fund-Manager Mapping"])
app.include_router(nav_router, prefix="/api/v1", tags=["NAV"])
app.include_router(benchmark_router, prefix="/api/v1", tags=["Benchmarks"])
app.include_router(metrics_router, prefix="/api/v1", tags=["Metrics"])
app.include_router(compare_router, prefix="/api/v1", tags=["Compare"])
app.include_router(recommend_router, prefix="/api/v1", tags=["Recommendation"])
app.include_router(metrics_read_router, prefix="/api/v1", tags=["Metrics"])


@app.get("/api/v1/health", tags=["Health"])
def health():
    return {"status": "ok"}
