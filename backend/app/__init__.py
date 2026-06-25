from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from core.database import create_tables
from core.redis_client import init_redis, close_redis
from core.config import settings
from middelware.cors import setup_cors
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────
    await init_redis()
    await create_tables()   # Creates tables if they don't exist
    yield
    # ── Shutdown ──────────────────────────────────────────
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="PraDoc Health API",
        description="Healthcare Appointment & Patient Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Middleware
    setup_cors(app)

    # Routers
    app.include_router(api_router)

    # Static file serving for uploads (documents, photos)
    uploads_path = Path(settings.UPLOAD_DIR)
    uploads_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "ok", "env": settings.APP_ENV}

    return app


app = create_app()
