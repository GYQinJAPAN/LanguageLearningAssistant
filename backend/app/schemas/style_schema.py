"""Pydantic schemas for translation style APIs."""

from pydantic import BaseModel


class StyleItem(BaseModel):
    """A translation style option."""

    key: str
    label: str


class StyleListResponse(BaseModel):
    """Available styles and the default style key."""

    styles: list[StyleItem]
    default_style: str
