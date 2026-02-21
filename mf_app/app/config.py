from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    DATABASE_URL: str ="postgresql+asyncpg://mf_admin:mf_secure_password_123@localhost:5432/mutual_fund_db"
    # Or for local TimescaleDB
    # DATABASE_URL: str = "postgresql+asyncpg://mf_user:mf_pass@localhost:5432/mf_user"
    
    model_config = ConfigDict(env_file=".env", extra="ignore")

settings = Settings()
