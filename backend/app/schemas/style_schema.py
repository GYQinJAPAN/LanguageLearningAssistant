from pydantic import BaseModel

"""
style 数据结构
"""


class StyleItem(BaseModel):
    """
    表示一个 style

    例如：
    {
      "key": "casual",
      "label": "Casual"
    }
    """

    key: str
    label: str


class StyleListResponse(BaseModel):
    """
    表示 /styles 接口返回的数据

    例如：
    {
      "styles": [
        {"key": "base_prompt", "label": "Base Prompt"},
        {"key": "casual", "label": "Casual"},
        {"key": "polite", "label": "Polite"}
      ],
      "default_style": "base_prompt"
    }
    """

    styles: list[StyleItem]
    default_style: str
