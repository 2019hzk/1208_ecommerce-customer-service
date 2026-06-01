"""数字人聊天 WebSocket 接口。

协议(纯 JSON 文本帧):

客户端 -> 服务端 (text):
    {"type": "user_text", "sender_id": "u1", "text": "...", "message_id": "(optional)"}

服务端 -> 客户端 (text):
    {"type": "user_ack", "message_id": "..."}
    {"type": "bot_text", "message_id": "...", "index": 0, "text": "..."}
    {"type": "turn_end",    "message_id": "..."}
    {"type": "interrupt"}                              # 服务端要求前端立即停播
    {"type": "error", "message": "..."}

说明: 数字人开口由前端把 bot_text 喂给 lm-avatar-chat-sdk 的
`requestToRespond(transcript)` 完成, 服务端 TTS + 唇形一条龙. 后端不再合成
"""
from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from atguigu.domain.messages import (
    BotMessage,
    FocusedObject,
    MessageType,
    UserMessage,
)
from atguigu.infrastructure import database
from atguigu.repository.dialogue_state_repository import DialogueStateRepository
from atguigu.service.dialogue_service import DialogueService
from atguigu.api.dependencies import get_engine

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/avatar/chat")
async def avatar_chat_ws(ws: WebSocket) -> None:
    await ws.accept()
    current_turn: asyncio.Task | None = None

    async def cancel_current(reason: str) -> None:
        nonlocal current_turn
        if current_turn is None or current_turn.done():
            current_turn = None
            return
        current_turn.cancel() # 只是发出取消请求，不是立刻杀死任务。 通知旧的一轮对话：你该停了
        try:
            await current_turn # 等旧的一轮真的停下来   为什么要等？为了避免旧任务还没停完，又启动新任务，导致旧回复和新回复一起往前端发。
        except (asyncio.CancelledError, Exception):
            pass
        finally:
            current_turn = None
        logger.info("WS turn cancelled: %s", reason)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await _safe_send_json(ws, {"type": "error", "message": "invalid json"})
                continue

            msg_type = payload.get("type")
            if msg_type == "user_text":
                # 新消息到达, 强制打断上一轮(若仍在播报)
                await cancel_current("new user_text arrived")
                await _safe_send_json(ws, {"type": "interrupt"})
                current_turn = asyncio.create_task(_run_turn(ws, payload))
            else:
                await _safe_send_json(
                    ws, {"type": "error", "message": f"unknown type: {msg_type}"}
                )
    except WebSocketDisconnect:
        logger.info("WS client disconnected")
    except Exception:
        logger.exception("WS handler crashed")
    finally:
        await cancel_current("ws closing")


async def _run_turn(ws: WebSocket, payload: dict[str, Any]) -> None:
    """处理一次用户输入: 调对话引擎拿回复, 再把回复文本推给前端。"""
    sender_id = payload.get("sender_id")
    if not sender_id:
        await _safe_send_json(ws, {"type": "error", "message": "missing sender_id"})
        return

    text = payload.get("text") or ""
    if not text.strip():
        await _safe_send_json(ws, {"type": "error", "message": "empty text"})
        return

    message_id = payload.get("message_id") or str(uuid.uuid4())
    user_message = UserMessage(
        sender_id=sender_id,
        message_id=message_id,
        type=MessageType.TEXT,
        text=text,
    )

    await _safe_send_json(ws, {"type": "user_ack", "message_id": message_id})

    # 复用现有对话引擎: 自带 DB session 生命周期
    try:
        engine = await get_engine()
        if engine is None:
            raise RuntimeError("dialogue engine not initialized")
        async with database.async_session() as session:
            repository = DialogueStateRepository(session=session)
            service = DialogueService(
                dialogue_state_repository=repository,
                dialogue_engine=engine,
            )
            result = await service.handle_message(user_message)
        messages: list[BotMessage] = result.messages
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.exception("dialogue handle_message failed")
        await _safe_send_json(
            ws, {"type": "error", "message": f"dialogue failed: {e}"}
        )
        return

    for index, bot_msg in enumerate(messages):
        await _safe_send_json(
            ws,
            {
                "type": "bot_text",
                "message_id": message_id,
                "index": index,
                "text": bot_msg.text,
                "object": _focused_object_to_dict(bot_msg.object),
            },
        )

    await _safe_send_json(ws, {"type": "turn_end", "message_id": message_id})


def _focused_object_to_dict(obj: FocusedObject | None) -> dict | None:
    if obj is None:
        return None
    return obj.to_dict()


async def _safe_send_json(ws: WebSocket, data: dict) -> None:
    try:
        await ws.send_text(json.dumps(data, ensure_ascii=False))
    except Exception:
        logger.debug("WS send_json failed (likely client closed)", exc_info=True)
