"""Translation API routes."""

import logging

from app.core.config import settings
from app.core.database import get_db_session
from app.schemas.history_schema import TranslationHistoryCreate
from app.schemas.translate_schema import TranslateRequest, TranslateResponse
from app.services.history_service import create_history_record
from app.services.llm_service import translate_and_rewrite
from app.utils.prompt_manager import PromptManager
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Translation"])
prompt_manager: PromptManager = PromptManager()


@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(
    request: TranslateRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """Translate user text and persist the result to history."""
    try:
        actual_style, prompt_template = prompt_manager.load_prompt(request.style)

        system_prompt = prompt_manager.build_system_prompt(
            prompt_template=prompt_template,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        result_text = await translate_and_rewrite(
            user_text=request.text,
            system_prompt=system_prompt,
        )

        response = TranslateResponse(
            original_text=request.text,
            translated_text=result_text,
            style_requested=request.style,
            style_applied=actual_style,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        await create_history_record(
            session=session,
            payload=TranslationHistoryCreate(
                source_text=response.original_text,
                translated_text=response.translated_text,
                style_requested=response.style_requested,
                style_applied=response.style_applied,
                source_lang=response.source_lang,
                target_lang=response.target_lang,
            ),
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
