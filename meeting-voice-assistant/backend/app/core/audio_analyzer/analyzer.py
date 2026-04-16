"""
音频内容分析器

基于 langchain/langgraph 的音频转写内容分析
"""

import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from .state import (
    AudioAnalysisState, TranscriptSegment, Chapter,
    SpeakerSummary, SpeakerRole, Decision, ActionItem, SourceTimestamp
)
from .graph import AudioAnalysisGraph
from .llm_client import LLMClient
from .config import get_config

logger = logging.getLogger("audio_analyzer")


@dataclass
class AnalysisResult:
    """分析结果"""
    theme: str
    summary: str
    chapters: List[Dict[str, Any]]
    speaker_roles: List[Dict[str, str]]
    topics: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    raw_response: str = ""

    @classmethod
    def from_state(cls, state: AudioAnalysisState) -> "AnalysisResult":
        """从状态创建结果"""
        # 从章节划分提取主题标签作为 topics
        topics = []
        key_points = []
        action_items = []

        # 从摘要中提取可能的 key_points（这里简化处理）
        if state.summary:
            # 简单按句号分割摘要
            sentences = [s.strip() for s in state.summary.split("。") if s.strip()]
            key_points = sentences[:5] if sentences else []

        # 从 chapters 中提取所有 action_items
        all_action_items = []
        for chapter in state.chapters:
            for ai in chapter.action_items:
                all_action_items.append({
                    "todo": ai.todo,
                    "source_timestamps": [
                        {"start": st.start, "end": st.end}
                        for st in ai.source_timestamps
                    ]
                })

        return cls(
            theme=state.theme,
            summary=state.summary,
            chapters=[c.to_dict() if isinstance(c, Chapter) else c for c in state.chapters],
            speaker_roles=[r.to_dict() if isinstance(r, SpeakerRole) else r for r in state.speaker_roles],
            topics=topics,
            key_points=key_points,
            action_items=all_action_items,
            raw_response=state.raw_response,
        )


class AudioAnalyzer:
    """
    音频内容分析器

    使用 langchain/langgraph 进行任务编排，对音频转写内容进行深度分析。

    使用示例:
    ```python
    analyzer = AudioAnalyzer()

    # 分析转写文本
    result = analyzer.analyze_transcript("会议内容转写文本...")

    # 分析结构化片段
    segments = [
        TranscriptSegment(text="你好", speaker="speaker_0", start_time=0.0, end_time=2.0),
        TranscriptSegment(text="大家好", speaker="speaker_1", start_time=2.5, end_time=5.0),
    ]
    result = analyzer.analyze_segments(segments)
    ```
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        """
        初始化分析器

        Args:
            provider: LLM provider ("minimax" or "deepseek")
            api_key: API 密钥
            endpoint: API 端点
        """
        config = get_config()

        if provider:
            config.provider = provider
        if api_key:
            if config.provider == "minimax":
                config.minimax_api_key = api_key
            else:
                config.deepseek_api_key = api_key
        if endpoint:
            if config.provider == "minimax":
                config.minimax_endpoint = endpoint
            else:
                config.deepseek_endpoint = endpoint

        self.llm_client = LLMClient(config)
        self.graph = AudioAnalysisGraph(self.llm_client)
        logger.info("[AudioAnalyzer] Initialized")

    def analyze_transcript(self, transcript_text: str) -> AnalysisResult:
        """
        分析转写文本

        Args:
            transcript_text: 音频转写文本

        Returns:
            AnalysisResult: 分析结果
        """
        logger.info(f"[AudioAnalyzer] Analyzing transcript: {len(transcript_text)} chars")

        # 构建初始状态
        state = AudioAnalysisState(
            transcript_text=transcript_text,
            segments=[],
        )

        # 运行工作流
        result_state = self.graph.run(state)

        # 返回结果
        return AnalysisResult.from_state(result_state)

    def analyze_segments(self, segments: List[TranscriptSegment]) -> AnalysisResult:
        """
        分析结构化转写片段

        Args:
            segments: 转写片段列表

        Returns:
            AnalysisResult: 分析结果
        """
        logger.info(f"[AudioAnalyzer] Analyzing {len(segments)} segments")

        # 构建转写文本
        transcript_lines = []
        for seg in segments:
            speaker_label = seg.speaker or "unknown"
            time_range = f"[{seg.start_time:.1f}s - {seg.end_time:.1f}s]"
            transcript_lines.append(f"{time_range} {speaker_label}: {seg.text}")

        transcript_text = "\n".join(transcript_lines)

        # 构建初始状态
        state = AudioAnalysisState(
            transcript_text=transcript_text,
            segments=segments,
        )

        # 运行工作流
        result_state = self.graph.run(state)

        # 返回结果
        return AnalysisResult.from_state(result_state)

    def _format_time(self, seconds: float) -> str:
        """格式化时间"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
