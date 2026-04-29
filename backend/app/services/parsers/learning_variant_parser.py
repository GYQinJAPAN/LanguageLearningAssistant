from app.schemas.translate_schema import TranslationVariant
from app.services.format.learning_response_format import VARIANT_LABELS, VARIANT_ORDER
from app.utils.json_payload import extract_json_payload


def parse_learning_variants(raw_text: str) -> list[TranslationVariant]:
    """Validate and normalize the three learning-mode variants."""
    payload = extract_json_payload(raw_text)
    items = payload.get("variants") if isinstance(payload, dict) else payload
    if not isinstance(items, list):
        raise RuntimeError("学习模式返回格式无效：variants 必须是数组。")
    if len(items) != len(VARIANT_ORDER):
        raise RuntimeError("学习模式返回格式无效：必须恰好返回 3 个版本。")

    variants_by_type: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict):
            raise RuntimeError("学习模式返回格式无效：每个 variant 必须是对象。")

        variant_type = item.get("variant_type")
        if variant_type not in VARIANT_ORDER:
            raise RuntimeError(f"学习模式返回格式无效：未知版本类型：{variant_type}")
        if variant_type in variants_by_type:
            raise RuntimeError(f"学习模式返回格式无效：variant_type 重复：{variant_type}")
        variants_by_type[variant_type] = item

    variants: list[TranslationVariant] = []
    for sort_order, variant_type in enumerate(VARIANT_ORDER):
        item: dict = variants_by_type.get(variant_type)
        if item is None:
            raise RuntimeError(f"学习模式返回格式无效：缺少 {variant_type}。")

        normalized = {
            "variant_type": item.get("variant_type"),
            "label": VARIANT_LABELS[variant_type],
            "translated_text": item.get("translated_text"),
            "short_note": item.get("short_note"),
            "sort_order": sort_order,
        }
        variant = TranslationVariant.model_validate(normalized)
        if not variant.translated_text.strip() or not variant.short_note.strip():
            raise RuntimeError(f"学习模式返回格式无效：{variant_type} 内容不能为空。")
        variants.append(variant)

    return variants
