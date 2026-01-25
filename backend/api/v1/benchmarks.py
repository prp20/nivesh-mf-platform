from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.models.benchmark_nav import BenchmarkNav

router = APIRouter()


@router.post("/benchmarks/nav/fetch")
def fetch_benchmark_nav(db: Session = Depends(get_db)):
    today = date.today()
    benchmarks = ["NIFTY 50", "NIFTY 100", "NIFTY 500"]

    for name in benchmarks:
        exists = (
            db.query(BenchmarkNav)
            .filter_by(benchmark_name=name, nav_date=today)
            .first()
        )
        if not exists:
            db.add(
                BenchmarkNav(
                    benchmark_name=name,
                    nav_date=today,
                    nav_value=100.0,  # placeholder
                )
            )

    db.commit()
    return {"message": "Benchmark NAV fetch completed"}


@router.get("/benchmarks/{benchmark_name}/nav")
def get_benchmark_nav(benchmark_name: str, db: Session = Depends(get_db)):
    return (
        db.query(BenchmarkNav)
        .filter(BenchmarkNav.benchmark_name == benchmark_name)
        .order_by(BenchmarkNav.nav_date)
        .all()
    )


@router.delete("/benchmarks/{benchmark_name}/nav")
def delete_benchmark_nav(benchmark_name: str, db: Session = Depends(get_db)):
    db.query(BenchmarkNav).filter(
        BenchmarkNav.benchmark_name == benchmark_name
    ).delete()
    db.commit()
    return {"message": "Benchmark NAV deleted"}
