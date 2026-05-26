from atguigu.task.flow.flows import FlowsList
from atguigu.domain.messages import BotMessage


class TaskHandler:

    def __init__(self, flows: FlowsList):
        self.flows = flows

    def handle(self) -> list[BotMessage]:
        return [BotMessage(text="任务已经处理")]
