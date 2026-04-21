"""Pydantic schemas for translation history APIs."""

from datetime import datetime

from app.schemas.translate_schema import TranslationVariant
from pydantic import BaseModel, ConfigDict, Field


class TranslationHistoryCreate(BaseModel):
    """Fields required to persist a translation history record."""

    source_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str


class TranslationVariantCreate(BaseModel):
    """Fields required to persist one learning-mode variant."""

    variant_type: str
    translated_text: str
    short_note: str
    sort_order: int = 0


class TranslationHistoryVariantItem(TranslationVariant):
    """A learning-mode variant returned by history APIs."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


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
    variants: list[TranslationHistoryVariantItem] = Field(default_factory=list)


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
