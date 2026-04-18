"""Database operations for translation history records."""

from app.models.translation_history import TranslationHistory
from app.schemas.history_schema import TranslationHistoryCreate
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_history_record(
    session: AsyncSession,
    payload: TranslationHistoryCreate,
) -> TranslationHistory:
    """Create and return a persisted translation history record."""

    history: TranslationHistory = TranslationHistory(**payload.model_dump())

    session.add(history)
    await session.commit()
    await session.refresh(history)

    return history


async def list_history_records(
    session: AsyncSession,
    page: int,
    page_size: int,
    keyword: str | None = None,
) -> tuple[list[TranslationHistory], int]:
    """Return a page of history records and the matching total count."""
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
    statement = select(TranslationHistory)

    if filters:
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    total = await session.scalar(count_statement)

    result = await session.execute(
        statement.order_by(
            TranslationHistory.created_at.desc(),
            TranslationHistory.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    return list(result.scalars().all()), total or 0


async def get_history_record(
    session: AsyncSession,
    history_id: int,
) -> TranslationHistory | None:
    """Return a history record by ID, or None when it does not exist."""
    return await session.get(TranslationHistory, history_id)


async def delete_history_record(
    session: AsyncSession,
    history_id: int,
) -> bool:
    """Delete a history record by ID and report whether it existed."""
    history = await session.get(TranslationHistory, history_id)

    if history is None:
        return False

    await session.delete(history)
    await session.commit()
    return True


async def clear_history_records(session: AsyncSession) -> int:
    """Delete all history records and return the number of removed rows."""
    result = await session.execute(delete(TranslationHistory))
    await session.commit()
    return result.rowcount or 0
