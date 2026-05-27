from typing import List
from atguigu.task.command.models import Command
from atguigu.task.flow.flows import FlowsList
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.processor import CommandProcessor


class TaskHandler:

    def __init__(self, flows: FlowsList, processor: CommandProcessor):
        self.flows = flows
        self.processor = processor

    def handle(self, state: DialogueState, *, commands: List[Command],
               ) -> list[BotMessage]:
        # 1. 利用CommandProcessor 处理对应的Command
        self.processor.run(state, commands, self.flows)

        # 2. FlowExecutor.run_task():推进流程（TaskContext/SystemContext）交互(TODO)

        return [BotMessage(text="xxxx")]
