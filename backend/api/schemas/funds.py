from datetime import date
from typing import Optional
from pydantic import BaseModel


class FundBase(BaseModel):
    scheme_code: str
    fund_name: str
    category: str
    sub_category: Optional[str] = None
    benchmark: Optional[str] = None
    aum: Optional[float] = None
    ter: Optional[float] = None
    exit_load: Optional[float] = None
    stamp_duty: Optional[float] = None
    fund_house: Optional[str] = None
    launch_date: Optional[date] = None


class FundCreate(FundBase):
    pass


class FundUpdate(BaseModel):
    fund_name: Optional[str] = None
    category: Optional[str] = None
    sub_category: Optional[str] = None
    benchmark: Optional[str] = None
    aum: Optional[float] = None
    ter: Optional[float] = None
    exit_load: Optional[float] = None
    stamp_duty: Optional[float] = None
    fund_house: Optional[str] = None
    launch_date: Optional[date] = None


class FundResponse(FundBase):
    id: int

    class Config:
        from_attributes = True
