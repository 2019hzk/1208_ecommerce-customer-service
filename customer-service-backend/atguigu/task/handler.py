from typing import List
from atguigu.task.command.models import Command
from atguigu.task.flow.flows import FlowsList
from atguigu.domain.messages import BotMessage
from atguigu.domain.state import DialogueState
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.action.runner import ActionRunner
from atguigu.task.flow.executor import FlowExecutor


class TaskHandler:

    def __init__(self,
                 flows: FlowsList,
                 processor: CommandProcessor,
                 action_runner: ActionRunner,
                 flow_executor: FlowExecutor):
        self.flows = flows
        self.processor = processor
        self.action_runner = action_runner
        self.flow_executor = flow_executor

    async def handle(self, state: DialogueState, *, commands: List[Command],
                     ) -> list[BotMessage]:
        # 1. 利用CommandProcessor 处理对应的Command
        self.processor.run(state, commands, self.flows)

        # 2. 推荐yaml中定义的流程
        messages = await self.flow_executor.run_task(state, self.flows, self.action_runner)

        # 3. 返回流程执行器得到的消息
        return messages
