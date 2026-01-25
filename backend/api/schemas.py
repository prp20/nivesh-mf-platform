from datetime import date
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
