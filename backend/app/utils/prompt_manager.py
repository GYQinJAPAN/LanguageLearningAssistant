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
        "Translate the user's text accurately and naturally into the target language.\n"
        "Output only the final translated text."
    )
    STYLE_KEY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

    def __init__(self, prompt_dir: Path | None = None) -> None:
        """
        初始化提示词管理器

        Args:
            prompt_dir: 存放提示词 .txt 文件的目录路径。
                       若未提供，则从应用配置 settings.PROMPT_DIR 读取。
        """
        if prompt_dir is None:
            prompt_dir = settings.PROMPT_DIR
        self.prompt_dir = prompt_dir

    def validate_style_key(self, style_name: str) -> str:
        """
        校验风格名称是否合法

        规则：
        - 不能为空或仅包含空白字符
        - 只能包含字母、数字、下划线、短横线，且必须以字母或数字开头
        - 长度 1~64 字符

        Args:
            style_name: 待校验的风格名称（可能包含首尾空白）

        Returns:
            去除首尾空白后的标准化风格名称

        Raises:
            ValueError: 风格名称不合法时抛出异常
        """
        style_key = style_name.strip()
        if not style_key:
            raise ValueError("style 不能为空。")
        if not self.STYLE_KEY_PATTERN.fullmatch(style_key):
            raise ValueError(
                "style 格式不合法，只允许字母、数字、下划线和短横线。"
            )
        return style_key

    def _prompt_path_for(self, style_name: str) -> Path:
        """
        根据风格名称生成对应的提示词文件路径，并进行路径穿越安全检查

        该方法确保生成的路径严格位于 prompt_dir 目录内，防止通过类似 '../etc/passwd'
        的恶意 style 名称访问系统其他文件。

        Args:
            style_name: 已经过校验的风格名称（不含扩展名）

        Returns:
            指向 {style_name}.txt 的绝对路径对象

        Raises:
            ValueError: 如果解析后的路径不在 prompt_dir 内，则抛出异常
        """
        prompt_dir = self.prompt_dir.resolve()  # 解析目录的绝对路径，避免符号链接干扰
        prompt_path = (prompt_dir / f"{style_name}.txt").resolve()  # 拼接文件路径并解析为绝对路径
        if prompt_path.parent != prompt_dir:
            raise ValueError("style 路径不合法。")
        return prompt_path

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

    def build_system_prompt(
            self,
            prompt_template: str,
            source_lang: str,
            target_lang: str,
    ) -> str:
        """Build the final system prompt sent to the LLM."""
        return f"""
                {prompt_template}

                Translation settings:
                - Source language: {source_lang}
                - Target language: {target_lang}

                Instructions:
                - If source language is 'auto', detect the source language
                  automatically.
                - Translate the user's text into the target language accurately
                  and naturally.
                - Output only the final translated result.
                """.strip()

    def list_styles(self) -> list[str]:
        """
       列出提示词目录下所有可用的风格名称

       扫描 prompt_dir 下的所有 .txt 文件，提取文件名（不含扩展名），
       并过滤掉不符合命名规范的文件。

       Returns:
           排序后的风格名称列表，默认风格（DEFAULT_STYLE）会排在第一位（如果存在）
       """
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
        # "Base_Prompt" 被识别为默认风格排第一，其余按字母序
        return sorted(
            style_names,
            key=lambda name: (name != self.DEFAULT_STYLE, name.lower()),
        )

    def get_default_style(self) -> str:
        return self.DEFAULT_STYLE

    def build_style_label(self, style_name: str) -> str:
        return style_name.replace("_", " ").replace("-", " ").title()
