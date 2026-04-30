"""Speaking tips API routes."""

import logging

from app.core.config import settings
from app.core.database import DatabaseOperationError, get_db_session
from app.schemas.speaking_tips_schema import SpeakingTipsResponse
from app.services.llm_service import LLMServiceError
from app.services.speaking_tips_service import get_or_create_speaking_tips
from app.utils.json_payload import StructuredOutputError
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Speaking Tips"])


@router.post("/variants/{variant_id}/speaking-tips", response_model=SpeakingTipsResponse)
async def create_or_get_speaking_tips(
    variant_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> SpeakingTipsResponse:
    """Return cached speaking tips or generate them for one translation variant."""
    logger.info("Speaking tips endpoint received request. variant_id=%s", variant_id)
    try:
        return await get_or_create_speaking_tips(session=session, variant_id=variant_id)
    except LookupError as exc:
        logger.warning("Speaking tips variant not found. variant_id=%s", variant_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        logger.warning("Speaking tips request rejected: %s", exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except StructuredOutputError as exc:
        logger.warning("Speaking tips structured output parsing failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Speaking tips service returned an invalid structured response.",
        ) from exc
    except LLMServiceError as exc:
        logger.warning("Speaking tips upstream call failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The speaking tips service is temporarily unavailable.",
        ) from exc
    except DatabaseOperationError as exc:
        logger.error("Speaking tips persistence failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save speaking tips.",
        ) from exc
    except RuntimeError as exc:
        logger.warning("Speaking tips generation failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Speaking tips request failed.",
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected speaking tips error.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error.",
        ) from exc
