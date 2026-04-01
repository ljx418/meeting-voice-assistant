"""
数据模型模块
"""

from pydantic import BaseModel
from typing import Optional, Any


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str
    asr_engine: str
    asr_mode: str
    uptime: float
