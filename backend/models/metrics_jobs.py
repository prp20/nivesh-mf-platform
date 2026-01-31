from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.models.base import Base

class MetricsJob(Base):
    __tablename__ = "metrics_jobs"

    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey("mutual_funds.id"), nullable=False)

    status = Column(String(20), nullable=False)  
    # PENDING | RUNNING | SUCCESS | FAILED

    error_message = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    fund = relationship("MutualFund")
