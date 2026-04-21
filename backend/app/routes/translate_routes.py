"""Translation API routes."""

import logging

from app.core.config import settings
from app.core.database import get_db_session
from app.schemas.translate_schema import (
    TranslateRequest,
    TranslateResponse,
)
from app.services.translation_service import handle_translation_request
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Translation"])


@router.post(
    "/translate",
    response_model=TranslateResponse,
    response_model_exclude_none=True,
    response_model_exclude_defaults=True,
)
async def translate_endpoint(
    request: TranslateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Translate user text and persist the result to history."""
    try:
        response = await handle_translation_request(
            request=request,
            session=session,
        )
        return response

    except ValueError as exc:
        logger.warning("Invalid translate request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.warning("Translation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        logger.exception("Unexpected translation error.")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后再试。")
