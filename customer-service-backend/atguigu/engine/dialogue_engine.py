import time

from atguigu.domain.state import DialogueState, Session
from atguigu.domain.messages import UserMessage, ProcessResult, BotMessage, MessageType
from atguigu.plan.planner import TurnPlanner
from atguigu.task.handler import TaskHandler
from atguigu.knowledge.handler import KnowLedgeHandler
from atguigu.chitchat.handler import ChitChatHandler
from atguigu.task.flow.flows import FlowsList
from atguigu.plan.turn_validator import TurnPlanValidator


class DialogueEngine:
    """
    调度中心（只协调各个组件、身上的各个组件真正干活）

    """

    def __init__(self,
                 turn_planner: TurnPlanner,
                 turn_validator: TurnPlanValidator,
                 task_handler: TaskHandler,
                 knowledge_handler: KnowLedgeHandler,
                 chit_chat_handler: ChitChatHandler
                 ):
        self.turn_planner = turn_planner
        self.turn_validator = turn_validator
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
            msgs = await self._handle_text_msg(state, self.turn_planner, self.task_handler.flows)
        else:
            # TODO
            self._handle_obj_msg()

        # 4. 提交 TODO

        # 5. 返回
        return ProcessResult(
            sender_id=user_message.sender_id,
            message_id=user_message.message_id,
            messages=[
                BotMessage(text="我是智能小客服"),
                BotMessage(text="欢迎你来到这里...")
            ]

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

    def _handle_obj_msg(self):
        """
        处理对象类型的消息
        :return:
        """
        pass

    async def _handle_text_msg(self, state: DialogueState,
                               turn_planner: TurnPlanner,
                               flows: FlowsList
                               ) -> list[BotMessage]:
        """
        处理文本类型消息
        :param state:
        :param turn_planner:
        :return:
        """

        # 1. 利用意图分析器调用LLM，确定任务轨道
        turn_plan = await turn_planner.predict(state, flows)

        # 2. 校验(TODO )
        self.turn_validator.validate()

        # 2.1 如果校验不通过，需要意图澄清器澄清意图
        # 2.2 如果校验通过，执行对应某一条轨道进行对应的处理

        if turn_plan.task is not None:
            self.task_handler.handle()
        elif turn_plan.knowledge is not None:
            self.knowledge_handler.handle()
        else:
            self.chit_chat_handler.handle()
