from typing import Dict, Any
from dataclasses import dataclass, field, asdict


@dataclass(slots=True)
class TaskContext:
    """
    业务任务的上下任务 各个业务任务的信息都会用TaskContext来保存
    """
    flow_id: str  # 业务流程的流程ID
    step_id: str | None = None  # 业务流程下步骤ID
    slots: Dict[str, Any] = field(default_factory=dict)  # 业务任务执行过程中收集到的数据 槽位数据

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskContext":
        return cls(
            flow_id=data["flow_id"],
            step_id=data.get("step_id"),
            slots=dict(data.get("slots", {})),
        )


@dataclass(slots=True)
class SystemContext:  # 系统上下文：模版【各个子类系统上下文的通用属性】
    """
    系统流程上下文
    """
    flow_id: str  # 系统流程的流程ID(system_task_started)
    step_id: str | None = None  # 系统流程的步骤ID(start)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SystemContext":
        clz = FLOW_ID_TO_CONTEXT_CLASS[data['flow_id']]
        return clz(**data)


@dataclass(slots=True)
class StartedSystemContext(SystemContext):
    started_flow_id: str = ""  # 开启具体某一个业务流程的流程ID    order_status_query
    started_flow_name: str = ""  # 开启具体的某一个业务流程的名字     订单状态查询


@dataclass(slots=True)
class InterruptedSystemContext(SystemContext):
    interrupted_flow_id: str = ""  # 中断老业务流程的ID
    interrupted_flow_name: str = ""  # 中断老业务流程的名字
    started_flow_id: str = ""  # 开始新业务流程ID
    started_flow_name: str = ""  # 开始新业务流程名字


@dataclass(slots=True)
class ResumedSystemContext(SystemContext):
    resumed_flow_id: str = ""  # 恢复业务流程的ID(中断的业务流程)
    resumed_flow_name: str = ""  # 恢复业务流程的名字(中断的业务流程)


@dataclass(slots=True)
class CanceledSystemContext(SystemContext):
    canceled_flow_id: str = ""
    canceled_flow_name: str = ""


@dataclass(slots=True)
class CollectedSystemContext(SystemContext):
    slot_name: str = ""  # 收集的槽位名：order_number(未来扩展渲染的时候能用到、点击卡片的时候，槽位的名字能做判断)
    response: Dict[str, Any] = field(default_factory=dict)  # {"text":"请告诉我你的订单号"} （响应输出的内容）


FLOW_ID_TO_CONTEXT_CLASS: Dict[str, Any] = {
    "system_task_started": StartedSystemContext,
    "system_task_resumed": ResumedSystemContext,
    "system_collect_information": CollectedSystemContext,
    "system_task_interrupted": InterruptedSystemContext,
    "system_task_canceled": CanceledSystemContext
}
