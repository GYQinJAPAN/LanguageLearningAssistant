from app.core.config import settings
from app.schemas.history_schema import (
    TranslationHistoryCreate,
    TranslationVariantCreate,
)
from app.schemas.translate_schema import (
    TranslateRequest,
    TranslateResponse,
    TranslationVariant,
)
from app.services.format.learning_response_format import (
    LEARNING_MIN_OUTPUT_TOKENS,
    LEARNING_VARIANT_RESPONSE_FORMAT,
)
from app.services.history_service import create_history_record
from app.services.llm_service import translate_and_rewrite
from app.services.parsers.learning_variant_parser import parse_learning_variants
from app.utils.prompt_manager import PromptManager
from sqlalchemy.ext.asyncio import AsyncSession

prompt_manager: PromptManager = PromptManager()


async def handle_translation_request(
    request: TranslateRequest,
    session: AsyncSession,
) -> TranslateResponse:
    actual_style, style_template = prompt_manager.load_prompt(request.style)
    task_template: str = prompt_manager.load_task_template(
        "translate_learning_mode" if request.result_mode == "learning" else "translate_single"
    )

    system_prompt: str = prompt_manager.build_system_prompt(
        style_template=style_template,
        task_template=task_template,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
    )

    raw_result_text = await translate_and_rewrite(
        user_text=request.text,
        system_prompt=system_prompt,
        max_output_tokens=(
            max(settings.OPENAI_MAX_TOKENS, LEARNING_MIN_OUTPUT_TOKENS) if request.result_mode == "learning" else None
        ),
        text_format=(LEARNING_VARIANT_RESPONSE_FORMAT if request.result_mode == "learning" else None),
    )
    variants: list[TranslationVariant] | None = None
    result_text = raw_result_text

    if request.result_mode == "learning":
        # reuse
        variants: list[TranslationVariant] = parse_learning_variants(raw_result_text)
        natural_variant = next(variant for variant in variants if variant.variant_type == "natural")
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

    response_variants = variants
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
    return response
