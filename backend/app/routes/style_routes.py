from fastapi import APIRouter
from app.core.config import PROMPT_DIR
from app.schemas.style_schema import StyleItem, StyleListResponse

router: APIRouter = APIRouter(prefix="/api/v1", tags=["Styles"])


@router.get("/styles", response_model=StyleListResponse)
async def get_styles():
    """
    style 列表 API
    """

    styles = []

    if PROMPT_DIR.exists():
        for file in PROMPT_DIR.glob("*.txt"):
            style_key = file.stem

            styles.append(
                StyleItem(key=style_key, label=style_key.replace("_", " ").title())
            )

    styles.sort(key=lambda x: x.key)

    return StyleListResponse(styles=styles, default_style="base_prompt")
