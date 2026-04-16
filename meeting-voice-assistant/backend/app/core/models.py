"""
共享数据模型定义

所有模块共用的 dataclass 定义，统一管理避免重复。
"""

from typing import List, Dict, Any, Optional
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