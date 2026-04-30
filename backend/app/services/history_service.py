"""Database operations for translation history records."""

import logging

from app.core.database import DatabaseOperationError, rollback_session
from app.models.translation_history import SpeakingTip, TranslationHistory, TranslationVariant
from app.schemas.history_schema import TranslationHistoryCreate, TranslationVariantCreate
from sqlalchemy import delete, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)


async def create_history_record(
    session: AsyncSession,
    payload: TranslationHistoryCreate,
    variants: list[TranslationVariantCreate] | None = None,
) -> TranslationHistory:
    """Create and return a persisted translation history record.

    Raises:
        DatabaseOperationError: If the record cannot be committed or reloaded.
    """
    history = TranslationHistory(**payload.model_dump())
    if variants:
        history.variants = [TranslationVariant(**variant.model_dump()) for variant in variants]

    try:
        session.add(history)
        await session.commit()
    except SQLAlchemyError as exc:
        await rollback_session(session, action="create_history_record")
        logger.exception("Failed to save translation history.")
        raise DatabaseOperationError("Failed to save translation history.") from exc

    try:
        await session.refresh(history)
        await session.refresh(history, attribute_names=["variants"])
    except SQLAlchemyError as exc:
        logger.exception("Failed to refresh saved translation history. history_id=%s", history.id)
        raise DatabaseOperationError("Failed to load saved translation history.") from exc

    logger.info(
        "Translation history saved. history_id=%s variant_count=%s",
        history.id,
        len(history.variants),
    )
    return history


async def list_history_records(
    session: AsyncSession,
    page: int,
    page_size: int,
    keyword: str | None = None,
) -> tuple[list[TranslationHistory], int]:
    """Return a page of history records and the matching total count.

    Raises:
        DatabaseOperationError: If the query fails.
    """
    filters = []
    if keyword:
        pattern = f"%{keyword.strip()}%"
        filters.append(
            or_(
                TranslationHistory.source_text.ilike(pattern),
                TranslationHistory.translated_text.ilike(pattern),
                TranslationHistory.style_requested.ilike(pattern),
                TranslationHistory.style_applied.ilike(pattern),
                TranslationHistory.source_lang.ilike(pattern),
                TranslationHistory.target_lang.ilike(pattern),
            )
        )

    count_statement = select(func.count()).select_from(TranslationHistory)
    statement = select(TranslationHistory).options(selectinload(TranslationHistory.variants))

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    try:
        total = await session.scalar(count_statement)
        result = await session.execute(
            statement.order_by(
                TranslationHistory.created_at.desc(),
                TranslationHistory.id.desc(),
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    except SQLAlchemyError as exc:
        logger.exception(
            "Failed to query translation history. page=%s page_size=%s keyword_present=%s",
            page,
            page_size,
            bool(keyword),
        )
        raise DatabaseOperationError("Failed to query translation history.") from exc

    return list(result.scalars().all()), total or 0


async def get_history_record(
    session: AsyncSession,
    history_id: int,
) -> TranslationHistory | None:
    """Return a history record by ID, or None when it does not exist.

    Raises:
        DatabaseOperationError: If the query fails.
    """
    try:
        result = await session.execute(
            select(TranslationHistory)
            .options(selectinload(TranslationHistory.variants))
            .where(TranslationHistory.id == history_id)
        )
    except SQLAlchemyError as exc:
        logger.exception("Failed to load translation history. history_id=%s", history_id)
        raise DatabaseOperationError("Failed to load translation history.") from exc
    return result.scalar_one_or_none()


async def delete_history_record(session: AsyncSession, history_id: int) -> bool:
    """Delete a history record by ID and report whether it existed.

    Raises:
        DatabaseOperationError: If the delete transaction fails.
    """
    try:
        history = await session.get(TranslationHistory, history_id)
    except SQLAlchemyError as exc:
        logger.exception("Failed to load history record for deletion. history_id=%s", history_id)
        raise DatabaseOperationError("Failed to delete translation history.") from exc

    if history is None:
        return False

    variant_ids = select(TranslationVariant.id).where(TranslationVariant.history_id == history_id)
    try:
        await session.execute(delete(SpeakingTip).where(SpeakingTip.variant_id.in_(variant_ids)))
        await session.execute(delete(TranslationVariant).where(TranslationVariant.history_id == history_id))
        await session.delete(history)
        await session.commit()
    except SQLAlchemyError as exc:
        await rollback_session(session, action="delete_history_record")
        logger.exception("Failed to delete translation history. history_id=%s", history_id)
        raise DatabaseOperationError("Failed to delete translation history.") from exc

    logger.info("Translation history deleted. history_id=%s", history_id)
    return True


async def clear_history_records(session: AsyncSession) -> int:
    """Delete all history records and return the number of removed rows.

    Raises:
        DatabaseOperationError: If the delete transaction fails.
    """
    try:
        await session.execute(delete(SpeakingTip))
        await session.execute(delete(TranslationVariant))
        result = await session.execute(delete(TranslationHistory))
        await session.commit()
    except SQLAlchemyError as exc:
        await rollback_session(session, action="clear_history_records")
        logger.exception("Failed to clear translation history.")
        raise DatabaseOperationError("Failed to clear translation history.") from exc

    deleted_count = result.rowcount or 0
    logger.info("Translation history cleared. deleted_count=%s", deleted_count)
    return deleted_count
