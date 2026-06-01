"""数字人云渲染相关 HTTP 路由。"""
from fastapi import APIRouter, Query

from atguigu.api.schema import AvatarSessionResponse
from atguigu.infrastructure import avatar

router = APIRouter()


@router.get("/api/avatar/session")
async def create_avatar_session(
    sender_id: str | None = Query(default=None, description="可选: 透传作为 deviceId"),
) -> AvatarSessionResponse:
    """创建/复用数字人云渲染会话, 给前端 SDK 初始化。
    """
    data = await avatar.create_chat_session(device_id=sender_id)
    return AvatarSessionResponse(**data)
