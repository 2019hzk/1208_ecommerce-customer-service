from abc import ABC, abstractmethod
from typing import Any
from dataclasses import dataclass, field
from atguigu.domain.state import DialogueState
from atguigu.domain.messages import BotMessage

"""
内置
action_response:(ActionResult:messages:"请先选择一个商品，再继续咨询")
action_listen: (ActionResult())
自定义：
action_recommend_similar_products
action_lookup_order_status(ActionResult:(slot_updates:{第三返回的}))
action_lookup_logistics (ActionResult:(slot_updates:{第三返回的}))
"""
@dataclass
class ActionResult:
    messages: list[BotMessage] = field(default_factory=list)         # action执行完后的结果 消息
    slot_updates: dict[str, Any] = field(default_factory=dict)       # 业务任务流程要的所有槽位信息（槽位信息来源两处：自己填（卡片）、llm填（文本）、三方返回的数据自己构建的）



class Action(ABC):
    name: str  # action的名字

    @abstractmethod
    async def run(
            self,
            state: DialogueState,
            action_kwargs: dict[str, Any],
    ) -> ActionResult:
        pass
