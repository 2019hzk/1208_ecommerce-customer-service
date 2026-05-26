from atguigu.domain.messages import BotMessage


class ChitChatHandler:

    def handle(self) -> list[BotMessage]:
        return [BotMessage(text="你今天还好嘛？")]
