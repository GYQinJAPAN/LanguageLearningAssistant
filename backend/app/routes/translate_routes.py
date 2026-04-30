"""Translation API routes."""

import logging

from app.core.config import settings
from app.core.database import DatabaseOperationError, get_db_session
from app.schemas.translate_schema import TranslateRequest, TranslateResponse
from app.services.llm_service import LLMServiceError
from app.services.translation_service import handle_translation_request
from app.utils.json_payload import StructuredOutputError
from app.utils.prompt_manager import PromptManagerError
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
) -> TranslateResponse:
    """Translate user text and persist the result to history."""
    logger.info(
        "Translate endpoint received request. mode=%s style=%s source_lang=%s target_lang=%s text_length=%s",
        request.result_mode,
        request.style,
        request.source_lang,
        request.target_lang,
        len(request.text),
    )
    try:
        return await handle_translation_request(request=request, session=session)
    except ValueError as exc:
        logger.warning("Invalid translate request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except PromptManagerError as exc:
        logger.error("Translation prompt loading failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation prompt configuration is unavailable.",
        ) from exc
    except StructuredOutputError as exc:
        logger.warning("Translation structured output parsing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Translation service returned an invalid structured response.",
        ) from exc
    except LLMServiceError as exc:
        logger.warning("Translation upstream call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The translation service is temporarily unavailable.",
        ) from exc
    except DatabaseOperationError as exc:
        logger.error("Translation history persistence failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save translation history.",
        ) from exc
    except RuntimeError as exc:
        logger.warning("Translation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation request failed.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected translation error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from exc
