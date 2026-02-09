from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_USER: str = "mf_user"
    DB_PASS: str = "mf_pass"
    DB_NAME: str = "mf_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:"
            f"{self.DB_PASS}@{self.DB_HOST}:"
            f"{self.DB_PORT}/{self.DB_NAME}"
        )

settings = Settings()
