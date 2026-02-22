from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime, date
from decimal import Decimal
from typing import Optional


# ============================================================================
# FUND MASTER SCHEMAS
# ============================================================================

class FundMasterCreate(BaseModel):
    scheme_code: str
    scheme_name: str
    amc_name: str
    inception_date: date
    plan_type: str  # 'Direct' or 'Regular'
    scheme_category: str
    scheme_subcategory: Optional[str] = None
    benchmark_index_code: Optional[str] = None
    is_active: bool = True


class FundMasterRead(FundMasterCreate):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FundMasterUpdate(BaseModel):
    scheme_name: Optional[str] = None
    amc_name: Optional[str] = None
    inception_date: Optional[date] = None
    plan_type: Optional[str] = None
    scheme_category: Optional[str] = None
    scheme_subcategory: Optional[str] = None
    benchmark_index_code: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# FUND METRICS SCHEMAS
# ============================================================================

class FundMetricsCreate(BaseModel):
    scheme_code: str
    current_nav: Decimal
    nav_date: date
    aum_in_crores: Optional[Decimal] = None
    rolling_return_3year: Optional[Decimal] = None
    rolling_return_5year: Optional[Decimal] = None
    sortino_ratio: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    alpha: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    standard_deviation: Optional[Decimal] = None
    maximum_drawdown: Optional[Decimal] = None
    tracking_error: Optional[Decimal] = None
    information_ratio: Optional[Decimal] = None
    calculation_period_start_date: Optional[date] = None
    calculation_period_end_date: Optional[date] = None
    has_sufficient_data: bool = True
    data_completeness_percentage: Optional[Decimal] = None


class FundMetricsRead(FundMetricsCreate):
    metrics_calculated_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class FundMetricsUpdate(BaseModel):
    current_nav: Optional[Decimal] = None
    nav_date: Optional[date] = None
    aum_in_crores: Optional[Decimal] = None
    rolling_return_3year: Optional[Decimal] = None
    rolling_return_5year: Optional[Decimal] = None
    sortino_ratio: Optional[Decimal] = None
    sharpe_ratio: Optional[Decimal] = None
    alpha: Optional[Decimal] = None
    beta: Optional[Decimal] = None
    standard_deviation: Optional[Decimal] = None
    maximum_drawdown: Optional[Decimal] = None
    tracking_error: Optional[Decimal] = None
    information_ratio: Optional[Decimal] = None
    calculation_period_start_date: Optional[date] = None
    calculation_period_end_date: Optional[date] = None
    has_sufficient_data: Optional[bool] = None
    data_completeness_percentage: Optional[Decimal] = None


# ============================================================================
# FUND NAV HISTORY SCHEMAS
# ============================================================================

class FundNavHistoryCreate(BaseModel):
    scheme_code: str
    nav_date: date
    nav_value: Decimal


class FundNavHistoryBulkCreate(BaseModel):
    """Schema for bulk NAV insertion with dictionary format"""
    scheme_code: str
    nav_data: dict  # Format: {"YYYY-MM-DD": nav_value, ...}


class FundNavHistoryBulkUpdate(BaseModel):
    """Schema for bulk NAV update/patch - only requires nav_data (scheme_code in URL)"""
    nav_data: dict  # Format: {"YYYY-MM-DD": nav_value, ...}


class FundNavHistoryRead(FundNavHistoryCreate):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# BENCHMARK MASTER SCHEMAS
# ============================================================================

class BenchmarkMasterCreate(BaseModel):
    benchmark_code: str
    benchmark_name: str
    ticker: str
    benchmark_type: Optional[str] = None
    asset_class: Optional[str] = None
    is_active: bool = True


class BenchmarkMasterRead(BenchmarkMasterCreate):
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class BenchmarkMasterUpdate(BaseModel):
    benchmark_name: Optional[str] = None
    benchmark_type: Optional[str] = None
    ticker: Optional[str] = None
    asset_class: Optional[str] = None
    is_active: Optional[bool] = None


# ============================================================================
# BENCHMARK NAV HISTORY SCHEMAS
# ============================================================================

class BenchmarkNavHistoryCreate(BaseModel):
    benchmark_code: str
    nav_date: date
    index_value: Decimal


class BenchmarkNavHistoryBulkCreate(BaseModel):
    """Schema for bulk benchmark NAV insertion with dictionary format"""
    benchmark_code: str
    nav_data: dict  # Format: {"YYYY-MM-DD": index_value, ...}


class BenchmarkNavHistoryBulkUpdate(BaseModel):
    """Schema for bulk benchmark NAV update/patch - only requires nav_data (benchmark_code in URL)"""
    nav_data: dict  # Format: {"YYYY-MM-DD": index_value, ...}


class BenchmarkNavHistoryRead(BenchmarkNavHistoryCreate):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# LEGACY SCHEMAS (For backward compatibility if needed)
# ============================================================================

class FundCreate(BaseModel):
    """Legacy schema - use FundMasterCreate instead"""
    scheme_code: str
    scheme_name: str
    amc: str
    plan: str
    risk_profile: str
    started_date: datetime
    eq_or_dt: str
    type_of_mf: str


class FundRead(FundCreate):
    """Legacy schema - use FundMasterRead instead"""
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NAVCreate(BaseModel):
    """Legacy schema - use FundNavHistoryCreate instead"""
    scheme_code: str
    nav_time: datetime
    nav_value: float


class NAVRead(NAVCreate):
    """Legacy schema - use FundNavHistoryRead instead"""
    model_config = ConfigDict(from_attributes=True)
