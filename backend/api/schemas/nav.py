from datetime import date
from pydantic import BaseModel
from typing import Optional


class HistoricalNavRequest(BaseModel):
    fund_id: int
    start_date: date
    end_date: date


class NavResponse(BaseModel):
    nav_date: date
    nav_value: float

    class Config:
        from_attributes = True


class NavDataResponse(BaseModel):
    id: int
    fund_id: int
    nav_date: date
    nav_value: float

    class Config:
        from_attributes = True
