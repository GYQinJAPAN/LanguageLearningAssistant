from collections.abc import AsyncGenerator
from pathlib import Path

from app.core.config import settings
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


# ========== 1. 定义 ORM 模型的基类 ==========
class Base(DeclarativeBase):
    """
    所有数据库模型类都必须继承这个 Base。
    这样 SQLAlchemy 就能自动发现所有继承它的类，并据此创建/映射表结构。
    """

    pass


# ========== 2. 创建异步数据库引擎 ==========
# create_async_engine 根据 DATABASE_URL 创建异步引擎对象。
# 引擎负责 管理数据库连接池，所有数据库操作最终都由它来执行。
engine = create_async_engine(settings.DATABASE_URL, future=True)

# ========== 3. 创建异步会话工厂 ==========
# async_sessionmaker 是一个工厂函数，每次调用它都会生成一个"新的" AsyncSession 实例。
# expire_on_commit=False 表示提交事务后，不会将会话中的对象标记为“过期”。
# 这可以避免在后续访问对象属性时,再次查询数据库（适合异步环境）。
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# ========== 4. 辅助函数：确保 SQLite 数据库文件的父目录存在 ==========
def ensure_sqlite_parent_dir() -> None:
    """
    如果使用 SQLite 数据库且指定了文件路径（而非内存数据库），
    则自动创建该文件所在的父目录，避免因目录不存在而报错。
    """

    # 将配置中的 DATABASE_URL 解析成 URL 对象
    url = make_url(settings.DATABASE_URL)

    # 仅处理 SQLite 驱动（例如 sqlite:///./data/app.db）
    # 协议头	sqlite:///
    # 遇到非 SQLite 的驱动（比如 PostgreSQL、MySQL），这个函数直接退出，什么都不做。
    if not url.drivername.startswith("sqlite"):
        return

    # 获取 数据库文件路径部分（例如 ./data/app.db）
    database_path = url.database

    if not database_path or database_path == ":memory:":
        return

    # 创建父目录：expanduser 处理 ~ 符号，expanduser() 会把它展开成绝对路径。
    # parents=True 递归创建，如果父目录也不存在就连父目录一起创建.
    # exist_ok=True 目录已存在也不报错
    Path(database_path).expanduser().parent.mkdir(parents=True, exist_ok=True)


# ========== 5. 初始化数据库（自动创建所有表） ==========
async def init_db() -> None:
    """
    在应用启动时调用，用于自动创建数据库中尚未存在的表。
    它会先确保 SQLite 文件目录存在，然后根据所有已导入的模型类（继承 Base）生成 CREATE TABLE 语句。
    """
    # 确保目录存在
    ensure_sqlite_parent_dir()

    # 导入 app.models 包，触发所有模型类的注册（让 SQLAlchemy 知道有哪些表需要创建）
    # 这里使用 import 而非常规导入，是为了避免循环引用，并在运行时执行模型定义。
    # noqa: F401 告诉 linter 忽略“未使用的导入”警告。
    import app.models  # noqa: F401

    async with engine.begin() as conn:
        # conn.run_sync() 可以在异步连接中,运行同步代码。
        # Base.metadata.create_all 是同步方法，它根据已注册的模型类生成并执行 CREATE TABLE 语句。
        await conn.run_sync(Base.metadata.create_all)


# ========== 6. 获取数据库会话的依赖函数（供 FastAPI 路由使用） ==========
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    这是一个异步生成器函数，用于在 FastAPI 的依赖注入中提供数据库会话。
    每次请求会创建一个新的 AsyncSession，并在请求结束后自动关闭会话。
    """
    # 通过会话工厂创建一个新的 AsyncSession 实例
    async with AsyncSessionLocal() as session:
        # yield 将控制权交给 FastAPI，让路由处理函数使用这个 session
        yield session
        # 当请求处理完成后，代码会回到这里，async with 会自动关闭会话并归还连接
