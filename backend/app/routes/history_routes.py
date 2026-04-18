from app.core.config import settings
from app.core.database import get_db_session
from app.schemas.history_schema import (
    TranslationHistoryClearResponse,
    TranslationHistoryDeleteResponse,
    TranslationHistoryItem,
    TranslationHistoryListResponse,
)
from app.services.history_service import (
    clear_history_records,
    delete_history_record,
    get_history_record,
    list_history_records,
)
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["History"])


@router.get("/history", response_model=TranslationHistoryListResponse)
async def list_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    q: str | None = Query(default=None, min_length=1, max_length=200),
    session: AsyncSession = Depends(get_db_session),
):
    keyword = q.strip() if q and q.strip() else None
    items, total = await list_history_records(
        session=session,
        page=page,
        page_size=page_size,
        keyword=keyword,
    )

    return TranslationHistoryListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


@router.get("/history/{history_id}", response_model=TranslationHistoryItem)
async def get_history(
    history_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    history = await get_history_record(session=session, history_id=history_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found.",
        )

    return history


@router.delete("/history/{history_id}", response_model=TranslationHistoryDeleteResponse)
async def delete_history(
    history_id: int,
    session: AsyncSession = Depends(get_db_session),
):
    deleted = await delete_history_record(session=session, history_id=history_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History record not found.",
        )

    return TranslationHistoryDeleteResponse(deleted=True, id=history_id)


@router.delete("/history", response_model=TranslationHistoryClearResponse)
async def clear_history(
    session: AsyncSession = Depends(get_db_session),
):
    deleted_count = await clear_history_records(session=session)

    return TranslationHistoryClearResponse(
        deleted=True,
        deleted_count=deleted_count,
    )
