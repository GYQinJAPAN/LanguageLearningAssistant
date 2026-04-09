from fastapi import APIRouter

from app.utils.prompt_manager import PromptManager
from app.core.config import PROMPT_DIR
from app.schemas.style_schema import StyleItem, StyleListResponse

"""基于 FastAPI 框架编写的后端接口（API）路由文件"""
router: APIRouter = APIRouter(prefix="/api/v1", tags=["Styles"])
prompt_manager: PromptManager = PromptManager()

# 初始化了一个 API 路由，所有的接口前面都会自动带上 /api/v1 的前缀，
# 并且在自动生成的 API 文档（如 Swagger UI）中，它会被归类到 Styles 标签下。


# 定义了一个处理 GET 请求 的接口，完整访问路径是 /api/v1/styles。
@router.get("/styles", response_model=StyleListResponse)
async def get_styles():
    """
    style 列表 API
    """

    style_names: list[str] = prompt_manager.list_styles()

    styles = [
        StyleItem(
            key=style_name,
            label=prompt_manager.build_style_label(style_name),
        )
        for style_name in style_names
    ]

    return StyleListResponse(
        styles=styles,
        default_style=prompt_manager.get_default_style(),
    )
