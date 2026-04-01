from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import PROMPT_DIR
from app.services.llm_service import translate_and_rewrite

router = APIRouter(prefix="/api/v1", tags=["Translation"])


class TranslateRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=2000, description="用户需要翻译的原文"
    )
    style: str = Field(
        default="base_prompt", description="重写语气，例如: casual, polite, flirty"
    )


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    style_applied: str


def load_prompt(style_name: str) -> str:
    prompt_path = PROMPT_DIR / f"{style_name}.txt"

    if not prompt_path.exists():
        prompt_path = PROMPT_DIR / "base_prompt.txt"

    if not prompt_path.exists():
        return "You are a helpful translation assistant. Translate the following text to natural English."

    return prompt_path.read_text(encoding="utf-8")


@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(request: TranslateRequest):
    try:
        system_prompt = load_prompt(request.style)

        result_text = await translate_and_rewrite(
            user_text=request.text, system_prompt=system_prompt
        )

        return TranslateResponse(
            original_text=request.text,
            translated_text=result_text,
            style_applied=request.style,
        )

    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")
