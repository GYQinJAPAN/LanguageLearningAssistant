"""Pydantic schemas for translation requests and responses."""

from typing import Literal

from pydantic import BaseModel, Field

ResultMode = Literal["single", "learning"]
VariantType = Literal["written", "natural", "spoken"]


class TranslateRequest(BaseModel):
    """Request body for translating user text."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="用户需要翻译的原文",
    )
    style: str = Field(
        default="base_prompt",
        description="翻译风格，例如: base_prompt, casual, polite",
    )
    source_lang: str = Field(default="auto", description="源语言，默认 auto 表示自动识别")
    target_lang: str = Field(default="English", description="目标语言，默认翻译为 English")
    result_mode: ResultMode = Field(
        default="single",
        description="结果模式：single 返回单个结果，learning 返回 written/natural/spoken 三个版本",
    )


class TranslationVariant(BaseModel):
    """One learning-mode translation variant."""

    variant_type: VariantType
    label: str
    variant_id: int | None = Field(default=None, ge=1)
    translated_text: str
    short_note: str
    sort_order: int = Field(default=0, ge=0)


class TranslateResponse(BaseModel):
    """Translation result returned to the client."""

    original_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str
    result_mode: ResultMode = "single"
    variants: list[TranslationVariant] | None = None
