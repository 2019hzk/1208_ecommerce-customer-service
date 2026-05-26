from typing import Dict, Any
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.domain.messages import BotMessage


class KnowLedgeHandler:

    def __init__(self, knowledge_intents: Dict[str, KnowledgeIntent]):
        self.knowledge_intents = knowledge_intents

    def handle(self) -> list[BotMessage]:
        return [BotMessage(text="我暂不知道任何信息")]
