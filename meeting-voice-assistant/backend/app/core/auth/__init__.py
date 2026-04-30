"""
认证模块

提供 JWT 和密码相关的认证功能
"""

from app.core.auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
)
from app.core.auth.password import hash_password, verify_password
from app.core.auth.dependencies import (
    AuthConfig,
    TokenPayload,
    User,
    get_auth_config,
    get_current_user,
    get_current_user_optional,
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "hash_password",
    "verify_password",
    "AuthConfig",
    "TokenPayload",
    "User",
    "get_auth_config",
    "get_current_user",
    "get_current_user_optional",
]
