"""
JWT Token 处理模块

提供 JWT token 的创建和验证功能
"""

from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from app.config import config


def create_access_token(data: dict) -> str:
    """
    创建访问令牌

    Args:
        data: 需要编码到 token 中的数据，包含 user_id 等信息

    Returns:
        编码后的 JWT token 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(
        to_encode,
        config.jwt.secret_key,
        algorithm="HS256"
    )


def create_refresh_token(data: dict) -> str:
    """
    创建刷新令牌

    Args:
        data: 需要编码到 token 中的数据，包含 user_id 等信息

    Returns:
        编码后的 JWT token 字符串
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(
        to_encode,
        config.jwt.secret_key,
        algorithm="HS256"
    )


def verify_token(token: str) -> Optional[dict]:
    """
    验证 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        解码后的 payload dict，验证失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            config.jwt.secret_key,
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    解码 JWT token（不验证签名，仅提取数据）

    用于获取 token 中的基本信息而不验证签名

    Args:
        token: JWT token 字符串

    Returns:
        解码后的 payload dict，失败返回 None
    """
    try:
        # 不验证签名，仅提取数据
        payload = jwt.decode(
            token,
            config.jwt.secret_key,
            algorithms=["HS256"],
            options={"verify_signature": False}
        )
        return payload
    except JWTError:
        return None
