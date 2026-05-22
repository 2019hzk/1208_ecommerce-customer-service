from dataclasses import dataclass


@dataclass(slots=True)
class FlowStepLink:
    """
    模版边（基类）
    """
    target: str  # 下一条步骤（节点）的ID


@dataclass(slots=True)
class FlowStepStaticLink(FlowStepLink):
    """
    对应的是next:"ask_order_number"
    """
    pass


@dataclass(slots=True)
class FlowStepConditionalLink(FlowStepLink):
    """
    对应的是next:"[{"if":"xxxxxx","then":"step_id"}]"
    """
    condition: str  # 接收if 中的xxxxx


@dataclass(slots=True)
class FlowStepFallbackLink(FlowStepLink):
    """"
      对应的是next:"[{"else":"step_id"}]"
    """
    pass
