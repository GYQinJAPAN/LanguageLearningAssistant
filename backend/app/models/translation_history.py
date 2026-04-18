"""Database model for persisted translation history."""

from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class TranslationHistory(Base):
    """Persisted source text, translated text, style, and language metadata."""

    __tablename__ = "translation_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    style_requested: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    style_applied: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_lang: Mapped[str] = mapped_column(String(64), nullable=False)
    target_lang: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
