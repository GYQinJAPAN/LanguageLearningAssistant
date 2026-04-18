from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TranslationHistoryCreate(BaseModel):
    source_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str


class TranslationHistoryItem(BaseModel):
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
    items: list[TranslationHistoryItem]
    # ge 是 "greater than or equal" 的缩写，意思是 大于或等于。
    # Field(...) 中的 ...（三个点）表示该字段是 必填的（没有默认值）
    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
