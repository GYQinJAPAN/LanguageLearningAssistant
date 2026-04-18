from app.models.translation_history import TranslationHistory
from app.schemas.history_schema import TranslationHistoryCreate, TranslationHistoryItem
from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession


# async def 协程函数，调用它不会立即执行内部代码，而是返回一个协程对象
# 只有用 await 调用它，才会真正开始执行并等待结果
async def create_history_record(
    session: AsyncSession,  # 异步数据库会话，用于执行数据库操作
    payload: TranslationHistoryCreate,  # 包含创建记录所需字段的数据对象
) -> TranslationHistory:

    history: TranslationHistory = TranslationHistory(**payload.model_dump())

    # 将新创建的记录对象添加到会话中，此时只是标记为“待插入”，还没有真正写入数据库
    session.add(history)

    await session.commit()

    # 提交后，数据库中会生成一些服务器端默认值（比如自增 ID、时间戳等）
    # 这里再次 await，等待数据库把最新的记录数据刷新到 history 对象中
    await session.refresh(history)

    # 返回已经包含完整字段（包括数据库自动生成字段）的记录对象
    return history


async def list_history_records(
    session: AsyncSession,  # 异步数据库会话
    page: int,  # 当前页码（从 1 开始）
    page_size: int,  # 每页记录数量
    keyword: str | None = None,  # 可选的搜索关键词，若为 None 则不进行过滤
) -> tuple[list[TranslationHistory], int]:  # 返回 (当前页记录列表, 符合条件的总记录数)
    filters = []  # 用于存放 SQL WHERE 条件的列表
    if keyword:
        pattern = f"%{keyword.strip()}%"
        filters.append(
            # or_ 表示多个字段中只要有一个匹配即可
            or_(
                TranslationHistory.source_text.ilike(pattern),
                TranslationHistory.translated_text.ilike(pattern),
                TranslationHistory.style_requested.ilike(pattern),
                TranslationHistory.style_applied.ilike(pattern),
                TranslationHistory.source_lang.ilike(pattern),
                TranslationHistory.target_lang.ilike(pattern),
            )
        )
    # 构建一个用于统计符合条件的总记录数的查询语句
    # select(func.count()) 表示 SELECT COUNT(*)
    # .select_from(TranslationHistory) 指定从翻译历史记录表中查询
    count_statement = select(func.count()).select_from(TranslationHistory)
    # 构建一个用于获取实际数据的查询语句，默认查询所有字段
    statement = select(TranslationHistory)

    if filters:
        # .where(*filters) 中的 * 将列表解包为多个参数，相当于 WHERE 条件1 OR 条件2 OR ...
        count_statement = count_statement.where(*filters)
        statement = statement.where(*filters)

    # 执行计数查询，并等待数据库返回结果
    # session.scalar() 用于获取单个值（第一行第一列），这里就是符合条件的总记录数
    total = await session.scalar(count_statement)

    # 执行分页数据查询，等待数据库返回结果
    # .order_by(...) 按创建时间和 ID 倒序排列，保证最新的记录在前面
    # .offset(...) 跳过前面若干条记录，实现分页!!!!!!
    # .limit(...) 限制返回的记录条数
    result = await session.execute(
        statement.order_by(
            TranslationHistory.created_at.desc(),
            TranslationHistory.id.desc(),
        )
        .offset((page - 1) * page_size)  # !!!!!!比如 page=2, page_size=10，则跳过前 10 条
        .limit(page_size)  # 只取 10 条
    )
    # result.scalars().all() 提取查询结果中的 ORM 对象并转为列表
    # total 可能为 None（比如表为空），此时用 or 0 保证返回整数 0

    return list(result.scalars().all()), total or 0


async def get_history_record(
    session: AsyncSession,
    history_id: int,
) -> TranslationHistory | None:
    return await session.get(TranslationHistory, history_id)


async def delete_history_record(
    session: AsyncSession,
    history_id: int,
) -> bool:
    history: TranslationHistoryItem = await session.get(TranslationHistory, history_id)

    if history is None:
        return False

    await session.delete(history)
    await session.commit()
    return True


async def clear_history_records(session: AsyncSession) -> int:
    result = await session.execute(delete(TranslationHistory))
    await session.commit()
    return result.rowcount or 0
