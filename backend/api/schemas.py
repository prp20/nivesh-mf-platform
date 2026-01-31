from datetime import date
from decimal import Decimal
from pydantic import BaseModel
from typing import Optional


class MutualFundCreate(BaseModel):
    scheme_code: str
    fund_name: str
    category: str
    sub_category: Optional[str] = None
    benchmark: Optional[str] = None
    aum: Optional[float] = None
    ter: Optional[float] = None
    launch_date: Optional[date] = None


class MutualFundResponse(MutualFundCreate):
    id: int

    class Config:
        from_attributes = True


class NavDataResponse(BaseModel):
    id: int
    fund_id: int
    nav_date: date
    nav_value: float

    class Config:
        from_attributes = True
