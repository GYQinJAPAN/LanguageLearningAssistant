"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.core.logger import setup_logging
from app.routes import history_routes, style_routes, translate_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application resources before serving requests."""
    logger.info("Application starting.")
    logger.info("Host: %s", settings.APP_HOST)
    logger.info("Port: %s", settings.APP_PORT)
    logger.info("API prefix: %s", settings.api_prefix)
    logger.info("Allowed origins: %s", settings.allowed_origins_list)
    logger.info("OpenAI model: %s", settings.OPENAI_MODEL)
    logger.info("Database URL: %s", settings.DATABASE_URL)
    await init_db()
    yield
    logger.info("Application shutting down.")


app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(translate_routes.router)
app.include_router(style_routes.router)
app.include_router(history_routes.router)


@app.get("/")
async def root():
    """Return a basic API landing response."""
    return {"message": "Welcome to the LLM Translator API. Visit /docs for documentation."}


@app.get("/health")
async def health_check():
    """Return application health metadata."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
