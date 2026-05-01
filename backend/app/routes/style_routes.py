"""Style API routes."""

import logging

from app.core.config import settings
from app.schemas.style_schema import StyleItem, StyleListResponse
from app.utils.prompt_manager import PromptManager
from fastapi import APIRouter, HTTPException, status

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Styles"])
prompt_manager: PromptManager = PromptManager()


@router.get("/styles", response_model=StyleListResponse)
async def get_styles() -> StyleListResponse:
    """Return available translation styles."""
    logger.info("Styles list requested.")
    try:
        style_names: list[str] = prompt_manager.list_styles()
        styles: list[StyleItem] = [
            StyleItem(
                key=style_name,
                label=prompt_manager.build_style_label(style_name),
            )
            for style_name in style_names
        ]
    except Exception as exc:
        logger.exception("Failed to list styles.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load styles.",
        ) from exc

    logger.debug("Styles list prepared. count=%s", len(styles))
    return StyleListResponse(
        styles=styles,
        default_style=prompt_manager.get_default_style(),
    )
