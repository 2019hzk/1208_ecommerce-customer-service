"""

定义接口数据模型
请求相关：
响应相关：
"""
from pydantic import BaseModel


class ChatObject(BaseModel):
    type: str
    id: str
    title: str | None = None  # 标题
    attributes: dict = {}  # 属性


class ChatRequest(BaseModel):
    sender_id: str  # 用户ID
    message_id: str | None = None  # 消息ID
    text: str | None = None  # 文本类型消息
    object: ChatObject | None = None  # 对象类型消息  (text内容和object内容不可能同时有)


class ChatBotMessage(BaseModel):
    text: str | None = None  # 现有能力：回复文本类型的消息
    object: ChatObject | None = None  # 扩展字段（机器人目前没有能力回复对象类型的消息）


class ChatResponse(BaseModel):
    sender_id: str
    message_id: str
    messages: list[ChatBotMessage]
