"""Helpers for extracting structured JSON payloads from LLM output."""

import json
import logging

logger = logging.getLogger(__name__)


class StructuredOutputError(RuntimeError):
    """Raised when structured LLM output cannot be parsed or normalized."""


def extract_json_payload(raw_text: str) -> object:
    """Parse a JSON object or array from raw LLM output.

    Raises:
        StructuredOutputError: If no valid JSON payload can be extracted.
    """
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.debug("Direct JSON parsing failed. output_length=%s", len(text))
        starts = [index for index in (text.find("{"), text.find("[")) if index >= 0]
        if not starts:
            logger.warning("Structured output did not contain a JSON payload.")
            raise StructuredOutputError("Structured output did not contain a JSON payload.")

        start = min(starts)
        end = max(text.rfind("}"), text.rfind("]"))
        if end <= start:
            logger.warning("Structured output JSON boundaries were incomplete.")
            raise StructuredOutputError("Structured output JSON was incomplete.")

        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            logger.warning("Structured output JSON parsing failed after fallback extraction.")
            raise StructuredOutputError("Structured output contained invalid JSON.") from exc
