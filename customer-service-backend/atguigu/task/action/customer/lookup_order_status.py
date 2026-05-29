from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class LookUpOrderStatusAction(Action):
    name = "action_lookup_order_status"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        调用电商平台查询订单状态接口
        :param state:
        :param action_kwargs:
        :return:
        """

        return ActionResult()
