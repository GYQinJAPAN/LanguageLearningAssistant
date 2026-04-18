from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DEFAULT_DATABASE_PATH = BASE_DIR / "data" / "app.db"
# .as_posix() 方法会将该路径转换为 使用正斜杠 / 分隔的字符串，例如："data/app.db"
# sqlite	表示数据库类型是 SQLite。
# +aiosqlite	指定使用 aiosqlite 这个 异步驱动 来操作 SQLite（因为标准库 sqlite3 是同步的）。
#:///	URL 协议分隔符，后面跟着数据库文件的 绝对路径。
DEFAULT_DATABASE_URL = f"sqlite+aiosqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"


class Settings(BaseSettings):
    APP_NAME: str = "LLM Chat Translator API"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: str = "http://127.0.0.1:5173,http://localhost:5173"

    PROMPT_DIR: Path = BASE_DIR / "app" / "prompts"
    DATABASE_URL: str = DEFAULT_DATABASE_URL

    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str | None = None
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
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    @property
    def api_prefix(self) -> str:
        prefix = self.API_PREFIX.strip()
        if not prefix:
            return ""
        return f"/{prefix.strip('/')}"  # 移除 prefix 首尾的所有斜杠 /。确保最终结果始终以单斜杠开头，且不以斜杠结尾。


settings = Settings()

# Compatibility alias for older imports. New code should use settings.PROMPT_DIR.
PROMPT_DIR = settings.PROMPT_DIR
