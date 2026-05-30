from typing import Any

from atguigu.domain.state import DialogueState
from atguigu.task.action.base import Action, ActionResult
from atguigu.task.action.customer.shared import fetch_logistics


class LookUpLogisticsAction(Action):
    name = "action_lookup_logistics"

    async def run(self, state: DialogueState, action_kwargs: dict[str, Any]) -> ActionResult:
        """
        调用电商平台查询物流信息接口
        :param state:
        :param action_kwargs:
        :return:
        """

        # 1. 准备电商的物流查询接口的数据
        order_id = state.active_task.slots.get('order_number')

        if order_id is None:
            return ActionResult(slot_updates={
                "tracking_number": "未知",
                "logistics_company": "未知",
                "logistics_status": "暂时无法查到物流信息，请稍后再试。",
            })

        # 2. 发送请求获取返回结果
        logistics_data = await  fetch_logistics(order_id=order_id)

        if logistics_data is None:
            return ActionResult(slot_updates={
                "tracking_number": "未知",
                "logistics_company": "未知",
                "logistics_status": "暂时无法查到物流信息，请稍后再试。",
            })

        # 3. 根据结果解析成ActionResult对象
        return ActionResult(
            slot_updates={
                "tracking_number": logistics_data.get('tracking_number') or "未知",
                "logistics_company": logistics_data.get('logistics_company') or "未知",
                "logistics_status": logistics_data.get('status_desc') or logistics_data.get('status') or "未知"
            }
        )
