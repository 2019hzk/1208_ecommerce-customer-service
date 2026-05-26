from typing import Dict
from atguigu.plan.turn_plan import TurnPlan, ClarifyReason, TurnPlanValidationResult
from atguigu.task.flow.flows import FlowsList
from atguigu.task.command.models import StartFlowCommand, SetSlotsCommand, ResumeFlowCommand, CancelFlowCommand
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.domain.state import DialogueState


class TurnPlanValidator:

    def validate(self,
                 state: DialogueState,
                 turn_plan: TurnPlan,
                 *,
                 flow_list: FlowsList,
                 intents: Dict[str, KnowledgeIntent]
                 ) -> TurnPlanValidationResult:
        """
        校验 turn_plan
        :param turn_plan:
        :return:
        """

        active_tracks = self._active_tracks(turn_plan)

        # 1. 是否没有命中轨道
        if not active_tracks:
            return self._reject(ClarifyReason.MISSING_TRACK)

        # 2. 是否命中多条轨道
        if len(active_tracks) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TRACKS)

        # 3. 获取唯一的轨道
        active_track = active_tracks[0]

        # 4. 判断轨道到底是哪一个
        if active_track == "task":
            # 4.1 业务任务轨道
            return self._validate_task_track(turn_plan, flow_list)

        if active_track == "knowledge":
            # 4.1 信息咨询任务轨道
            return self._validate_knowledge_track(state, turn_plan, intents)

        return TurnPlanValidationResult(valid=True)

    @staticmethod
    def _active_tracks(turn_plan: TurnPlan) -> list[str]:
        active_tracks: list[str] = []
        if turn_plan.task is not None:
            active_tracks.append("task")  # 轨道的名字

        if turn_plan.knowledge is not None:
            active_tracks.append("knowledge")  # 轨道的名字

        if turn_plan.chitchat is not None:
            active_tracks.append("chitchat")  # 轨道的名字

        return active_tracks

    def _reject(self, reason: ClarifyReason) -> TurnPlanValidationResult:
        return TurnPlanValidationResult(
            valid=False,
            reason=reason
        )

    def _validate_task_track(self,
                             turn_plan: TurnPlan,
                             flow_list: FlowsList) -> TurnPlanValidationResult:
        """
        校验业务任务轨道
        四重校验规则（TODO 更多的校验规则）
        1. 校验1：是否存在对应的命令commands 是否有值
        2. 校验2：是否满足白名单中定义的四种命令类型
        3. 校验3：是否存在多个开启流程的命令（StartFlowCommand类型有多个）
        4. 校验4：根据业务流程的流程ID  判断开启的业务流程是否在流程清单中

        :param turn_plan:
        :param flows:
        :return:
        """
        task_track = turn_plan.task

        # 1. 校验1
        if not task_track.commands:
            return self._reject(ClarifyReason.MISSING_TASK_COMMANDS)

        # 2. 校验2
        allowed = (StartFlowCommand, SetSlotsCommand, ResumeFlowCommand, CancelFlowCommand)

        if not all(isinstance(cmd, allowed) for cmd in task_track.commands):
            return self._reject(ClarifyReason.INVALID_TASK_COMMANDS)

        # 3. 校验3(用一种StartFlowCommand ... )
        start_flow_cmd = [cmd for cmd in task_track.commands if isinstance(cmd, StartFlowCommand)]

        if len(start_flow_cmd) > 1:
            return self._reject(ClarifyReason.MULTIPLE_TASK_FLOWS)

        # 4. 校验4
        if start_flow_cmd:
            flow_id = start_flow_cmd[0].flow
            flow = flow_list.get_flow_by_id(flow_id)
            if flow is None:
                return self._reject(ClarifyReason.UNKNOWN_TASK_FLOW)

        return TurnPlanValidationResult(valid=True)

    def _validate_knowledge_track(self, state: DialogueState, turn_plan: TurnPlan,
                                  intents: Dict[str, KnowledgeIntent]) -> TurnPlanValidationResult:

        knowledge_plan = turn_plan.knowledge
        if knowledge_plan is None or not knowledge_plan.intents:
            return self._reject(ClarifyReason.MISSING_KNOWLEDGE_INTENT)

        focused_object = state.focused_object
        for intent in knowledge_plan.intents:
            intent_meta = intents[intent]
            required_object = intent_meta.requires_object
            if required_object is not None:
                if focused_object is None or focused_object.type != required_object:
                    return self._reject(ClarifyReason.MISSING_FOCUSED_OBJECT)

        return TurnPlanValidationResult(valid=True)
