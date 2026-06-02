from atguigu.domain.messages import UserMessage, ProcessResult, ChatHistoryMessage
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.engine.dialogue_engine import DialogueEngine
from atguigu.domain.state import DialogueState
from atguigu.prompts.history_builder import HistoryBuilder

class DialogueService:
    """
    处理对话的业务类
    """

    def __init__(self, dialogue_state_repository: DialogueStateRepository,
                 dialogue_engine: DialogueEngine):
        self.dialogue_repository = dialogue_state_repository
        self.dialogue_engine = dialogue_engine

    async def handle_message(self, user_message: UserMessage) -> ProcessResult:
        """
        核心处理逻辑(IO：很慢/计算:调用LLM以及执行引擎、比较慢)
        :param user_message:
        :return:
        """

        # 1. 从数据库中 load 对话的聚合根数据 O阶段----[session/orm层数据模型]
        dialogue_state = await self.dialogue_repository.load(user_message.sender_id)

        # 2. 调用引擎使用对话状态对象 进行业务的各种计算操作(引擎)
        process_result = await self.dialogue_engine.handle_dialogue(dialogue_state, user_message)

        # 3. 通过save 将对话的聚合根写入到数据库中 I 阶段
        await self.dialogue_repository.save(dialogue_state)

        return process_result

    async def load_chat_history(self, sender_id: str) -> list[ChatHistoryMessage]:
        # 1. 获取用户的所有对话状态信息
        state: DialogueState = await self.dialogue_repository.load(sender_id)

        chat_messages: list[ChatHistoryMessage] = []
        for session in state.sessions:
            for turn in session.turns:
                chat_messages.append(HistoryBuilder.render_chat_history_user_message(turn.user_message, session))
                bot_msg = [HistoryBuilder.render_chat_history_bot_message(bot_msg, session) for bot_msg in
                           turn.bot_messages]
                chat_messages.extend(bot_msg)

        return chat_messages
