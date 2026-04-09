import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import setup_logging
from app.routes import style_routes
from app.routes import translate_routes
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

setup_logging()
logger = logging.getLogger(__name__)  # 获取一个日志记录器，名称是当前模块名


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting...")
    logger.info("Host: %s", settings.APP_HOST)
    logger.info("Port: %s", settings.APP_PORT)
    logger.info("Allowed origins: %s", settings.allowed_origins_list)
    yield
    logger.info("Application shutting down...")


# 创建 FastAPI 应用
app: FastAPI = FastAPI(
    title="LLM Chat Translator API",
    lifespan=lifespan,
)

# 配置中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册路由
app.include_router(translate_routes.router, tags=["Translate"])
app.include_router(style_routes.router, tags=["Styles"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to the LLM Translator API. Visit /docs for documentation."
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}
