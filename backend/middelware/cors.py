from fastapi.middleware.cors import CORSMiddleware
from core.config import settings


def setup_cors(app) -> None:
    """Attach CORS middleware to the FastAPI app."""
    origins = [
        settings.FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
