"""
统一的数据模型定义

包含:
- SourceTimestamp, SpeakerSummary, Decision, ActionItem, Chapter, SpeakerRole
- TranscriptSegment, AudioAnalysisState, AnalysisResult
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class SourceTimestamp:
    """来源时间戳"""
    start: float
    end: float


@dataclass
class SpeakerSummary:
    """说话人摘要"""
    speaker: str
    summary: str
    source_timestamps: List[SourceTimestamp] = field(default_factory=list)


@dataclass
class Decision:
    """决策点"""
    decision: str
    source_timestamps: List[SourceTimestamp] = field(default_factory=list)


@dataclass
class ActionItem:
    """待办事项"""
    todo: str
    source_timestamps: List[SourceTimestamp] = field(default_factory=list)


@dataclass
class Chapter:
    """章节"""
    title: str
    start_time: int
    end_time: int
    summary: str
    speaker_summaries: List[SpeakerSummary] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    action_items: List[ActionItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "summary": self.summary,
            "speaker_summaries": [
                {
                    "speaker": ss.speaker,
                    "summary": ss.summary,
                    "source_timestamps": [
                        {"start": st.start, "end": st.end}
                        for st in ss.source_timestamps
                    ]
                }
                for ss in self.speaker_summaries
            ],
            "decisions": [
                {
                    "decision": d.decision,
                    "source_timestamps": [
                        {"start": st.start, "end": st.end}
                        for st in d.source_timestamps
                    ]
                }
                for d in self.decisions
            ],
            "action_items": [
                {
                    "todo": ai.todo,
                    "source_timestamps": [
                        {"start": st.start, "end": st.end}
                        for st in ai.source_timestamps
                    ]
                }
                for ai in self.action_items
            ]
        }


@dataclass
class SpeakerRole:
    """发言人员角色"""
    speaker: str
    role: str
    reasoning: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "speaker": self.speaker,
            "role": self.role,
            "reasoning": self.reasoning
        }


@dataclass
class TranscriptSegment:
    """转写片段"""
    text: str
    speaker: Optional[str] = None
    start_time: float = 0.0
    end_time: float = 0.0


@dataclass
class AnalysisResult:
    """会议分析结果（新版统一格式）"""
    theme: str = ""
    summary: str = ""
    chapters: List[Chapter] = field(default_factory=list)
    speaker_roles: List[SpeakerRole] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        all_action_items = []
        for chapter in self.chapters:
            for ai in chapter.action_items:
                all_action_items.append({
                    "todo": ai.todo,
                    "source_timestamps": [
                        {"start": st.start, "end": st.end}
                        for st in ai.source_timestamps
                    ]
                })

        return {
            "theme": self.theme,
            "summary": self.summary,
            "chapters": [c.to_dict() if isinstance(c, Chapter) else c for c in self.chapters],
            "speaker_roles": [r.to_dict() if isinstance(r, SpeakerRole) else r for r in self.speaker_roles],
            "topics": self.topics,
            "key_points": self.key_points,
            "action_items": all_action_items,
        }


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
    chapters: List[Chapter] = field(default_factory=list)  # 章节划分
    summary: str = ""  # 内容摘要（保留兼容）
    speaker_roles: List[SpeakerRole] = field(default_factory=list)  # 发言人员角色

    # 兼容字段（用于兼容旧的输出格式）
    topics: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    action_items_list: List[str] = field(default_factory=list)

    # 元数据
    error: Optional[str] = None
    raw_response: str = ""  # LLM 原始响应
