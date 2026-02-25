from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .db import Base, engine
from .routers.receipts import router as receipts_router
from .routers.stats import router as stats_router


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _startup_create_tables_with_retry():
        last_error: Exception | None = None
        for _ in range(20):
            try:
                with engine.connect() as conn:
                    conn.exec_driver_sql("SELECT 1")
                Base.metadata.create_all(bind=engine)
                return
            except Exception as e:
                last_error = e
                time.sleep(2)
        raise RuntimeError(f"Database not ready after retries: {last_error}")

    app.include_router(receipts_router)
    app.include_router(stats_router)

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_dir)), name="uploads")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
