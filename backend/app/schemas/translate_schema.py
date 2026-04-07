from pydantic import BaseModel, Field

"""翻译请求/响应结构"""


class TranslateRequest(BaseModel):
    text: str = Field(
        ..., min_length=1, max_length=2000, description="用户需要翻译的原文"
    )
    style: str = Field(
        default="base_prompt", description="翻译风格，例如: base_prompt, casual, polite"
    )
    # TODO 前端:源语言下拉框
    source_lang: str = Field(
        default="auto", description="源语言，默认 auto 表示自动识别"
    )
    target_lang: str = Field(
        default="English", description="目标语言，默认翻译为 English"
    )


class TranslateResponse(BaseModel):
    original_text: str  # 原文
    translated_text: str  # 翻译后的结果
    style_requested: str  # 前端请求的 style
    style_applied: str  # 后端实际生效的 style
    source_lang: str  # 请求中指定的源语言
    target_lang: str  # 目标语言
