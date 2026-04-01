"""
LangGraph 状态定义
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class TranscriptSegment:
    """转写片段"""
    text: str
    speaker: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class AudioAnalysisState:
    """音频分析状态"""

    # 输入
    transcript_text: str = ""  # 原始转写文本
    segments: List[TranscriptSegment] = field(default_factory=list)  # 结构化片段

    # 中间状态
    speakers: List[str] = field(default_factory=list)  # 识别出的说话人列表

    # 分析结果
    theme: str = ""  # 主题
    chapters: List[Dict[str, Any]] = field(default_factory=list)  # 章节划分
    summary: str = ""  # 内容摘要
    speaker_roles: List[Dict[str, str]] = field(default_factory=list)  # 发言人员角色

    # 元数据
    error: Optional[str] = None
    raw_response: str = ""  # LLM 原始响应
