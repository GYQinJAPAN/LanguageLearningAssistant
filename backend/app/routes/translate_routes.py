from fastapi import APIRouter, HTTPException

from app.core.config import PROMPT_DIR
from app.schemas.translate_schema import TranslateResponse, TranslateRequest
from app.services.llm_service import translate_and_rewrite

"""
翻译 API
"""
# 定义 API
router: APIRouter = APIRouter(prefix="/api/v1", tags=["Translation"])


@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(request: TranslateRequest):
    try:
        actual_style, prompt_template = load_prompt(request.style)

        system_prompt = build_system_prompt(
            prompt_template=prompt_template,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

        result_text = await translate_and_rewrite(
            user_text=request.text,
            system_prompt=system_prompt,
        )

        return TranslateResponse(
            original_text=request.text,
            translated_text=result_text,
            style_requested=request.style,
            style_applied=actual_style,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        )

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


def load_prompt(style_name: str) -> tuple[str, str]:
    prompt_path = PROMPT_DIR / f"{style_name}.txt"

    if prompt_path.exists():
        return style_name, prompt_path.read_text(encoding="utf-8")

    fallback_path = PROMPT_DIR / "base_prompt.txt"
    if fallback_path.exists():
        return "base_prompt", fallback_path.read_text(encoding="utf-8")

    return (
        "default_builtin",
        (
            "You are a professional translation assistant.\n"
            "Translate the user's text accurately and naturally into the target language.\n"
            "Output only the final translated text."
        ),
    )


def build_system_prompt(
    prompt_template: str,
    source_lang: str,
    target_lang: str,
) -> str:
    return f"""
{prompt_template}

Translation settings:
- Source language: {source_lang}
- Target language: {target_lang}

Instructions:
- If source language is 'auto', detect the source language automatically.
- Translate the user's text into the target language accurately and naturally.
- Output only the final translated result.
""".strip()
