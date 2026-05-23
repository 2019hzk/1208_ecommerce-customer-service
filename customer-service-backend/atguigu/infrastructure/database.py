"""
sqlalchemy:名字sql log 幂
作用：通过声明式方式让Python语言操作数据库（MySQL PGSQL...）
使用：1. （声明）定义数据模型 2. 利用session对象通过API方式来交互数据库（crud）

操作自己的数据库（customer_service） dialogue_states表（整个对话状态：聚合根）

"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from atguigu.config.config import settings
from sqlalchemy import text

engine: AsyncEngine | None = None
async_session: async_sessionmaker[AsyncSession]


def init_db_engine():
    global engine, async_session
    # 1. 创建异步引擎
    engine = create_async_engine(
        settings.database_url,
        echo=True)

    # 2. 创建异步session工厂
    async_session = async_sessionmaker(engine, expire_on_commit=False)


async def close_db_engine():
    await engine.dispose()


async def main():
    init_db_engine()

    async  with async_session() as session:
        result = await session.execute(text("select 1"))  # 测试是否通（core）
        # print(type(result.fetchone()))
        print(result.fetchone())

    await close_db_engine()


if __name__ == '__main__':
    asyncio.run(main())
