"""Validation and normalization for learning-mode structured output."""

import logging

from app.schemas.translate_schema import TranslationVariant
from app.services.format.learning_response_format import VARIANT_LABELS, VARIANT_ORDER
from app.utils.json_payload import StructuredOutputError, extract_json_payload
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def _raise_parse_error(message: str) -> None:
    """Log and raise a normalized learning-mode parse error."""
    logger.warning("Learning-mode structured output validation failed: %s", message)
    raise StructuredOutputError(message)


def parse_learning_variants(raw_text: str) -> list[TranslationVariant]:
    """Validate and normalize the three learning-mode variants.

    Raises:
        StructuredOutputError: If the payload shape or content is invalid.
    """
    payload = extract_json_payload(raw_text)
    items = payload.get("variants") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        _raise_parse_error("Learning mode output must include a 'variants' array.")
    if len(items) != len(VARIANT_ORDER):
        _raise_parse_error("Learning mode output must contain exactly three variants.")

    variants_by_type: dict[str, dict[str, object]] = {}
    for item in items:
        if not isinstance(item, dict):
            _raise_parse_error("Each learning mode variant must be an object.")

        variant_type = item.get("variant_type")
        if variant_type not in VARIANT_ORDER:
            _raise_parse_error(f"Learning mode output contained an unknown variant_type: {variant_type}.")
        if variant_type in variants_by_type:
            _raise_parse_error(f"Learning mode output contained a duplicate variant_type: {variant_type}.")
        variants_by_type[variant_type] = item

    variants: list[TranslationVariant] = []
    for sort_order, variant_type in enumerate(VARIANT_ORDER):
        item = variants_by_type.get(variant_type)
        if item is None:
            _raise_parse_error(f"Learning mode output is missing the '{variant_type}' variant.")

        normalized: dict[str, object] = {
            "variant_type": item.get("variant_type"),
            "label": VARIANT_LABELS[variant_type],
            "translated_text": item.get("translated_text"),
            "short_note": item.get("short_note"),
            "sort_order": sort_order,
        }
        try:
            variant = TranslationVariant.model_validate(normalized)
        except ValidationError as exc:
            logger.warning(
                "Learning-mode structured output model validation failed for variant_type=%s",
                variant_type,
            )
            raise StructuredOutputError("Learning mode output contained invalid variant fields.") from exc
        if not variant.translated_text.strip() or not variant.short_note.strip():
            _raise_parse_error(f"Learning mode variant '{variant_type}' cannot be empty.")
        variants.append(variant)

    return variants
