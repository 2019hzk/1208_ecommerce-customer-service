"""阿里云万相数字人(灵眸)会话客户端: 封装 CreateChatSession。

供前端 `lm-avatar-chat-sdk` 初始化云渲染数字人使用。
SDK 调用是阻塞的, 通过 `asyncio.to_thread` 包装成异步接口供 FastAPI 使用。

"""
from __future__ import annotations

import logging
import uuid
import asyncio
from typing import Any

from alibabacloud_lingmou20250527.client import Client as LingMouClient
from alibabacloud_lingmou20250527 import models as lm_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models

from atguigu.config.config import settings

logger = logging.getLogger(__name__)

_client: LingMouClient | None = None


def init_avatar_client() -> None:
    """在 FastAPI lifespan 中调用, 提前完成客户端初始化。"""
    global _client
    if _client is not None:
        return
    if not settings.avatar_access_key_id or not settings.avatar_access_key_secret:
        logger.warning(
            "Avatar AccessKey is not configured; lazy init will fail on first request."
        )
        return
    _client = _build_client()
    logger.info("Avatar client initialized. endpoint=%s", settings.avatar_endpoint)


def _build_client() -> LingMouClient:
    config = open_api_models.Config(
        access_key_id=settings.avatar_access_key_id,
        access_key_secret=settings.avatar_access_key_secret,
    )
    config.endpoint = settings.avatar_endpoint
    return LingMouClient(config)


def _get_client() -> LingMouClient:
    global _client
    if _client is None:
        if not settings.avatar_access_key_id or not settings.avatar_access_key_secret:
            raise RuntimeError(
                "Avatar AccessKey 未配置, 请在 .env 设置 "
                "AVATAR_ACCESS_KEY_ID / AVATAR_ACCESS_KEY_SECRET"
            )
        _client = _build_client()
    return _client


def _rtc_params_to_dict(rtc) -> dict[str, Any]:
    if rtc is None:
        return {}
    return {
        "appId": rtc.app_id,
        "channel": rtc.channel,
        "nonce": rtc.nonce,
        "timestamp": rtc.timestamp,
        "token": rtc.token,
        "gslb": rtc.gslb,
        "clientUserId": rtc.client_user_id,
        "serverUserId": rtc.server_user_id,
        "avatarUserId": rtc.avatar_user_id,
    }



def _do_create(device_id: str) -> dict[str, Any]:
    """对应官方 demo:
    client.create_chat_session_with_options(project_id, request, headers, runtime)
    project_id 是控制台项目主键(如 'C1rRS1KmS3WurHor8HXYlSkQ');
    request 里通常只填 instance_id, 其余 device_id 由调用方按需补。
    """
    client = _get_client()
    project_id = settings.avatar_project_id
    if not project_id:
        raise RuntimeError("Avatar 项目 ID 未配置, 请在 .env 设置 AVATAR_PROJECT_ID")

    req_kwargs: dict[str, Any] = {}
    if settings.avatar_instance_id:
        req_kwargs["instance_id"] = settings.avatar_instance_id
    if device_id:
        req_kwargs["device_id"] = device_id
    if settings.avatar_license:
        req_kwargs["license"] = settings.avatar_license
    if settings.avatar_platform:
        req_kwargs["platform"] = settings.avatar_platform
    req = lm_models.CreateChatSessionRequest(**req_kwargs)

    resp = client.create_chat_session_with_options(
        project_id, req, {}, util_models.RuntimeOptions()
    )
    data = getattr(resp.body, "data", None)
    if data is None:
        raise RuntimeError(
            f"CreateChatSession returned empty data. request_id={getattr(resp.body, 'request_id', None)}"
        )
    return {
        "sessionId": data.session_id,
        "rtcParams": _rtc_params_to_dict(data.rtc_params),
    }


def _create_chat_session_sync(device_id: str) -> dict[str, Any]:
    return _do_create(device_id)


async def create_chat_session(device_id: str | None = None) -> dict[str, Any]:
    """创建一次数字人云渲染会话, 返回前端 SDK 初始化所需 JSON。"""
    device = device_id or str(uuid.uuid4())

    payload = await asyncio.to_thread(_create_chat_session_sync, device)
    return payload
