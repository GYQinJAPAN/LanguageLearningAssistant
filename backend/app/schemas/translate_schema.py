"""Pydantic schemas for translation requests and responses."""

from pydantic import BaseModel, Field


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


class TranslateResponse(BaseModel):
    """Translation result returned to the client."""

    original_text: str
    translated_text: str
    style_requested: str
    style_applied: str
    source_lang: str
    target_lang: str
