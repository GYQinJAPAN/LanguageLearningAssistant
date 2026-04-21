"""Database model for persisted translation history."""

from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

VARIANT_LABELS = {
    "written": "书面版",
    "natural": "自然版",
    "spoken": "口语版",
}


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
    variants: Mapped[list["TranslationVariant"]] = relationship(
        back_populates="history",
        cascade="all, delete-orphan",
        order_by="TranslationVariant.sort_order",
    )


class TranslationVariant(Base):
    """Persisted learning-mode translation variant for one history record."""

    __tablename__ = "translation_variants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    history_id: Mapped[int] = mapped_column(
        ForeignKey("translation_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    variant_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    short_note: Mapped[str] = mapped_column(Text, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    history: Mapped[TranslationHistory] = relationship(back_populates="variants")

    @property
    def label(self) -> str:
        """Return a display label for the variant type."""
        return VARIANT_LABELS.get(self.variant_type, self.variant_type)
