from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_name: str = "multiagent-content-factory"

    database_url: str = "sqlite+pysqlite:///./data/app.db"

    object_storage_mode: str = "local"  # local | s3 (reserved)
    local_storage_dir: str = "./data/storage"

    jwt_secret: str = "change-me"
    jwt_issuer: str = "multiagent-content-factory"
    jwt_audience: str = "web"
    jwt_expires_minutes: int = 60 * 24 * 3

    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    celery_always_eager: bool = True

    embedding_provider: str = "sentence_transformers"
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    llm_provider: str = "stub"

    def ensure_dirs(self) -> None:
        Path("./data").mkdir(parents=True, exist_ok=True)
        if self.object_storage_mode == "local":
            Path(self.local_storage_dir).mkdir(parents=True, exist_ok=True)


settings = Settings()

