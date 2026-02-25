from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
        enable_decoding=False,
    )

    app_name: str = "OCR Receipts Demo"
    environment: str = "dev"

    database_url: str = "mysql+pymysql://ocr:ocr@127.0.0.1:3307/ocr"

    upload_dir: str = "uploads"

    # Comma-separated origins, e.g. "http://localhost:5173,http://localhost:3000"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    tesseract_cmd: str | None = None

    # Tesseract OCR language (e.g. "vie" or "eng")
    ocr_lang: str = "vie"

    # Optional: fallback OCR language if the primary language is missing (default: eng)
    ocr_fallback_lang: str | None = "eng"

    # Optional: path to tessdata directory (where *.traineddata lives)
    # Example: C:\Program Files\Tesseract-OCR\tessdata
    tessdata_prefix: str | None = None

    def cors_origins_list(self) -> list[str]:
        if not self.cors_origins:
            return []
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

    @field_validator("upload_dir", mode="before")
    @classmethod
    def _normalize_upload_dir(cls, v):
        if isinstance(v, str):
            return v.replace("\\", "/")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
