"""Translation request orchestration and history persistence."""

import logging

from app.core.config import settings
from app.schemas.history_schema import TranslationHistoryCreate, TranslationVariantCreate
from app.schemas.translate_schema import TranslateRequest, TranslateResponse, TranslationVariant
from app.services.format.learning_response_format import (
    LEARNING_MIN_OUTPUT_TOKENS,
    LEARNING_VARIANT_RESPONSE_FORMAT,
)
from app.services.history_service import create_history_record
from app.services.llm_service import translate_and_rewrite
from app.services.parsers.learning_variant_parser import parse_learning_variants
from app.utils.json_payload import StructuredOutputError
from app.utils.prompt_manager import PromptManager
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
prompt_manager: PromptManager = PromptManager()


async def handle_translation_request(
    request: TranslateRequest,
    session: AsyncSession,
) -> TranslateResponse:
    """Translate one request, parse learning output when needed, and persist history."""
    logger.info(
        "Translation request received. mode=%s style=%s source_lang=%s target_lang=%s text_length=%s",
        request.result_mode,
        request.style,
        request.source_lang,
        request.target_lang,
        len(request.text),
    )

    actual_style, style_template = prompt_manager.load_prompt(request.style)
    task_name = "translate_learning_mode" if request.result_mode == "learning" else "translate_single"
    task_template = prompt_manager.load_task_template(task_name)
    logger.debug(
        "Translation prompt resolved. requested_style=%s applied_style=%s task=%s",
        request.style,
        actual_style,
        task_name,
    )

    system_prompt = prompt_manager.build_system_prompt(
        style_template=style_template,
        task_template=task_template,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )

    logger.info("Calling LLM for translation. mode=%s applied_style=%s", request.result_mode, actual_style)
    raw_result_text = await translate_and_rewrite(
        user_text=request.text,
        system_prompt=system_prompt,
        max_output_tokens=(
            max(settings.OPENAI_MAX_TOKENS, LEARNING_MIN_OUTPUT_TOKENS) if request.result_mode == "learning" else None
        ),
        text_format=(LEARNING_VARIANT_RESPONSE_FORMAT if request.result_mode == "learning" else None),
    )
    logger.info(
        "LLM translation completed. mode=%s output_length=%s",
        request.result_mode,
        len(raw_result_text),
    )

    variants: list[TranslationVariant] | None = None
    result_text = raw_result_text

    if request.result_mode == "learning":
        variants = parse_learning_variants(raw_result_text)
        logger.info("Learning-mode variants parsed successfully. count=%s", len(variants))
        logger.debug("Learning-mode variant types=%s", [variant.variant_type for variant in variants])
        natural_variant = next((variant for variant in variants if variant.variant_type == "natural"), None)
        if natural_variant is None:
            logger.warning("Learning-mode output did not include the natural variant.")
            raise StructuredOutputError("Learning mode output is missing the 'natural' variant.")
        result_text = natural_variant.translated_text

    history = await create_history_record(
        session=session,
        payload=TranslationHistoryCreate(
            source_text=request.text,
            translated_text=result_text,
            style_requested=request.style,
            style_applied=actual_style,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
        ),
        variants=[
            TranslationVariantCreate(
                variant_type=variant.variant_type,
                translated_text=variant.translated_text,
                short_note=variant.short_note,
                sort_order=variant.sort_order,
            )
            for variant in variants or []
        ],
    )
    logger.info("History save completed for translation. history_id=%s", history.id)

    response_variants: list[TranslationVariant] | None = variants
    if variants:
        persisted_variant_ids = {variant.variant_type: variant.id for variant in history.variants}
        response_variants = [
            variant.model_copy(update={"variant_id": persisted_variant_ids.get(variant.variant_type)})
            for variant in variants
        ]

    response = TranslateResponse(
        original_text=request.text,
        translated_text=result_text,
        style_requested=request.style,
        style_applied=actual_style,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        result_mode=request.result_mode,
        variants=response_variants,
    )
    logger.debug(
        "Translation response prepared. history_id=%s variant_count=%s",
        history.id,
        len(response_variants or []),
    )
    return response
