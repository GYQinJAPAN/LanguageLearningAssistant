"""Prompt file discovery, validation, and rendering utilities."""

import logging
import re
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


class PromptManager:
    """Manage prompt files, style validation, fallback, and prompt rendering."""

    DEFAULT_STYLE = "base_prompt"
    BUILTIN_FALLBACK_STYLE = "default_builtin"
    BUILTIN_FALLBACK_PROMPT = (
        "You are a professional translation assistant.\n"
        "Translate the user's text accurately and naturally into the target language."
    )
    TASK_DIR_NAME = "tasks"
    TASK_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
    BUILTIN_SINGLE_TASK = (
        "Translate the user's text into the target language accurately and naturally.\n"
        "Do not add explanations, notes, or quotation marks.\n"
        "Output only the final translated result."
    )
    STYLE_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

    def __init__(self, prompt_dir: Path | None = None) -> None:
        """Initialize the manager with the configured prompt directory."""
        if prompt_dir is None:
            prompt_dir = settings.PROMPT_DIR
        self.prompt_dir = prompt_dir

    def validate_style_key(self, style_name: str) -> str:
        """Validate and normalize a style key."""
        style_key = style_name.strip()
        if not style_key:
            raise ValueError("style 不能为空。")
        if not self.STYLE_KEY_PATTERN.fullmatch(style_key):
            raise ValueError("style 格式不合法，只允许字母、数字、下划线和短横线。")
        return style_key

    def _prompt_path_for(self, style_name: str) -> Path:
        """Return the prompt file path and reject paths outside prompt_dir."""
        prompt_dir = self.prompt_dir.resolve()
        prompt_path = (prompt_dir / f"{style_name}.txt").resolve()
        if prompt_path.parent != prompt_dir:
            raise ValueError("style 路径不合法。")
        return prompt_path

    def _task_path_for(self, task_name: str) -> Path:
        """Return a task template path and reject paths outside the task dir."""
        task_key = task_name.strip()
        if not self.TASK_KEY_PATTERN.fullmatch(task_key):
            raise ValueError("task template 格式不合法。")

        task_dir = (self.prompt_dir / self.TASK_DIR_NAME).resolve()
        task_path = (task_dir / f"{task_key}.txt").resolve()
        if task_path.parent != task_dir:
            raise ValueError("task template 路径不合法。")
        return task_path

    def load_prompt(self, style_name: str) -> tuple[str, str]:
        """Load the requested prompt or fall back only for valid missing styles."""
        style_key = self.validate_style_key(style_name)
        prompt_path = self._prompt_path_for(style_key)

        if prompt_path.exists():
            return style_key, prompt_path.read_text(encoding="utf-8")

        logger.warning(
            "Prompt file for style '%s' was not found. Falling back to '%s'.",
            style_key,
            self.DEFAULT_STYLE,
        )

        fallback_path = self._prompt_path_for(self.DEFAULT_STYLE)
        if fallback_path.exists():
            return self.DEFAULT_STYLE, fallback_path.read_text(encoding="utf-8")

        logger.warning("Default prompt file was not found. Using built-in fallback.")
        return self.BUILTIN_FALLBACK_STYLE, self.BUILTIN_FALLBACK_PROMPT

    def load_task_template(self, task_name: str) -> str:
        """Load a task template used with a style prompt."""
        task_path = self._task_path_for(task_name)
        if task_path.exists():
            return task_path.read_text(encoding="utf-8")

        if task_name == "translate_single":
            logger.warning("Single-translation task template was not found. Using built-in fallback.")
            return self.BUILTIN_SINGLE_TASK

        raise ValueError(f"task template 不存在：{task_name}")

    def build_system_prompt(
        self,
        style_template: str,
        task_template: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """Build the final system prompt sent to the LLM."""
        return f"""
                Style requirements:
                {style_template}

                Translation settings:
                - Source language: {source_lang}
                - Target language: {target_lang}

                Shared instructions:
                - If source language is 'auto', detect the source language
                  automatically.
                - Translate from the source language into the target language.
                - The target language is mandatory. Every translated result must
                  be written in the target language, not rewritten in the source
                  language.
                - If the target language is Japanese or 日语, every translated
                  result must be Japanese.
                - Preserve the original meaning faithfully.
                - Apply the selected style requirements to every translated result.

                Task instructions:
                {task_template}
                """.strip()

    def list_styles(self) -> list[str]:
        """Return valid prompt style names, with the default style first."""
        if not self.prompt_dir.exists():
            logger.warning("Prompt directory does not exist: %s", self.prompt_dir)
            return [self.DEFAULT_STYLE]

        style_names: set[str] = set()
        for file in self.prompt_dir.glob("*.txt"):
            if not file.is_file():
                continue

            style_name = file.stem
            if not self.STYLE_KEY_PATTERN.fullmatch(style_name):
                logger.warning("Skipping invalid prompt file name: %s", file.name)
                continue

            style_names.add(style_name)

        if not style_names:
            style_names.add(self.DEFAULT_STYLE)

        return sorted(
            style_names,
            key=lambda name: (name != self.DEFAULT_STYLE, name.lower()),
        )

    def get_default_style(self) -> str:
        """Return the configured default style key."""
        return self.DEFAULT_STYLE

    def build_style_label(self, style_name: str) -> str:
        """Convert a style key into a display label."""
        return style_name.replace("_", " ").replace("-", " ").title()
