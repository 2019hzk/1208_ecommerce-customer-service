from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Command:
    command: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Command":
        clz = COMMAND_NAME_TO_CLASS.get(data["command"])
        if clz is not None:
            return clz(**data)
        return Command(command="unknown")


@dataclass
class StartFlowCommand(Command):
    flow: str  # 开启的新的业务流程的流程ID(LLM提供你的，你给了一份可用的流程清单：available_flows_json)


@dataclass
class SetSlotsCommand(Command):
    slots: Dict[str, Any]  # {"order_number":"A20240315001"}(LLM给你的填充的槽位信息（槽位的名字：槽位的值），你给的，在流程中会有槽位的完整信息)


@dataclass
class CancelFlowCommand(Command):
    pass  # 只支持取消当前的业务任务 TODO:自己添加一个flow---->在提示词中添加一个flow ,


@dataclass
class ResumeFlowCommand(Command):
    flow: str | None = None  # 恢复指定的业务流程或者当前活跃的业务流程（LLM生成的，你给了interrupted_tasks_json）


COMMAND_NAME_TO_CLASS = {
    "start_flow": StartFlowCommand,
    "set_slots": SetSlotsCommand,
    "cancel_flow": CancelFlowCommand,
    "resume_flow": ResumeFlowCommand,
}

if __name__ == '__main__':
    # c = CancelFlowCommand(command="xxxx")
    c = Command(command="xxxx")

    print(isinstance(c, StartFlowCommand))
