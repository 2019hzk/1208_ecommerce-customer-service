import time
from typing import Dict, Any
from atguigu.domain.state import DialogueState, Session
from atguigu.domain.messages import UserMessage, ProcessResult, BotMessage, MessageType
from atguigu.plan.planner import TurnPlanner
from atguigu.task.command.models import Command
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowLedgeHandler
from atguigu.chitchat.handler import ChitChatHandler
from atguigu.task.flow.flows import FlowsList
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
from atguigu.knowledge.intents import KnowledgeIntent
from atguigu.plan.turn_plan import ClarifyReason
from atguigu.task.command.models import SetSlotsCommand
from atguigu.task.flow.steps import CollectedFlowStep


class DialogueEngine:
    """
    调度中心（只协调各个组件、身上的各个组件真正干活）
    """

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_validator: TurnPlanValidator,
                 clarify_responder: ClarifyResponder,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowLedgeHandler,
                 chit_chat_handler: ChitChatHandler
                 ):
        self.turn_planner = turn_planner
        self.turn_validator = turn_validator  # TurnPlan校验器（负责校验）
        self.clarify_responder = clarify_responder  # 意图澄清器（响应澄清的内容）
        self.task_handler = task_handler  # 处理轨道是业务任务的
        self.knowledge_handler = knowledge_handler  # 处理轨道信息咨询的
        self.chit_chat_handler = chit_chat_handler  # 处理轨道是闲聊的

    async def handle_dialogue(self, state: DialogueState,
                              user_message: UserMessage) -> ProcessResult:
        # 1. 开启Session(不是SQL的Session，业务的会话Session)
        self._prepare_session(state)

        # 2. 开启turn
        self._begin_turn(state, user_message)

        # 3. 判断消息类型
        # 3.1 文本消息类型
        if user_message.type is MessageType.TEXT:
            msgs = await self._handle_text_msg(state,
                                               self.turn_planner,
                                               self.task_handler.flows,
                                               self.knowledge_handler.knowledge_intents)
        else:
            state.set_focused_object(user_message.object)
            msgs = await self._handle_obj_msg(user_message, state, self.task_handler.flows)

        # 4. 更新turn中的BotMessage
        state.pending_turn.bot_messages.extend(msgs)

        # 5. 提交
        state.commit_turn()

        # 6. 返回
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=msgs
        )

    def _prepare_session(self, state: DialogueState) -> None:
        """

        :param self:
        :param state:  会话状态
        :return:
        """

        # 1. 获取当前session是否存在
        current_session: Session = state.current_session()

        # 2. 判断session是否存在
        # 2.1 session不存在
        if current_session is None:
            state.start_session()
            return

        # 2.2 session存在
        # a) 检查session是否可用(规则：会话时间 是否超时) 超时(1)关闭当前session (2)清空session的相关信息 (3)开启session)
        now = time.time()
        if now - current_session.last_activity_at > 60 * 60:
            state.close_session()
            state.reset_running_state_for_new_session()
            state.start_session()
        # b) 存在且可用 (更新当前session的激活时间)
        else:
            current_session.last_activity_at = now
        return

    def _begin_turn(self, state: DialogueState, user_message: UserMessage):
        state.begin_turn(user_message)

    async def _handle_text_msg(self, state: DialogueState,
                               turn_planner: TurnPlanner,
                               flows: FlowsList,
                               knowledge_intents: Dict[str, KnowledgeIntent]
                               ) -> list[BotMessage]:
        """
        处理文本类型消息
        :param state:
        :param turn_planner:
        :return:
        """

        # 1. 利用意图分析器调用LLM，确定任务轨道
        turn_plan = await turn_planner.predict(state, flows=flows, intents=knowledge_intents)

        # 2. 校验
        validated = self.turn_validator.validate(state, turn_plan, flow_list=flows, intents=knowledge_intents)

        # 2.1 如果校验不通过，需要意图澄清器澄清意图
        if not validated.valid:
            return await self.clarify_responder.respond(state, validated.reason)

        # 2.2 如果校验通过，执行对应某一条轨道进行对应的处理

        if turn_plan.task is not None:
            return await self.task_handler.handle(state, commands=turn_plan.task.commands)
        elif turn_plan.knowledge is not None:
            return await self.knowledge_handler.handle(state, turn_plan.knowledge.intents)
        else:
            return await self.chit_chat_handler.handle(state)

    async def _handle_obj_msg(self, user_message: UserMessage,
                              state: DialogueState,
                              flows: FlowsList) -> list[BotMessage]:

        # 1. 将对象解析成command(SetSlotsCommand)
        commands = self._resolve_object_command(user_message, state, flows)
        # 2. 判断command是否有(流程的步骤刚好需要你点击的卡片) 退后续的流程即可（槽位填好了）
        if commands:
            return await self.task_handler.handle(state, commands=commands)

        # 3. 业务流程存在
        if state.active_task is not None:
            return await self.task_handler.handle(state, commands=[])

        # 4. 业务流程不存在
        return await self.clarify_responder.respond(state, reason=ClarifyReason.OBJECT_REQUIRES_INTENT)

    def _resolve_object_command(self, user_message: UserMessage,
                                state: DialogueState,
                                flows: FlowsList) -> list[Command]:

        # 1. 获取对象消息
        user_obj = user_message.object
        if user_obj is None:
            return []
        # 2. 获取对象消息的类型
        object_type = user_obj.type

        # 3. 判读对象的类型
        if object_type == "order":
            if self._flow_has_unfilled_collect_slot(state, flows, "order_number"):
                return [SetSlotsCommand(command="set_slots", slots={"order_number": user_obj.id})]

            return []

        # 3. 判读对象的类型
        if object_type == "product":
            if self._flow_has_unfilled_collect_slot(state, flows, "product_id"):
                return [SetSlotsCommand(command="set_slots", slots={"product_id": user_obj.id})]
            return []

        return []

    def _flow_has_unfilled_collect_slot(self, state: DialogueState,
                                        flows: FlowsList, slot_name: str) -> bool:

        # 1. 获取活跃任务
        active_task = state.active_task

        # 2. 是否存在活跃任务-----(澄清)
        if active_task is None:
            return False

        # 3. 从活跃任务中获取流程
        flow_id = active_task.flow_id
        flow = flows.get_flow_by_id(flow_id)
        if flow is None:
            return False

        # 4. 判断该流程中的上下文当前槽位是否已经填过
        if active_task.slots.get(slot_name):
            return False

        for step in flow.steps:
            if isinstance(step, CollectedFlowStep) and step.slot_name == slot_name:
                return True

        return False
