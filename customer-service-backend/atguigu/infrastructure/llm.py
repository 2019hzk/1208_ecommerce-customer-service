from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from atguigu.config.config import settings

llm: BaseChatModel = init_chat_model(
    model=settings.llm_model,
    model_provider="openai",
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
    temperature=0  # 尽最大努力保证稳定性

)

if __name__ == '__main__':
    print(llm.invoke("你还好吗？我最近不太开心，给给我提供一些开心的情绪价值").content)
