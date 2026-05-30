from typing import Dict, Any

from atguigu.domain.state import DialogueState
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.knowledge.provider import KnowledgeChunk
from atguigu.knowledge.registry import KnowledgeProviderRegistry
from atguigu.knowledge.responder import KnowledgeResponder
from atguigu.domain.messages import BotMessage


class KnowLedgeHandler:

    def __init__(self,
                 knowledge_intents: Dict[str, KnowledgeIntent],
                 provider_registry: KnowledgeProviderRegistry,
                 knowledge_responder: KnowledgeResponder
                 ):
        self.knowledge_intents = knowledge_intents
        self.provider_registry = provider_registry
        self.knowledge_responder = knowledge_responder

    async def handle(self, state: DialogueState,
                     knowledge_intents: list[str]) -> list[BotMessage]:

        # ① 根据意图寻找知识来源
        provider_ids: list[str] = self._get_provider_ids_by_intents(knowledge_intents)

        # ② 从每个 provider 检索知识片段
        chunks: list[KnowledgeChunk] = []
        for provider_id in provider_ids:
            provider = self.provider_registry.get(provider_id)
            current_chunks = await provider.retrieve(state)
            chunks.extend(current_chunks)

        # ③ 用知识生成回复
        return await self.knowledge_responder.respond(
            user_message=state.pending_turn.user_message,
            recent_turns=state.current_session().turns[-5:],
            chunks=chunks
        )

    # 请问这件商品的退款以及退货政策是什么-----> intents=["return_policy","refund_policy"]
    def _get_provider_ids_by_intents(self, knowledge_intents: list[str]) -> list[str]:
        provider_ids: list[str] = []
        for intent in knowledge_intents:
            provider_ids.extend(self.knowledge_intents[intent].provider_ids)
        return list(set(provider_ids))
