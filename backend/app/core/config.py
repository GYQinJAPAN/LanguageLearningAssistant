from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "LLM Chat Translator API"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"

    PROMPT_DIR: Path = BASE_DIR / "app" / "prompts"

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 300

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

    @property
    def api_prefix(self) -> str:
        prefix = self.API_PREFIX.strip()
        if not prefix:
            return ""
        return f"/{prefix.strip('/')}"  # 移除 prefix 首尾的所有斜杠 /。确保最终结果始终以单斜杠开头，且不以斜杠结尾。


settings = Settings()

# Compatibility alias for older imports. New code should use settings.PROMPT_DIR.
PROMPT_DIR = settings.PROMPT_DIR
