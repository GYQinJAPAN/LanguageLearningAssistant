"""OpenAI client access and translation service functions."""

import logging

from app.core.config import settings
from app.utils.prompt_manager import PromptManager
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
_client: AsyncOpenAI | None = None
prompt_manager: PromptManager = PromptManager()


def get_openai_client() -> AsyncOpenAI:
    """Return a cached OpenAI async client configured from settings."""
    global _client

    if not settings.OPENAI_API_KEY:
        logger.error("OpenAI API key is not configured.")
        raise RuntimeError("OpenAI API key is not configured. Check backend/.env.")

    if _client is None:
        client_options = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_options["base_url"] = settings.OPENAI_BASE_URL

        _client = AsyncOpenAI(**client_options)

    return _client


async def _generate_text_response(
    *,
    user_text: str,
    instructions: str,
    max_output_tokens: int | None = None,
    text_format: dict | None = None,
) -> str:
    """Send one text-generation request to the LLM and return the text output."""
    try:
        response_options = {
            "model": settings.OPENAI_MODEL,
            "instructions": instructions,
            "input": user_text,
            "temperature": settings.OPENAI_TEMPERATURE,
            "max_output_tokens": max_output_tokens or settings.OPENAI_MAX_TOKENS,
        }
        if text_format:
            response_options["text"] = {"format": text_format}

        response = await get_openai_client().responses.create(**response_options)
        return (response.output_text or "").strip()
    except RuntimeError:
        raise
    except Exception as exc:
        logger.exception("OpenAI API call failed.")
        raise RuntimeError("The translation service is temporarily unavailable.") from exc


async def translate_and_rewrite(
    user_text: str,
    system_prompt: str,
    max_output_tokens: int | None = None,
    text_format: dict | None = None,
) -> str:
    """Send the prompt and user text to the LLM and return the final text."""
    return await _generate_text_response(
        user_text=user_text,
        instructions=system_prompt,
        max_output_tokens=max_output_tokens,
        text_format=text_format,
    )


async def generate_speaking_tips(
    *,
    source_lang: str,
    target_lang: str,
    source_text: str,
    variant_type: str,
    translated_text: str,
    max_output_tokens: int | None = None,
    text_format: dict | None = None,
) -> str:
    """Generate speaking tips for one selected learning-mode variant."""
    task_template = prompt_manager.load_task_template("speaking_tips")
    instructions = task_template.format(
        source_lang=source_lang,
        target_lang=target_lang,
        source_text=source_text,
        variant_type=variant_type,
        translated_text=translated_text,
    )
    return await _generate_text_response(
        user_text=translated_text,
        instructions=instructions,
        max_output_tokens=max_output_tokens,
        text_format=text_format,
    )
