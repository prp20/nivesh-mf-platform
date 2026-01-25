from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class FundManager(Base):
    __tablename__ = "fund_managers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    experience_years = Column(Integer, nullable=True)

    funds = relationship(
        "MutualFund",
        secondary="fund_manager_mapping",
        back_populates="managers",
    )
