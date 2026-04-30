"""Structured output contract for learning-mode translation variants."""

VARIANT_ORDER = ("written", "natural", "spoken")
VARIANT_LABELS = {
    "written": "书面版",
    "natural": "自然版",
    "spoken": "口语版",
}
LEARNING_MIN_OUTPUT_TOKENS = 900
LEARNING_VARIANT_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "translation_learning_variants",
    "description": ("Three target-language translation variants for learning mode."),
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["variants"],
        "properties": {
            "variants": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "variant_type",
                        "translated_text",
                        "short_note",
                    ],
                    "properties": {
                        "variant_type": {
                            "type": "string",
                            "enum": list(VARIANT_ORDER),
                        },
                        "translated_text": {
                            "type": "string",
                        },
                        "short_note": {
                            "type": "string",
                        },
                    },
                },
            }
        },
    },
}
