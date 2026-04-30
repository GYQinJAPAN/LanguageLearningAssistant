"""Pydantic schemas for speaking tips APIs."""

from pydantic import BaseModel, Field


class SpeakingTipLinkingNote(BaseModel):
    """One short linking or flow reminder."""

    phrase: str
    tip: str


class SpeakingTipsPayload(BaseModel):
    """Normalized speaking tips content."""

    stress_words: list[str] = Field(default_factory=list)
    linking_notes: list[SpeakingTipLinkingNote] = Field(default_factory=list)
    more_spoken_text: str
    note_text: str = ""


class SpeakingTipsResponse(SpeakingTipsPayload):
    """Response returned after loading or generating speaking tips."""

    variant_id: int = Field(..., ge=1)
    cached: bool
