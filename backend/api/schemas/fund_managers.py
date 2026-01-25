from typing import Optional
from pydantic import BaseModel


class FundManagerBase(BaseModel):
    name: str
    experience_years: Optional[int] = None


class FundManagerCreate(FundManagerBase):
    pass


class FundManagerUpdate(BaseModel):
    name: Optional[str] = None
    experience_years: Optional[int] = None


class FundManagerResponse(FundManagerBase):
    id: int

    class Config:
        from_attributes = True
