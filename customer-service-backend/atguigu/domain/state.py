import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any
from atguigu.domain.contexts import TaskContext, SystemContext
from atguigu.domain.messages import FocusedObject, UserMessage, BotMessage


@dataclass(slots=True)
class Turn:
    """
    本轮对话的对象
    """
    turn_id: str
    user_message: UserMessage
    bot_messages: list[BotMessage]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id,
            "user_message": self.user_message.to_dict(),
            "bot_messages": [bot_message.to_dict() for bot_message in self.bot_messages]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Turn":
        return cls(
            turn_id=data['turn_id'],
            user_message=UserMessage.from_dict(data['user_message']),
            bot_messages=[BotMessage.from_dict(bot_msg_dict) for bot_msg_dict in data['bot_messages']]
        )


@dataclass(slots=True)
class Session:
    """
    会话信息
    """
    session_id: str  # 会话ID(标识)
    started_at: float  # 会话开启的时间（根据session时间做各种各样的统计）
    last_activity_at: float  # 最后一次活动的时间戳，用来判断超时
    closed_at: float | None = None  # session是否关闭了(有值：session关 没值：session没关)
    turns: list[Turn] = field(default_factory=list)  # 当前会话的多轮

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "last_activity_at": self.last_activity_at,
            "closed_at": self.closed_at,
            "turns": [turn.to_dict() for turn in self.turns]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        return cls(
            session_id=data['session_id'],
            started_at=data['started_at'],
            last_activity_at=data['last_activity_at'],
            closed_at=data.get('closed_at'),
            turns=[Turn.from_dict(turn_dict) for turn_dict in data.get('turns')]
        )


@dataclass(slots=True)
class DialogueState:
    sender_id: str  # 必须传入
    active_task: TaskContext | None = None  # 当前执行的业务任务
    paused_tasks: list[TaskContext] = field(default_factory=list)  # 当期暂停的业务任务（多个）
    active_system_task: SystemContext | None = None  # 当前执行的系统流程
    focused_object: FocusedObject | None = None
    sessions: list[Session] = field(default_factory=list)  # 当前用户的所有回话都存储起来
    current_session_id: str | None = None  # 当前用户的session的sessionID
    pending_turn: Turn | None = None  # turn会话的暂存区（变量：内存中缓冲区） 不会持久化

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "active_task": self.active_task.to_dict() if self.active_task else None,
            "paused_tasks": [paused_task.to_dict() for paused_task in self.paused_tasks],
            "active_system_task": self.active_system_task.to_dict() if self.active_system_task else None,
            "focused_object": self.focused_object.to_dict() if self.focused_object else None,
            "sessions": [session.to_dict() for session in self.sessions],
            "current_session_id": self.current_session_id
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueState":
        return cls(
            sender_id=data['sender_id'],
            active_task=TaskContext.from_dict(data['active_task']) if data.get('active_task') else None,
            paused_tasks=[TaskContext.from_dict(paused_task_dict) for paused_task_dict in data['paused_tasks']],
            active_system_task=SystemContext.from_dict(data['active_system_task']) if data.get(
                'active_system_task') else None,
            focused_object=FocusedObject.from_dict(data['focused_object']) if data.get('focused_object') else None,
            sessions=[Session.from_dict(session_dict) for session_dict in data['sessions']],
            current_session_id=data.get('current_session_id'),
            pending_turn=Turn.from_dict(data['pending_turn']) if data.get('pending_turn') else None
        )

    # --------------任务相关--------------------------

    def start_active_system_task(self, active_system_task: SystemContext):
        """
        开启系统流程
        :param active_system_task:
        :return:
        """
        self.active_system_task = active_system_task

    def end_active_system_task(self):
        """
        结束系统流程
        :return:
        """
        self.active_system_task = None

    def start_active_task(self, active_task: TaskContext):
        """
        开启业务任务
        :param active_task:
        :return:
        """
        self.active_task = active_task

    def end_active_task(self):
        """
        结束业务任务
        :return:
        """
        self.active_task = None

    def interrupted_active_task(self):
        """
        中断活跃任务
        :return:
        """

        self.paused_tasks.append(self.active_task)
        self.active_task = None

    def resumed_active_task(self, flow_id: str | None = None) -> bool:
        """
        恢复业务任务:流程ID
        :return: 要不恢复成功 要不就是回复失败
        """

        # 1. 判断栈中是否存在中断的业务任务
        if not self.paused_tasks:
            return False

        # 2. 判断业务流程ID 是否存在
        # 2.1 如果不存在(只能恢复栈顶的)
        if flow_id is None:
            task = self.paused_tasks.pop()
            self.active_task = task
            return True
        # 2.2 如果存在
        for i, paused_task in enumerate(self.paused_tasks):
            if paused_task.flow_id == flow_id:
                # a) 激活
                self.active_task = paused_task
                # b) 删除
                del self.paused_tasks[i]

                return True

        return False

    def cancel_active_task(self):
        self.active_task = None
        self.active_system_task = None

    # --------------槽位相关--------------------------
    def set_slots(self, slots: Dict[str, Any]):
        """
        设置槽位
        :param slots:
        :return:
        """
        if self.active_task is not None:
            self.active_task.slots.update(slots)

    def remove_slot(self, slot_name: str):
        """
        移除槽位
        :param slot_name: 移除的槽位名
        :return:
        """
        self.active_task.slots.pop(slot_name)

    # --------------当前信息（当前任务、当前session）--------------------------
    def current_active_task(self):
        """
        当前正在执行的任务（系统流程、业务任务）
        先获取系统流程 如果获取不到 获取业务任务
        :return:
        """

        return self.active_system_task or self.active_task

    def current_session(self) -> Session | None:
        """
        返回当前session
        :return:
        """
        for session in self.sessions:
            if session.session_id == self.current_session_id:
                return session

        return None

    # --------------session相关的--------------------------
    def start_session(self):
        """
        开启session
        :return:
        """

        now = time.time()
        session = Session(session_id=str(uuid.uuid4()), started_at=now, last_activity_at=now)
        self.sessions.append(session)
        self.current_session_id = session.session_id

    def close_session(self):
        if self.current_session() is not None:
            # 1. 修改session的时间closed_at
            self.current_session().closed_at = time.time()
            # 2. 清空当前的session_id
            self.current_session_id = None

    def reset_running_state_for_new_session(self):
        """
        session会话超时（60min超时时间）
        :return:
        """
        self.active_task = None
        self.active_system_task = None
        self.paused_tasks = []
        self.focused_object = None
        self.pending_turn = None

    # --------------turn相关的--------------------------

    def begin_turn(self, message: UserMessage):
        if self.current_session():
            turn = Turn(turn_id=str(uuid.uuid4()), user_message=message, bot_messages=[])
            self.pending_turn = turn

    def commit_turn(self):
        if self.current_session():
            self.current_session().turns.append(self.pending_turn)
            self.pending_turn = None

    # --------------FocusedObject相关的--------------------------
    def set_focused_object(self, focused_object: FocusedObject):
        self.focused_object = focused_object
