import asyncio
from models import Base, User, Address
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, text


# async def async_main():
#     # 1. 定义异步引擎
#     engine = create_async_engine("mysql+aiomysql://root:root@localhost:3306/sqlalchemy_test?charset=utf8mb4", echo=True)
#
#     async with engine.begin() as conn:
#         # 执行建表语句
#         await conn.run_sync(Base.metadata.create_all)     #  1.从异步引擎中获取到一个异步连接  2. 将耗时的IO建表操作丢给另外一个线程执行  3. run_sync会将异步连接剥掉异步身份成为同步连接
#
#
#         print("建表执行完毕")
#
#     await engine.dispose()   # 关闭引擎

async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
    async with async_session() as session:
        async with session.begin():
            session.add_all(
                [
                    User(name="Mr 张"),
                    User(
                        name="sandy",
                    ),
                    User(name="patrick")
                ]
            )


async def async_main():
    # 1. 创建异步引擎
    engine = create_async_engine(
        "mysql+aiomysql://root:root@localhost:3306/sqlalchemy_test?charset=utf8mb4",
        echo=True)

    # 2. 创建异步session工厂      expire_on_commit:提交之后 变量是否还保留(默认不保留) 提交之后变量仍然保留设置为False:
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    # 3. 执行建表
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    # await insert_objects(async_session)
    async with async_session() as session:
        user = (await session.scalar(select(User)))

        await session.commit()



if __name__ == '__main__':
    asyncio.run(async_main())
