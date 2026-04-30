"""
认证依赖模块

提供 FastAPI 依赖注入函数，用于保护 API 端点
"""

from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.config import config
from app.core.auth.jwt_handler import verify_token

# HTTP Bearer 认证方案
security = HTTPBearer(auto_error=False)


class AuthConfig(BaseModel):
    """认证配置"""
    dev_mode: bool = False
    dev_user_id: Optional[str] = None
    dev_bypass_auth: bool = False


class TokenPayload(BaseModel):
    """Token payload 模型"""
    user_id: str
    username: str
    exp: int
    type: str


class User(BaseModel):
    """当前用户模型"""
    id: str
    username: str
    email: Optional[str] = None


@lru_cache()
def get_auth_config() -> AuthConfig:
    """
    获取认证配置

    从环境变量读取认证配置：
    - DEV_MODE: 开发模式开关
    - DEV_USER_ID: 开发模式默认用户 ID
    - DEV_BYPASS_AUTH: 开发模式跳过认证

    Returns:
        AuthConfig 实例
    """
    dev_mode = config.jwt.get("DEV_MODE", "false").lower() == "true"
    dev_user_id = config.jwt.get("DEV_USER_ID") if dev_mode else None
    dev_bypass_auth = config.jwt.get("DEV_BYPASS_AUTH", "false").lower() == "true"

    return AuthConfig(
        dev_mode=dev_mode,
        dev_user_id=dev_user_id,
        dev_bypass_auth=dev_bypass_auth
    )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    获取当前认证用户

    开发模式下，如果配置了 DEV_BYPASS_AUTH=true，
    将返回一个默认的开发用户，绕过 JWT 认证。

    Args:
        credentials: HTTP Bearer 凭证

    Returns:
        User 实例

    Raises:
        HTTPException: 认证失败时抛出
    """
    auth_config = get_auth_config()

    # 开发模式逃生通道
    if auth_config.dev_mode and auth_config.dev_bypass_auth:
        return User(
            id=auth_config.dev_user_id or "dev_user",
            username="dev_user",
            email="dev@localhost"
        )

    # 正常 JWT 验证
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证 token 类型
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    username = payload.get("username")

    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(id=user_id, username=username, email=payload.get("email"))


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """
    获取当前用户（可选）

    与 get_current_user 类似，但认证失败时返回 None 而不是抛出异常

    Returns:
        User 实例或 None
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
