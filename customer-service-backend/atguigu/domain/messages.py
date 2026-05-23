"""

消息类型：两种
UserMessage(用户)
BotMessage(机器人)

to_dict:将实例对象转成字典对象
from_dict:将字典对象转成实例对象

"""
from enum import Enum
from typing import Dict, Any
from dataclasses import field, dataclass


class MessageType(Enum):
    TEXT = "text"  # 文本类型
    OBJECT = "object"  # 对象类型


@dataclass(slots=True)  # 访问速度比较快/内存占用空间少__dict__
class FocusedObject:
    """
    聚焦对象
    """
    id: str
    type: str
    title: str = ""
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "attributes": dict(self.attributes)  # 浅拷贝
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FocusedObject":  # 前向引用 添加一个字符串""作为一个字面量
        return cls(
            id=data['id'],
            type=data['type'],
            title=data.get('title', ''),
            attributes=data.get('attributes', {})
        )

@dataclass(slots=True)
class UserMessage:
    sender_id: str  # 用户ID(必填字段)
    message_id: str  # 消息ID(必填字段)
    type: MessageType  # 消息类型（text or object）必填字段
    text: str | None = None  # 文本消息
    object: FocusedObject | None = None  # 对象类型的消息

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sender_id": self.sender_id,
            "message_id": self.message_id,
            "type": self.type.value,
            "text": self.text,
            "object": self.object.to_dict() if self.object else None

        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserMessage":
        return cls(
            sender_id=data['sender_id'],
            message_id=data['message_id'],
            type=MessageType(data['type']),
            text=data.get('text'),
            object=FocusedObject.from_dict(data['object']) if data.get('object') else None
        )


@dataclass(slots=True)
class BotMessage:
    text: str | None = None               # 主要回复消息的内容
    object: FocusedObject | None = None   # 扩展字段

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "object": self.object.to_dict() if self.object else None

        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BotMessage":
        return cls(
            text=data.get('text'),
            object=FocusedObject.from_dict(data['object']) if data.get('object') else None
        )

@dataclass
class ProcessResult:
    sender_id: str                                 # 用户ID
    message_id: str                                # 消息ID(内部生成)
    messages: list[BotMessage]                     # 回复消息（机器人回复的所有消息都给前端）

