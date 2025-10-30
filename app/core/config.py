# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):

    MY_SQL_USER: str
    MY_SQL_PASSWORD: str
    MY_SQL_DB: str
    MY_SQL_HOST: str = "mysql"
    MY_SQL_PORT: int = 3306
    SECRET_KEY: str = "secret_key_1234"
    ALGORITHM: str = "HS256"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+asyncmy://{self.MY_SQL_USER}:{self.MY_SQL_PASSWORD}"
            f"@{self.MY_SQL_HOST}:{self.MY_SQL_PORT}/{self.MY_SQL_DB}"
        )

    class Config:
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()
