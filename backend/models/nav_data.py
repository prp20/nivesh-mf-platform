from sqlalchemy import (
    Column,
    Integer,
    Date,
    Numeric,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .base import Base


class NavData(Base):
    __tablename__ = "nav_data"

    id = Column(Integer, primary_key=True)
    fund_id = Column(
        Integer,
        ForeignKey("mutual_funds.id", ondelete="CASCADE"),
        nullable=False,
    )
    nav_date = Column(Date, nullable=False)
    nav_value = Column(Numeric(12, 6), nullable=False)

    fund = relationship("MutualFund", back_populates="navs")

    __table_args__ = (
        UniqueConstraint("fund_id", "nav_date", name="uq_fund_nav_date"),
        Index("ix_nav_fund_date", "fund_id", "nav_date"),
    )

