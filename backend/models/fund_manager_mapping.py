from sqlalchemy import Column, Integer, ForeignKey
from .base import Base


class FundManagerMapping(Base):
    __tablename__ = "fund_manager_mapping"

    fund_id = Column(
        Integer,
        ForeignKey("mutual_funds.id", ondelete="CASCADE"),
        primary_key=True,
    )
    manager_id = Column(
        Integer,
        ForeignKey("fund_managers.id", ondelete="CASCADE"),
        primary_key=True,
    )
