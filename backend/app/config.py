from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# uvicorn cwd 为 backend/；用户也常把 .env 放在仓库根目录（与根目录 .env.example 一致）
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent
_ENV_FILES = tuple(
    str(p)
    for p in (_REPO_ROOT / ".env", _BACKEND_ROOT / ".env")
    if p.is_file()
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        **({"env_file": _ENV_FILES} if _ENV_FILES else {}),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    database_url: str = "postgresql+asyncpg://coc:coc@localhost:5432/coc_ai_keeper"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
