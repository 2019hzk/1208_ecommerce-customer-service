
"""
未来调用中台接口查询订单数据、商品数据...

"""

import asyncio
from httpx import AsyncClient

http_client: AsyncClient | None = None  # 全局变量


def init_http_client():
    global http_client
    http_client = AsyncClient(timeout=10.0)


async def close_http_client():
    await http_client.aclose()


async def main():
    # 1. 初始化http_client
    init_http_client()

    response = await http_client.get(url="http://192.168.200.145:18081/orders/B20260409001")
    print(response.json())

if __name__ == '__main__':
    asyncio.run(main())
