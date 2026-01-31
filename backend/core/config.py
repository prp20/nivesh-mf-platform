import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PostgreSQL configuration (relational data)
    postgres_host: str = "localhost"
    postgres_port: int = 5433
    postgres_name: str = "mf_relational"
    postgres_user: str = "mf_user"
    postgres_password: str = "mf_password"

    # TimescaleDB configuration (time-series data)
    timescaledb_host: str = "localhost"
    timescaledb_port: int = 5432
    timescaledb_name: str = "mf_timeseries"
    timescaledb_user: str = "mf_user"
    timescaledb_password: str = "mf_password"

    @property
    def postgres_url(self) -> str:
        return f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_name}"

    @property
    def timescaledb_url(self) -> str:
        return f"postgresql+psycopg://{self.timescaledb_user}:{self.timescaledb_password}@{self.timescaledb_host}:{self.timescaledb_port}/{self.timescaledb_name}"

    app_name: str = "Nivesh MF Analytics"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
