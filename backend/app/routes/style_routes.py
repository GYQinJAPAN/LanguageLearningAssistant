from app.core.config import settings
from app.schemas.style_schema import StyleItem, StyleListResponse
from app.utils.prompt_manager import PromptManager
from fastapi import APIRouter

router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Styles"])
prompt_manager: PromptManager = PromptManager()


@router.get("/styles", response_model=StyleListResponse)
async def get_styles():
    style_names = prompt_manager.list_styles()
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
