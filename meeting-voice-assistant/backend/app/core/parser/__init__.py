"""
语义解析模块

提供说话人、角色、章节、主题等会议信息的解析能力
"""

from .meeting_info import (
    MeetingInfo,
    Chapter,
    MeetingInfoExtractor,
    SpeakerParser,
    RoleParser,
    ChapterParser,
    TopicParser,
)

__all__ = [
    "MeetingInfo",
    "Chapter",
    "MeetingInfoExtractor",
    "SpeakerParser",
    "RoleParser",
    "ChapterParser",
    "TopicParser",
]
