from dataclasses import dataclass, field
from atguigu.task.command.models import Command


@dataclass(slots=True)
class TaskTurnPlan:
    commands: list[Command] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "TaskTurnPlan":
        return cls(commands=[Command.from_dict(command) for command in data["commands"]])


@dataclass
class KnowledgeTurnPlan:
    intents: list[str] = field(default_factory=list)


    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeTurnPlan":
        return cls(intents=data["intents"])


@dataclass
class ChitchatTurnPlan:
    pass


@dataclass(slots=True)
class TurnPlan:
    """
    轮的规划结果(三种任务轨道)---（扩展点，并行处理：后续继续实现）

    """
    task: TaskTurnPlan | None = None                                # 业务任务---业务任务的轨道
    knowledge: KnowledgeTurnPlan | None = None                      # 信息质询---信息咨询业务轨道
    chitchat: ChitchatTurnPlan | None = None                        # 闲聊的 ----闲聊业务轨道

    @classmethod
    def from_dict(cls, data: dict) -> "TurnPlan":
        return cls(
            task=TaskTurnPlan.from_dict(data["task"]) if data.get("task") is not None else None,
            knowledge=KnowledgeTurnPlan.from_dict(data["knowledge"]) if data.get("knowledge") is not None else None,
            chitchat=ChitchatTurnPlan() if data.get("chitchat") is not None else None
        )












