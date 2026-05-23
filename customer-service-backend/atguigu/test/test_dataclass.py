from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class SystemContext:
    flow_id: str
    step_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StartedSystemContext(SystemContext):
    started_flow_id: str = ""
    started_flow_name: str = ""


if __name__ == '__main__':
    start_system_context = StartedSystemContext(started_flow_id="开启", started_flow_name="开启任务",
                                                flow_id="退款业务")

    print(start_system_context.to_dict())
