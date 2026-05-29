from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class LookUpLogisticsAction(Action):
    name = "action_lookup_logistics"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        调用电商平台查询物流信息接口
        :param state:
        :param action_kwargs:
        :return:
        """

        return ActionResult()
