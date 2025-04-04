from pathlib import Path
from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent.resolve()
    PROJECT_NAME: str = "TestTask API"

    SQLITE_DB_NAME: str = "db.sqlite3"

    BOT_TOKEN: str = ""

    @computed_field
    @property
    def ASYNC_SQLITE_ALCHEMY_URI(self) -> str:
        schema = "sqlite+aiosqlite"
        return f"{schema}:///{self.PROJECT_ROOT}/{self.SQLITE_DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", env_ignore_empty=True, extra="ignore"
    )


@lru_cache
def get_settings():
    return Settings()
