import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    app_name: str = "Nivesh MF Analytics"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
