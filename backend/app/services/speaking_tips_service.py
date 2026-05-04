"""Business flow for per-variant speaking tips generation and caching."""

import json
import logging
from json import JSONDecodeError

from app.core.database import rollback_session
from app.core.exceptions import DatabaseOperationError, UnsupportedTargetLanguageError
from app.models.translation_history import (
    SpeakingTip,
    TranslationHistory,
    TranslationVariant,
)
from app.schemas.speaking_tips_schema import SpeakingTipsPayload, SpeakingTipsResponse
from app.services.format.speaking_tips_response_format import (
    SPEAKING_TIPS_OUTPUT_TOKENS,
    SPEAKING_TIPS_RESPONSE_FORMAT,
)
from app.services.llm_service import generate_speaking_tips
from app.services.parsers.speaking_tips_parser import parse_speaking_tips
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

ENGLISH_TARGET_LANGUAGE_VALUES = {
    "english",
    "en",
    "英语",
    "英文",
}


def is_english_target_language(target_lang: str) -> bool:
    """Return whether the saved target language should allow speaking tips."""
    normalized = target_lang.strip()
    if not normalized:
        return False

    lowered = normalized.lower()
    if lowered in ENGLISH_TARGET_LANGUAGE_VALUES:
        return True

    normalized_ascii = lowered.replace("_", "-")
    return normalized_ascii.startswith("english") or normalized_ascii in {
        "en-us",
        "en-gb",
    }


def _deserialize_cached_tip(tip: SpeakingTip) -> SpeakingTipsPayload:
    """Convert a persisted speaking tips row back into the response payload."""
    try:
        return SpeakingTipsPayload(
            stress_words=json.loads(tip.stress_words_json),
            linking_notes=json.loads(tip.linking_notes_json),
            more_spoken_text=tip.more_spoken_text,
            note_text=tip.note_text,
        )
    except (JSONDecodeError, TypeError, ValueError) as exc:
        logger.exception("Cached speaking tips payload is invalid. variant_id=%s", tip.variant_id)
        raise DatabaseOperationError("Cached speaking tips are unavailable.") from exc


def _serialize_payload(variant_id: int, payload: SpeakingTipsPayload, cached: bool) -> SpeakingTipsResponse:
    """Convert normalized tips payload into the API response model."""
    return SpeakingTipsResponse(
        variant_id=variant_id,
        cached=cached,
        stress_words=payload.stress_words,
        linking_notes=payload.linking_notes,
        more_spoken_text=payload.more_spoken_text,
        note_text=payload.note_text,
    )


async def get_or_create_speaking_tips(
    session: AsyncSession,
    variant_id: int,
) -> SpeakingTipsResponse:
    """Return cached speaking tips or generate, persist, and return them."""
    logger.info("Speaking tips request received. variant_id=%s", variant_id)

    try:
        cached_tip = await session.scalar(select(SpeakingTip).where(SpeakingTip.variant_id == variant_id))
    except SQLAlchemyError as exc:
        logger.exception("Failed to load cached speaking tips. variant_id=%s", variant_id)
        raise DatabaseOperationError("Failed to load speaking tips.") from exc
    if cached_tip is not None:
        logger.info("Speaking tips cache hit. variant_id=%s cached=true", variant_id)
        return _serialize_payload(
            variant_id=variant_id,
            payload=_deserialize_cached_tip(cached_tip),
            cached=True,
        )

    try:
        variant = await session.scalar(
            select(TranslationVariant)
            .options(selectinload(TranslationVariant.history))
            .where(TranslationVariant.id == variant_id)
        )
    except SQLAlchemyError as exc:
        logger.exception(
            "Failed to load translation variant for speaking tips. variant_id=%s",
            variant_id,
        )
        raise DatabaseOperationError("Failed to load speaking tips target variant.") from exc
    if variant is None:
        logger.warning(
            "Speaking tips request referenced missing variant. variant_id=%s",
            variant_id,
        )
        raise LookupError("Translation variant not found.")

    history: TranslationHistory | None = variant.history
    if history is None:
        logger.error(
            "Speaking tips request found variant without history. variant_id=%s",
            variant_id,
        )
        raise DatabaseOperationError("Translation history is missing for the selected variant.")

    if not is_english_target_language(history.target_lang):
        logger.warning(
            "Speaking tips rejected for non-English target language. variant_id=%s target_lang=%s",
            variant_id,
            history.target_lang,
        )
        raise UnsupportedTargetLanguageError(
            "Speaking tips are currently available only when the target language is English."
        )

    logger.info("Speaking tips cache miss. variant_id=%s cached=false", variant_id)
    logger.info(
        "Calling LLM for speaking tips. variant_id=%s variant_type=%s",
        variant_id,
        variant.variant_type,
    )
    raw_text = await generate_speaking_tips(
        source_lang=history.source_lang,
        target_lang=history.target_lang,
        source_text=history.source_text,
        variant_type=variant.variant_type,
        translated_text=variant.translated_text,
        max_output_tokens=SPEAKING_TIPS_OUTPUT_TOKENS,
        text_format=SPEAKING_TIPS_RESPONSE_FORMAT,
    )
    payload = parse_speaking_tips(raw_text)
    logger.info(
        "Speaking tips parsed successfully. variant_id=%s stress_word_count=%s linking_note_count=%s",
        variant_id,
        len(payload.stress_words),
        len(payload.linking_notes),
    )

    speaking_tip = SpeakingTip(
        variant_id=variant.id,
        stress_words_json=json.dumps(payload.stress_words, ensure_ascii=False),
        linking_notes_json=json.dumps(
            [item.model_dump() for item in payload.linking_notes],
            ensure_ascii=False,
        ),
        more_spoken_text=payload.more_spoken_text,
        note_text=payload.note_text,
    )
    try:
        session.add(speaking_tip)
        await session.commit()
    except SQLAlchemyError as exc:
        await rollback_session(session, action="create_speaking_tips")
        logger.exception("Failed to persist speaking tips. variant_id=%s", variant_id)
        raise DatabaseOperationError("Failed to save speaking tips.") from exc

    logger.info("Speaking tips saved successfully. variant_id=%s", variant_id)
    return _serialize_payload(variant_id=variant.id, payload=payload, cached=False)
