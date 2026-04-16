"""
消息协议定义
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MessageType(str, Enum):
    """消息类型枚举"""

    # 客户端 → 服务端
    START = "start"
    AUDIO = "audio"
    STOP = "stop"

    # 服务端 → 客户端
    STARTED = "started"
    TRANSCRIPT = "transcript"
    ERROR = "error"
    COMPLETED = "completed"


class StartMessage(BaseModel):
    """开始消息"""

    type: str = "start"
    session_id: str
    mode: Optional[str] = "2pass"


class TranscriptMessage(BaseModel):
    """识别结果消息"""

    type: str = "transcript"
    session_id: str
    text: str
    speaker: str = "speaker_0"
    start_time: float = 0.0
    end_time: float = 0.0
    confidence: float = 1.0
    is_final: bool = True
    mode: Optional[str] = None  # "2pass-online" 或 "2pass-offline"


class ErrorMessage(BaseModel):
    """错误消息"""

    type: str = "error"
    message: str


class StartedMessage(BaseModel):
    """开始确认消息"""

    type: str = "started"
    session_id: str
    mode: str = "2pass"
