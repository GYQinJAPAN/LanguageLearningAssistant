from pathlib import Path

from app.core.config import PROMPT_DIR


class PromptManager:
    """
    统一管理 prompt 文件的读取、fallback、style 列表获取，
    以及 system prompt 的构造逻辑。
    """

    DEFAULT_STYLE = "base_prompt"
    BUILTIN_FALLBACK_STYLE = "default_builtin"
    BUILTIN_FALLBACK_PROMPT = (
        "You are a professional translation assistant.\n"
        "Translate the user's text accurately and naturally into the target language.\n"
        "Output only the final translated text."
    )

    def __init__(self, prompt_dir: Path = PROMPT_DIR) -> None:
        self.prompt_dir = prompt_dir

    def load_prompt(self, style_name: str) -> tuple[str, str]:
        """
        根据 style_name 读取对应 prompt。
        如果不存在，则回退到 base_prompt.txt。
        如果 base_prompt.txt 也不存在，则回退到内置默认 prompt。

        Returns:
            tuple[str, str]:
                - 实际应用的 style 名称
                - prompt 文本内容
        """
        prompt_path = self.prompt_dir / f"{style_name}.txt"

        if prompt_path.exists():
            return style_name, prompt_path.read_text(encoding="utf-8")

        fallback_path = self.prompt_dir / f"{self.DEFAULT_STYLE}.txt"
        if fallback_path.exists():
            return self.DEFAULT_STYLE, fallback_path.read_text(encoding="utf-8")

        return self.BUILTIN_FALLBACK_STYLE, self.BUILTIN_FALLBACK_PROMPT

    def build_system_prompt(
        self,
        prompt_template: str,
        source_lang: str,
        target_lang: str,
    ) -> str:
        """
        基于 prompt 模板和语言参数，构造最终发送给 LLM 的 system prompt。
        """
        return f"""
                {prompt_template}
                
                Translation settings:
                - Source language: {source_lang}
                - Target language: {target_lang}
                
                Instructions:
                - If source language is 'auto', detect the source language automatically.
                - Translate the user's text into the target language accurately and naturally.
                - Output only the final translated result.
                """.strip()

    def list_styles(self) -> list[str]:
        """
        返回 prompts 目录下所有可用的 style 名称（不含 .txt 后缀）。
        按字母顺序排序。
        """
        if not self.prompt_dir.exists():
            return []

        style_names = [file.stem for file in self.prompt_dir.glob("*.txt")]
        style_names.sort()
        return style_names

    def get_default_style(self) -> str:
        """
        返回默认 style 名称。
        """
        return self.DEFAULT_STYLE

    def build_style_label(self, style_name: str) -> str:
        """
        将 style key 转成适合前端显示的 label。
        例如:
            base_prompt -> Base Prompt
            casual -> Casual
        """
        return style_name.replace("_", " ").title()
