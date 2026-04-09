from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py
# parent = core
# parent.parent = app
# parent.parent.parent = backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    OPENAI_API_KEY: str
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()

# 兼容旧代码
PROMPT_DIR = BASE_DIR / "app" / "prompts"
