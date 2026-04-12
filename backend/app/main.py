import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import setup_logging
from app.routes import style_routes, translate_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting.")
    logger.info("Host: %s", settings.APP_HOST)
    logger.info("Port: %s", settings.APP_PORT)
    logger.info("API prefix: %s", settings.api_prefix)
    logger.info("Allowed origins: %s", settings.allowed_origins_list)
    logger.info("OpenAI model: %s", settings.OPENAI_MODEL)
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


@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Translator API. Visit /docs for documentation."}


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
