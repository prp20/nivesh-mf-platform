from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FundCreate(BaseModel):
    scheme_code: str
    scheme_name: str
    amc: str
    plan: str
    risk_profile: str
    started_date: datetime
    eq_or_dt: str
    type_of_mf: str

class FundRead(FundCreate):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class NAVCreate(BaseModel):
    scheme_code: str
    nav_time: datetime
    nav_value: float

class NAVRead(NAVCreate):
    model_config = ConfigDict(from_attributes=True)
