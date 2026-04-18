"""Pydantic schemas for translation history APIs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TranslationHistoryCreate(BaseModel):
    """Fields required to persist a translation history record."""

    source_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str


class TranslationHistoryItem(BaseModel):
    """A translation history record returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    source_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str
    created_at: datetime


class TranslationHistoryListResponse(BaseModel):
    """Paginated translation history response."""

    items: list[TranslationHistoryItem]
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)


class TranslationHistoryDeleteResponse(BaseModel):
    """Response returned after deleting one history record."""

    deleted: bool
    id: int


class TranslationHistoryClearResponse(BaseModel):
    """Response returned after clearing all history records."""

    deleted: bool
    deleted_count: int = Field(..., ge=0)
