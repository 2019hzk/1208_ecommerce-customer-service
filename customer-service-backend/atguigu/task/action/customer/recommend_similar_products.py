from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult


class RecommendSimilarProductsAction(Action):
    name = "action_recommend_similar_products"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        商品推荐 （占位）
        :param state:
        :param action_kwargs:
        :return:
        """
        return ActionResult()
