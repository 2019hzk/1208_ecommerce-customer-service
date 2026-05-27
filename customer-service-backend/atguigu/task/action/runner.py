from dataclasses import dataclass, field
from typing import Any
from atguigu.task.action.registry import ActionRegistry
from atguigu.task.action.base import ActionResult
from atguigu.domain.state import DialogueState


@dataclass
class ActionCall:
    """
    FlowExecutor返回的
    """
    action_name: str
    action_kwargs: dict[str, Any] = field(default_factory=dict)


class ActionRunner:
    def __init__(self, registry: ActionRegistry) -> None:
        self.registry = registry

    async def run(self, action_call: ActionCall, state: DialogueState) -> ActionResult:
        # 1. 获取action的名字
        action_name = action_call.action_name

        # 2. 从Action注册中心获取名字对应的Action的实例对象
        action = self.registry.get(action_name)

        # 3. 调用具体Action的逻辑
        return await action.run(state, action_call.action_kwargs)
