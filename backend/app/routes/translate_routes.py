import logging

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.schemas.translate_schema import TranslateRequest, TranslateResponse
from app.services.llm_service import translate_and_rewrite
from app.utils.prompt_manager import PromptManager

logger = logging.getLogger(__name__)
router: APIRouter = APIRouter(prefix=settings.api_prefix, tags=["Translation"])
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

    except ValueError as exc:
        logger.warning("Invalid translate request: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except RuntimeError as exc:
        logger.warning("Translation failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception:
        logger.exception("Unexpected translation error.")
        raise HTTPException(status_code=500, detail="服务器内部错误，请稍后再试。")
