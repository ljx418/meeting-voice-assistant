"""
用户认证 API

提供用户注册、登录和认证相关接口

认证方式：
- HTTP: Authorization: Bearer <token> header
- WebSocket: ?token= <token> query param
- 开发模式：DEV_BYPASS_AUTH=true 时跳过认证
"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field

from app.config import config
from app.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
)
from app.core.auth.dependencies import User
from app.db.user_repository import get_user_repository
from app.utils.logger import setup_logger

logger = setup_logger("auth.api")

router = APIRouter(prefix="/auth", tags=["认证"])


# ============ Request/Response Models ============

class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=100, description="密码")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """用户信息响应"""
    id: str
    username: str
    email: str
    is_active: bool = True


class MessageResponse(BaseModel):
    """消息响应"""
    message: str


# ============ 用户存储（SQLite 持久化）============

def _get_user_repo():
    """获取用户仓库实例"""
    return get_user_repository()


async def create_user(username: str, email: str, password: str):
    """
    创建新用户

    Args:
        username: 用户名
        email: 邮箱
        password: 明文密码

    Returns:
        用户信息字典，创建失败返回 None
    """
    repo = _get_user_repo()
    user = await repo.create_user(username, email, password)

    if user is None:
        logger.warning(f"Registration failed: username or email already exists - {username}")
        return None

    logger.info(f"User created successfully: {username} (id={user['id']})")
    return user


async def authenticate_user(username: str, password: str):
    """
    验证用户凭据

    Args:
        username: 用户名
        password: 明文密码

    Returns:
        用户信息字典，验证失败返回 None
    """
    repo = _get_user_repo()
    user = await repo.authenticate(username, password)

    if user is None:
        logger.warning(f"Login failed: invalid credentials - {username}")
        return None

    logger.info(f"User authenticated successfully: {username}")
    return user


# ============ API Endpoints ============

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    responses={
        201: {"description": "用户创建成功"},
        400: {"description": "用户名或邮箱已存在"},
    },
)
async def register(request: UserRegisterRequest) -> UserResponse:
    """
    用户注册接口

    - **username**: 用户名 (3-50字符)
    - **email**: 邮箱地址
    - **password**: 密码 (6-100字符)
    """
    # 开发模式：允许跳过实际注册
    if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
        dev_user_id = config.jwt.dev_user_id or "dev_user"
        return UserResponse(
            id=dev_user_id,
            username=request.username,
            email=request.email,
            is_active=True,
        )

    user = await create_user(
        username=request.username,
        email=request.email,
        password=request.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )

    return UserResponse(**user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    responses={
        401: {"description": "用户名或密码错误"},
    },
)
async def login(request: UserLoginRequest) -> TokenResponse:
    """
    用户登录接口

    返回 JWT 访问令牌和刷新令牌

    - **username**: 用户名
    - **password**: 密码
    """
    # 开发模式：返回开发令牌
    if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
        dev_user_id = config.jwt.dev_user_id or "dev_user"
        access_token = create_access_token({
            "user_id": dev_user_id,
            "username": request.username,
        })
        refresh_token = create_refresh_token({
            "user_id": dev_user_id,
            "username": request.username,
        })
        logger.info(f"Dev mode login: {request.username}")
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    user = await authenticate_user(request.username, request.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 生成令牌
    access_token = create_access_token({
        "user_id": user["id"],
        "username": user["username"],
        "email": user["email"],
    })
    refresh_token = create_refresh_token({
        "user_id": user["id"],
        "username": user["username"],
    })

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前用户信息",
    responses={
        401: {"description": "未认证"},
    },
)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """
    获取当前登录用户的信息

    需要携带有效的 JWT 访问令牌
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email or "",
        is_active=True,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    responses={
        401: {"description": "刷新令牌无效或已过期"},
    },
)
async def refresh_token(refresh_token: str) -> TokenResponse:
    """
    使用刷新令牌获取新的访问令牌

    - **refresh_token**: 刷新令牌
    """
    payload = verify_token(refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "refresh":
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

    # 生成新令牌
    new_access_token = create_access_token({
        "user_id": user_id,
        "username": username,
        "email": payload.get("email"),
    })
    new_refresh_token = create_refresh_token({
        "user_id": user_id,
        "username": username,
    })

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
    )


@router.get(
    "/verify",
    summary="验证令牌",
    responses={
        200: {"description": "令牌有效"},
        401: {"description": "令牌无效或已过期"},
    },
)
async def verify_token_endpoint(token: str) -> dict:
    """
    验证 JWT 令牌是否有效

    - **token**: JWT 令牌字符串
    """
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    return {
        "valid": True,
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "type": payload.get("type"),
    }


# ============ WebSocket 认证 ============

async def verify_ws_api_key(websocket, api_key: str) -> bool:
    """
    验证 WebSocket API Key

    用于 WebSocket 连接时的 API Key 认证
    兼容旧版 API Key 认证方式
    """
    if not api_key:
        return False

    # 获取配置的 API Key
    configured_key = config.api.get("API_KEY") if hasattr(config, 'api') else None

    # 如果没有配置 API Key，验证总是失败
    if not configured_key:
        return False

    # 简单比较
    return api_key == configured_key


async def verify_ws_jwt_token(token: str) -> bool:
    """
    验证 WebSocket JWT Token

    用于 WebSocket 连接时的 JWT 认证
    """
    if not token:
        return False

    payload = verify_token(token)
    return payload is not None and payload.get("type") == "access"


# ============ HTTP 认证依赖 ============

async def verify_api_key(api_key: str = Depends(lambda: None)) -> str:
    """
    API Key 认证依赖

    用于 FastAPI 路由的 Depends 认证
    返回 api_key 值，如果验证失败则抛出异常
    """
    # 开发模式绕过
    if config.jwt.dev_mode and config.jwt.dev_bypass_auth:
        return config.jwt.dev_user_id or "dev_user"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )

    configured_key = config.api.get("API_KEY") if hasattr(config, 'api') else None
    if not configured_key or api_key != configured_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

    return api_key
