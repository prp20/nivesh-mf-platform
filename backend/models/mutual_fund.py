from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class MutualFund(Base):
    __tablename__ = "mutual_funds"

    id = Column(Integer, primary_key=True)
    scheme_code = Column(String(50), nullable=False, unique=True)
    fund_name = Column(String(255), nullable=False)

    category = Column(String(50), nullable=False)       # Equity / Debt / Hybrid
    sub_category = Column(String(100), nullable=True)   # Large Cap, Flexi Cap

    benchmark = Column(String(100), nullable=True)

    aum = Column(Numeric(20, 2), nullable=True)
    ter = Column(Numeric(5, 2), nullable=True)
    exit_load = Column(Numeric(5, 2), nullable=True)
    stamp_duty = Column(Numeric(5, 2), nullable=True)
    fund_house = Column(String(255), nullable=True)

    launch_date = Column(Date, nullable=True)

    # Relationships (navs removed - it's in TimescaleDB)
    managers = relationship(
        "FundManager",
        secondary="fund_manager_mapping",
        back_populates="funds",
    )
    metrics = relationship(
        "FundMetricsSnapshot",
        back_populates="fund",
        cascade="all, delete-orphan",
    )
