"""
数据模型 - 音频相关
"""

from pydantic import BaseModel, Field
from typing import Optional


class AudioConfig(BaseModel):
    """音频配置"""
    sample_rate: int = Field(default=16000, description="采样率 Hz")
    channels: int = Field(default=1, description="声道数")
    sample_width: int = Field(default=2, description="采样位深 (bytes)")


class ControlMessage(BaseModel):
    """控制消息"""
    type: str = Field(default="control", description="消息类型")
    action: str = Field(description="动作: start/stop/pause/resume")
    metadata: Optional[dict] = Field(default=None, description="元数据")


class TranscriptMessage(BaseModel):
    """转写结果消息"""
    type: str = Field(default="transcript")
    seq: int = Field(description="序列号")
    data: dict = Field(description="转写数据")
