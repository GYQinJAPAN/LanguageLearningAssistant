import logging

from app.core.config import settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)
_client: AsyncOpenAI | None = None


def get_openai_client() -> AsyncOpenAI:
    global _client

    if not settings.OPENAI_API_KEY:
        logger.error("OpenAI API key is not configured.")
        raise RuntimeError("OpenAI API key 未配置，请检查后端 .env。")

    if _client is None:
        client_options = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            client_options["base_url"] = settings.OPENAI_BASE_URL

        _client = AsyncOpenAI(**client_options)

    return _client


async def translate_and_rewrite(
    user_text: str,
    system_prompt: str,
) -> str:
    """Send the prompt and user text to the LLM and return the final text."""
    try:
        response = await get_openai_client().chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=settings.OPENAI_TEMPERATURE,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""

    except RuntimeError:
        raise
    except Exception:
        logger.exception("OpenAI API call failed.")
        raise RuntimeError("翻译服务暂时不可用，请稍后再试。")
