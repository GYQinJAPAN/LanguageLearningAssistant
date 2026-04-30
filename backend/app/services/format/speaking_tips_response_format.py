"""Structured output contract for speaking tips generation."""

SPEAKING_TIPS_STRESS_WORDS_MAX = 4
SPEAKING_TIPS_LINKING_NOTES_MAX = 2
SPEAKING_TIPS_OUTPUT_TOKENS = 500

SPEAKING_TIPS_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "translation_speaking_tips",
    "description": "Concise speaking tips for one selected translation variant.",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "stress_words",
            "linking_notes",
            "more_spoken_text",
            "note_text",
        ],
        "properties": {
            "stress_words": {
                "type": "array",
                "items": {"type": "string"},
                "maxItems": SPEAKING_TIPS_STRESS_WORDS_MAX,
            },
            "linking_notes": {
                "type": "array",
                "maxItems": SPEAKING_TIPS_LINKING_NOTES_MAX,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["phrase", "tip"],
                    "properties": {
                        "phrase": {"type": "string"},
                        "tip": {"type": "string"},
                    },
                },
            },
            "more_spoken_text": {
                "type": "string",
            },
            "note_text": {
                "type": "string",
            },
        },
    },
}
