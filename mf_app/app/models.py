from sqlalchemy import Column, Integer, BigInteger, String, Numeric, TIMESTAMP, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Fund(Base):
    __tablename__ = "funds"
    id = Column(Integer, primary_key=True, index=True)
    scheme_code = Column(String, unique=True, index=True, nullable=False)
    scheme_name = Column(String, nullable=False)
    amc = Column(String, nullable=False)
    plan = Column(String, nullable=False)
    risk_profile = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    started_date = Column(TIMESTAMP, server_default=func.now())
    eq_or_dt = Column(String, nullable=False)
    type_of_mf = Column(String, nullable=False)

class NAV(Base):
    __tablename__ = "nav"
    id = Column(BigInteger, primary_key=True)
    scheme_code = Column(String, index=True, nullable=False)
    nav_time = Column(TIMESTAMP, nullable=False, index=True, primary_key=True)
    nav_value = Column(Numeric(18,6), nullable=False)