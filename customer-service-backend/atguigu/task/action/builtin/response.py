from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.domain.messages import BotMessage


class ActionResponse(Action):
    name = "action_response"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        响应内容
        :param state:
        :param action_kwargs:
        :return:
        """

        text = action_kwargs.get('text')

        return ActionResult(messages=[BotMessage(text=text)])
