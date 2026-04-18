from datetime import datetime, timezone

from app.core.database import Base
from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


# 定义一个继承自 Base 的类，它就会自动对应数据库中的一张表
class TranslationHistory(Base):
    # 指定这张表在数据库里的实际名称
    __tablename__ = "translation_history"

    # id：整数,主键,同时自动创建索引
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # source_text：源文本， Text 类型（适合存长文本），不能为空
    source_text: Mapped[str] = mapped_column(Text, nullable=False)

    # translated_text：翻译后的文本，Text 类型，不能为空
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)

    # style_requested：用户请求的翻译风格，最长 64 个字符，建立索引
    style_requested: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # style_applied：实际应用到的翻译风格，最长 64 字符，建立索引
    style_applied: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # source_lang：源语言代码（如 "zh", "en"），最长 64 字符，不能为空
    source_lang: Mapped[str] = mapped_column(String(64), nullable=False)

    # target_lang：目标语言代码，最长 64 字符，不能为空
    target_lang: Mapped[str] = mapped_column(String(64), nullable=False)

    # created_at：记录创建的时间戳，带时区信息（UTC）
    # default 参数指定：如果不手动传入时间，就自动用当前 UTC 时间填充
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),  # 支持时区的日期时间类型
        default=lambda: datetime.now(timezone.utc),  # 默认值生成函数：调用当前 UTC 时间
        nullable=False,  # 不能为空
        index=True,  # 创建索引，方便按时间排序或过滤
    )
