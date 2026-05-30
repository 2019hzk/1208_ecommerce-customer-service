"""
定义fastapi实例

"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from atguigu.api.router.chat_router import router
from atguigu.infrastructure.database import init_db_engine, close_db_engine
from atguigu.api.dependencies import init_dialogue_engine
from atguigu.infrastructure.http import init_http_client, close_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    1.回调lifespan的时机：在服务一启动的时候会先来调用（初始化HTTP客户端、Redis客户端、MySQL数据库的连接池...）
    2.参数app以及类型必须要指定，因为底层FastAPI对资源做共享和传递
    3.yield: 让FASTAPI处理请求，等应用关闭,才执行close_db_engine
    :return:
    """
    init_db_engine()
    init_http_client()
    init_dialogue_engine()
    yield  # FASTAPI 处理请求....
    await close_db_engine()  # 应用关闭的时候才执行到
    await  close_http_client()


app = FastAPI(description="电商小二智能客服应用", lifespan=lifespan)

app.include_router(router)
