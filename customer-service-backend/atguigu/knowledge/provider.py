import json, asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
from atguigu.config.config import settings
from atguigu.infrastructure import http
from atguigu.domain.state import DialogueState


@dataclass(slots=True)
class KnowledgeChunk:
    content: str


class KnowledgeProvider(ABC):
    provider_id = ""  # 提供商的ID

    @abstractmethod
    async def retrieve(  # 提供检索方法
            self,
            state: DialogueState,
    ) -> list[KnowledgeChunk]:
        pass


class ProductAPIProvider(KnowledgeProvider):
    provider_id = 'api.product'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        product_id = state.focused_object.id
        data: dict[str, Any] = await self._get_product_info_by_id(product_id)
        text = json.dumps(data, ensure_ascii=False, indent=2)
        return [KnowledgeChunk(content=f"商品信息:\n{text}")]

    async def _get_product_info_by_id(self, product_id: str) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/products/{product_id}"
        response = await http.http_client.get(url)
        return response.json()["data"]


class OrderAPIProvider(KnowledgeProvider):
    provider_id = 'api.order'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        focused_object = state.focused_object
        order_number = focused_object.id

        order_payload, logistics_payload = await asyncio.gather(
            self._fetch_order(order_number),
            self._fetch_logistics(order_number),
        )

        return [
            KnowledgeChunk(
                content="订单与物流信息：\n"
                        + json.dumps(
                    {
                        "order_number": order_number,
                        "order": order_payload,
                        "logistics": logistics_payload,
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        ]

    async def _fetch_order(self, order_number) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/orders/{order_number}"
        response = await http.http_client.get(url)
        return response.json()["data"]

    async def _fetch_logistics(self, order_number) -> dict[str, Any]:
        url = f"{settings.commerce_api_base_url}/orders/{order_number}/logistics"
        response = await http.http_client.get(url)
        return response.json().get("data", {})


class FAQProvider(KnowledgeProvider):
    provider_id = 'faq.default'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        # TODO
        return [KnowledgeChunk(content="未检索到相关问题")]


class RAGProvider(KnowledgeProvider):
    provider_id = 'rag.default'

    async def retrieve(self, state: DialogueState) -> list[KnowledgeChunk]:
        # RAG知识库查询知识接口（TODO）
        return [KnowledgeChunk(content="未检索到相关信息")]
