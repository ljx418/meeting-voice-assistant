"""
静态 API Key 认证模块

参考 ADR-001 设计方案：
https://docs/architecture/ADR-001-api-authentication.md

认证方式：
- HTTP: X-API-Key header 或 ?api_key= query param
- WebSocket: ?api_key= query param
- 未配置 API_KEY 时：认证关闭（本地开发模式）
"""

from typing import Optional

from fastapi import HTTPException, status, WebSocket, Query, Security
from fastapi.security import APIKeyHeader, APIKeyQuery

from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger("auth.api_key")

# 安全方案定义
_header_scheme = APIKeyHeader(name="X-API-Key", auto_error=False)
_query_scheme = APIKeyQuery(name="api_key", auto_error=False)

# API Key 配置 - 从统一配置获取
_API_KEY: Optional[str] = config.api.api_key


async def verify_api_key(
    header_key: str = Security(_header_scheme),
    query_key: str = Security(_query_scheme),
) -> None:
    """
    HTTP 端点认证依赖

    支持两种认证方式:
    1. X-API-Key header
    2. ?api_key= query param

    如果 API_KEY 未配置，认证被禁用（本地开发模式）

    Raises:
        HTTPException: 认证失败
    """
    # 本地开发模式：未配置 API_KEY 时跳过认证
    if not _API_KEY:
        logger.debug("Auth disabled: API_KEY not configured")
        return

    provided = header_key or query_key

    if not provided:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if provided != _API_KEY:
        logger.warning(f"Auth failed: invalid API key provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )


async def verify_ws_api_key(websocket: WebSocket, api_key: str = Query(None)) -> bool:
    """
    WebSocket 端点认证

    WebSocket 无法使用自定义 header，认证凭证只能通过 query param 传递

    Args:
        websocket: WebSocket 连接
        api_key: query param 中的 API key

    Returns:
        True 表示认证成功，False 表示认证失败（调用方应关闭连接）
    """
    # 本地开发模式：未配置 API_KEY 时跳过认证
    if not _API_KEY:
        logger.debug("WS Auth disabled: API_KEY not configured")
        return True

    if not api_key:
        logger.warning("WS auth failed: missing API key")
        return False

    if api_key != _API_KEY:
        logger.warning("WS auth failed: invalid API key")
        return False

    return True
