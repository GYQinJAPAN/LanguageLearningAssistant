from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import style_routes
from app.routes import translate_routes

# 创建 FastAPI 应用
app: FastAPI = FastAPI(title="LLM Chat Translator API")

# 配置中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
