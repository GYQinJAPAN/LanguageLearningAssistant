from app.core.config import PROMPT_DIR
from app.schemas.translate_schema import TranslateResponse, TranslateRequest
from app.services.llm_service import translate_and_rewrite
from app.utils.prompt_manager import PromptManager
from fastapi import APIRouter, HTTPException

"""
翻译 API
"""
# 定义 API
router: APIRouter = APIRouter(prefix="/api/v1", tags=["Translation"])
prompt_manager: PromptManager = PromptManager()


@router.post("/translate", response_model=TranslateResponse)
async def translate_endpoint(request: TranslateRequest):

    try:
        actual_style, prompt_template = prompt_manager.load_prompt(request.style)

        system_prompt = prompt_manager.build_system_prompt(
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
