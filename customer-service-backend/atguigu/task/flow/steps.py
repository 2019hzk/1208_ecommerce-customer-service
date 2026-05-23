"""
步骤（节点）设计
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List
from atguigu.task.flow.links import FlowStepLink, FlowStepStaticLink, FlowStepFallbackLink, FlowStepConditionalLink


class FlowStepType(Enum):
    """
    流程的步骤类型
    流程概念（管理节点的容器）
    步骤概念（节点）
    """
    START = "start"
    ACTION = "action"
    END = "end"
    COLLECT = "collect"


@dataclass(slots=True)
class ResponseDefinition:
    """
    响应的模式:静态模式(static) 改写模式(rephrase) | prompt
    响应内容(静态内容 改写后的内容)
    “”:一段输出而已 不需要定义逻辑（渲染）
    None:未定义/缺失字段：定义逻辑 处理
    """
    text: str  # 必填字段
    model: str = "static"  # 响应模式
    prompt: str | None = None


@dataclass(slots=True)
class SlotValidation:
    condition: str  # 条件(必填)
    failure_response: ResponseDefinition | None = None


@dataclass(slots=True)
class FlowStep:
    """
    （业务流程、系统）流程步骤 模版
    """
    id: str  # 步骤ID
    type: FlowStepType  # 步骤类型
    next: List[FlowStepLink] = field(default_factory=list)  # 下一步
    description: str = ""  # 步骤描述

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "FlowStep":
        # 多态转发
        step_type = step_data['type']
        clz = TYPE_TO_FLOW_STEP[step_type]
        return clz.from_dict(step_data)

    @staticmethod
    def base_load_fields(base_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        加载各个步骤的基础字段
        :param base_data: 各个步骤的字典数据
        :return:
        """
        return {
            "id": base_data['id'],
            "type": FlowStepType(base_data['type']),
            "description": base_data.get('description', ''),
            "next": _build_links(base_data['next'])
        }


def _build_links(link_data: str | list[Dict[str, Any]]) -> List[FlowStepLink]:
    # 1. next是字符串
    if isinstance(link_data, str):
        return [FlowStepStaticLink(target=link_data)]

    # 2. next是列表
    else:
        links = []
        for link_dict in link_data:
            if "if" in link_dict:
                links.append(FlowStepConditionalLink(condition=link_dict['if'], target=link_dict['then']))
            else:
                links.append(FlowStepFallbackLink(target=link_dict['else']))
        return links


@dataclass(slots=True)
class StartedFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "StartedFlowStep":
        return cls(**FlowStep.base_load_fields(step_data))


@dataclass(slots=True)
class ActionFlowStep(FlowStep):
    action: str = ""  # 行动的名字（action_listen:哨兵-等你/action_response:告诉你/action_xxxx:找东西 ）----外部yaml必传
    args: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "ActionFlowStep":
        return cls(
            **FlowStep.base_load_fields(step_data),
            action=step_data['action'],
            args=step_data.get('args', {})
        )


@dataclass(slots=True)
class EndFlowStep(FlowStep):

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "EndFlowStep":
        return cls(**FlowStep.base_load_fields(step_data))


@dataclass(slots=True)
class CollectedFlowStep(FlowStep):
    slot_name: str = ""  # 必填字段
    response: ResponseDefinition = field(default_factory=ResponseDefinition)  # 必填字段（填写的槽位）
    validate: SlotValidation | None = None  # 扩展槽位校验的能力

    @classmethod
    def from_dict(cls, step_data: Dict[str, Any]) -> "CollectedFlowStep":
        return cls(
            **FlowStep.base_load_fields(step_data),
            slot_name=step_data['slot_name'],
            response=ResponseDefinition(
                text=step_data['response']['text'],
                model=step_data['response'].get('model', 'static'),
                prompt=step_data['response'].get('prompt')
            ),
            validate=SlotValidation(
                condition=step_data['validate']['condition'],
                failure_response=ResponseDefinition(
                    text=step_data['validate']['failure_response']['text'],
                    model=step_data['validate']['failure_response'].get('model', 'static'),
                    prompt=step_data['validate']['failure_response'].get('prompt')
                ) if step_data['validate'].get('failure_response') else None
            ) if step_data.get('validate') else None
        )


# 类的类型 实例类型
TYPE_TO_FLOW_STEP: Dict[str, type[FlowStep]] = {
    "start": StartedFlowStep,
    "action": ActionFlowStep,
    "end": EndFlowStep,
    "collect": CollectedFlowStep
}

if __name__ == '__main__':
    data = {
        "id": "111",
        "type": "start",
        "next": [],
        "description": "1111111"
    }
    print(FlowStep.from_dict(data))
