"""
会议信息解析模块

负责从识别文本中提取:
1. 说话人信息 (speaker)
2. 会议角色 (role: 主持人、记录员等)
3. 会议章节 (chapter)
4. 会议主题 (topic)
"""

import re
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class Chapter:
    """会议章节"""
    id: str
    title: str
    start_time: float
    end_time: Optional[float] = None


@dataclass
class MeetingInfo:
    """
    解析后的会议信息

    Attributes:
        topic: 会议主题
        detected_roles: speaker_id -> role 映射
        detected_chapters: 章节列表
        keywords: 关键词列表
    """
    topic: Optional[str] = None
    detected_roles: dict[str, str] = field(default_factory=dict)
    detected_chapters: list[Chapter] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


class SpeakerParser:
    """
    说话人解析器

    从文本模式中识别说话人提及:
    - "张三说:" -> speaker: 张三
    - "李四认为" -> speaker: 李四
    """

    # 说话人提及正则模式
    SPEAKER_PATTERNS = [
        # "XXX说:", "XXX认为", "XXX指出"
        r'^(\S{2,4})(?:说|认为|指出|表示|提到|补充道|问道|回答|解释道)',
        # "主持人XXX", "记录员XXX"
        r'^(?:主持人|记录员|参会者|嘉宾|专家)(\S{1,4})',
        # "@XXX"
        r'^@(\S{2,4})',
    ]

    def __init__(self):
        self._compiled_patterns = [
            re.compile(p) for p in self.SPEAKER_PATTERNS
        ]

    def parse(self, text: str, speaker_hint: Optional[str] = None) -> Optional[str]:
        """
        从文本中提取说话人

        Args:
            text: 识别文本
            speaker_hint: 来自 ASR 的说话人提示

        Returns:
            说话人名称或 None
        """
        # 如果 ASR 提供了说话人信息，优先使用
        if speaker_hint:
            return speaker_hint

        # 从文本模式匹配说话人
        for pattern in self._compiled_patterns:
            match = pattern.match(text.strip())
            if match:
                speaker_name = match.group(1)
                logger.debug(f"Detected speaker from text: {speaker_name}")
                return speaker_name

        return None


class RoleParser:
    """
    会议角色识别

    识别说话人在当前会议中的角色:
    - 主持人 (host/mod)
    - 记录员 (notetaker)
    - 普通参会者 (participant)
    """

    ROLE_KEYWORDS = {
        "host": ["主持人", "主持", "会议主持", "组织者", "主办方"],
        "notetaker": ["记录", "记一下", "记笔记", "文档", "整理一下"],
        "participant": [],
    }

    def parse(
        self,
        text: str,
        speaker: str,
        current_roles: dict[str, str]
    ) -> Optional[str]:
        """
        从文本中识别角色

        Args:
            text: 识别文本
            speaker: 说话人名称
            current_roles: 当前已分配的角色映射

        Returns:
            角色名称或 None
        """
        # 如果已分配角色，不再重复识别
        if speaker in current_roles:
            return None

        text_lower = text.lower()

        for role, keywords in self.ROLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    logger.info(f"Detected role '{role}' for speaker '{speaker}'")
                    return role

        return None

    def infer_role_from_context(
        self,
        text: str,
        speaker: str,
        current_roles: dict[str, str]
    ) -> Optional[str]:
        """
        根据上下文推断角色

        Args:
            text: 识别文本
            speaker: 说话人
            current_roles: 当前角色

        Returns:
            推断的角色或 None
        """
        # 说话人首次发言时的模式识别
        if speaker not in current_roles:
            # 通常主持人先发言
            if text.startswith(("大家", "各位", "今天", "首先", "欢迎")):
                return "host"

        return None


class ChapterParser:
    """
    会议章节识别

    识别会议中的章节转换:
    - "我们先来看第一部分" -> Chapter: 议程一
    - "接下来" -> 章节切换
    """

    CHAPTER_PATTERNS = [
        (r'^(?:先来|首先|第一(?:部分|个|项|环节))', "议程一"),
        (r'^(?:接下来|然后|第二(?:部分|个|项|环节))', "议程二"),
        (r'^(?:再|接着|第三(?:部分|个|项|环节))', "议程三"),
        (r'^(?:最后|总结|归纳|收尾)', "总结"),
        (r'^(?:休息|茶歇|休息一下)', "休息"),
    ]

    def __init__(self):
        self._current_chapter: Optional[Chapter] = None
        self._chapter_counter = 0

    def parse(self, text: str, timestamp: float) -> Optional[Chapter]:
        """
        识别章节边界

        Args:
            text: 识别文本
            timestamp: 时间戳

        Returns:
            新章节或 None
        """
        for pattern, title in self.CHAPTER_PATTERNS:
            if re.search(pattern, text):
                # 结束当前章节
                if self._current_chapter:
                    self._current_chapter.end_time = timestamp

                # 创建新章节
                self._chapter_counter += 1
                self._current_chapter = Chapter(
                    id=f"chapter_{self._chapter_counter:03d}",
                    title=title,
                    start_time=timestamp,
                )

                logger.info(f"New chapter detected: {title}")
                return self._current_chapter

        return None

    @property
    def current_chapter(self) -> Optional[Chapter]:
        """获取当前章节"""
        return self._current_chapter

    def reset(self) -> None:
        """重置章节状态"""
        self._current_chapter = None
        self._chapter_counter = 0


class TopicParser:
    """
    会议主题识别

    从会议开始阶段识别会议主题
    """

    TOPIC_PATTERNS = [
        # "今天我们讨论XXX"
        r'(?:今天|今天我们|本次|这会儿)(?:讨论|聊|聊一聊|聊聊|谈谈)(.+?)(?:这个|那个|的?话题)?$',
        # "关于XXX的讨论"
        r'(?:关于)(.+?)(?:的?讨论|会议|议题|内容)',
        # "议题是XXX"
        r'(?:议题|主题|题目)(?:是|为)(.+?)$',
    ]

    def __init__(self):
        self._compiled_patterns = [
            re.compile(p) for p in self.TOPIC_PATTERNS
        ]
        self._confirmed_topic: Optional[str] = None

    def parse(self, texts: list[str]) -> Optional[str]:
        """
        从历史文本中推断会议主题

        Args:
            texts: 历史文本列表 (按时间排序)

        Returns:
            识别的主题或 None
        """
        # 如果已有确认的主题，直接返回
        if self._confirmed_topic:
            return self._confirmed_topic

        # 遍历前 N 条文本尝试识别主题
        for text in texts[:10]:
            for pattern in self._compiled_patterns:
                match = pattern.search(text)
                if match:
                    topic = match.group(1).strip()
                    if len(topic) >= 2:
                        self._confirmed_topic = topic
                        logger.info(f"Detected meeting topic: {topic}")
                        return topic

        return None


class MeetingInfoExtractor:
    """
    会议信息提取器 - 整合所有解析器
    """

    def __init__(self):
        self.speaker_parser = SpeakerParser()
        self.role_parser = RoleParser()
        self.chapter_parser = ChapterParser()
        self.topic_parser = TopicParser()

    def process(
        self,
        text: str,
        timestamp: float,
        speaker_hint: Optional[str] = None,
    ) -> MeetingInfo:
        """
        处理识别结果，提取会议信息

        Args:
            text: 识别文本
            timestamp: 时间戳
            speaker_hint: ASR 提供的说话人提示

        Returns:
            提取的会议信息
        """
        info = MeetingInfo()

        # 提取说话人
        speaker = self.speaker_parser.parse(text, speaker_hint)
        if speaker:
            # 提取角色
            role = self.role_parser.parse(text, speaker, info.detected_roles)
            if role:
                info.detected_roles[speaker] = role

        # 检测章节
        chapter = self.chapter_parser.parse(text, timestamp)
        if chapter:
            info.detected_chapters.append(chapter)

        return info

    def extract_topic(self, texts: list[str]) -> Optional[str]:
        """从文本列表中提取主题"""
        return self.topic_parser.parse(texts)

    def reset(self) -> None:
        """重置所有解析器状态"""
        self.chapter_parser.reset()
