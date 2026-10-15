from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import Settings, get_settings


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    # Interactive docs help locally, but would publish the full API surface in production.
    show_docs = not settings.is_production

    app = FastAPI(
        title="Orbit API",
        version="0.1.0",
        docs_url="/api/docs" if show_docs else None,
        openapi_url="/api/openapi.json" if show_docs else None,
        redoc_url=None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
