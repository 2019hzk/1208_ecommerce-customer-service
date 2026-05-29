from pathlib import Path
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.plan.planner import TurnPlanner
from atguigu.knowledge.handler import KnowLedgeHandler
from atguigu.chitchat.handler import ChitChatHandler
from atguigu.task.handler import TaskHandler
from atguigu.task.flow.loader import FlowLoader
from atguigu.plan.turn_validator import TurnPlanValidator
from atguigu.clarify.responder import ClarifyResponder
from atguigu.knowledge.intents import KNOWLEDGE_INTENTS
from atguigu.task.command.processor import CommandProcessor
from atguigu.task.action.builder import build_action_runner
from atguigu.task.flow.executor import FlowExecutor

# 真正加载YAML
PROJECT_DIR = Path(__file__).resolve().parents[2]
FLOW_CONFIG_DIR = PROJECT_DIR / "flow_config"
FLOW_CONFIG_FILES = ["system_flows.yml", "user_flows.yml"]


def build_dialogue_engine():
    flow_list = FlowLoader().load_many([FLOW_CONFIG_DIR / file_name for file_name in FLOW_CONFIG_FILES])
    return DialogueEngine(
        turn_planner=TurnPlanner(),
        turn_validator=TurnPlanValidator(),
        clarify_responder=ClarifyResponder(),
        task_handler=TaskHandler(flows=flow_list,
                                 processor=CommandProcessor(),
                                 action_runner=build_action_runner(),
                                 flow_executor=FlowExecutor()
                                 ),
        knowledge_handler=KnowLedgeHandler(knowledge_intents=KNOWLEDGE_INTENTS),
        chit_chat_handler=ChitChatHandler()
    )
