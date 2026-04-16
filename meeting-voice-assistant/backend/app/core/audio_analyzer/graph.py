"""
LangGraph 工作流定义
"""

import json
import logging
import uuid
import re
from pathlib import Path
from datetime import datetime
from typing import Generator, Optional, List, Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from .state import (
    AudioAnalysisState, TranscriptSegment, Chapter,
    SpeakerSummary, SpeakerRole, Decision, ActionItem, SourceTimestamp
)
from .prompt import build_analysis_prompt
from .llm_client import LLMClient

logger = logging.getLogger("audio_analyzer.graph")

# LLM 缓存目录
CACHE_DIR = Path(__file__).parent.parent.parent.parent / "llm_cache"
CACHE_DIR.mkdir(exist_ok=True)


def _get_cache_path(session_id: str) -> Path:
    """获取缓存目录路径"""
    cache_path = CACHE_DIR / session_id
    cache_path.mkdir(exist_ok=True, parents=True)
    return cache_path


def _save_llm_cache(session_id: str, prompt: str, response: str) -> None:
    """保存 LLM 请求和响应到缓存"""
    try:
        cache_path = _get_cache_path(session_id)

        # 保存请求
        request_file = cache_path / "llm_request.txt"
        request_file.write_text(prompt, encoding="utf-8")
        logger.info(f"[LLM Cache] Request saved: {request_file}")

        # 保存响应
        response_file = cache_path / "llm_response.json"
        response_file.write_text(response, encoding="utf-8")
        logger.info(f"[LLM Cache] Response saved: {response_file}")

        # 保存元数据
        meta = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "prompt_length": len(prompt),
            "response_length": len(response),
        }
        meta_file = cache_path / "meta.json"
        meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    except Exception as e:
        logger.warning(f"[LLM Cache] Failed to save cache: {e}")


def extract_speakers(state: AudioAnalysisState) -> AudioAnalysisState:
    """提取说话人列表"""
    speakers = set()

    for segment in state.segments:
        if segment.speaker and segment.speaker != "unknown":
            speakers.add(segment.speaker)

    state.speakers = sorted(list(speakers))
    logger.info(f"[AudioAnalyzer] Extracted speakers: {state.speakers}")
    return state


def _extract_json(text: str) -> str:
    """从 LLM 响应中提取 JSON（处理 code fences）"""
    # 移除 code fences (```json ... ``` 或 ``` ... ```)
    json_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(json_pattern, text)
    if match:
        return match.group(1).strip()
    # 如果没有 code fences，尝试直接解析
    return text.strip()


def _parse_timestamps(timestamps: List[Dict[str, Any]]) -> List[SourceTimestamp]:
    """解析时间戳列表"""
    result = []
    for ts in timestamps:
        if isinstance(ts, dict) and "开始" in ts and "结束" in ts:
            result.append(SourceTimestamp(start=ts["开始"], end=ts["结束"]))
        elif isinstance(ts, dict) and "start" in ts and "end" in ts:
            result.append(SourceTimestamp(start=ts["start"], end=ts["end"]))
    return result


def _parse_speaker_summaries(summaries: List[Dict[str, Any]]) -> List[SpeakerSummary]:
    """解析说话人摘要列表"""
    result = []
    for s in summaries:
        if isinstance(s, dict):
            source_timestamps = _parse_timestamps(s.get("来源时间戳", s.get("source_timestamps", [])))
            result.append(SpeakerSummary(
                speaker=s.get("说话人", s.get("speaker", "")),
                summary=s.get("摘要内容", s.get("summary", "")),
                source_timestamps=source_timestamps
            ))
    return result


def _parse_decisions(decisions: List[Dict[str, Any]]) -> List[Decision]:
    """解析决策点列表"""
    result = []
    for d in decisions:
        if isinstance(d, dict):
            source_timestamps = _parse_timestamps(d.get("来源时间戳", d.get("source_timestamps", [])))
            result.append(Decision(
                decision=d.get("决策内容", d.get("decision", "")),
                source_timestamps=source_timestamps
            ))
    return result


def _parse_action_items(action_items: List[Dict[str, Any]]) -> List[ActionItem]:
    """解析待办事项列表"""
    result = []
    for a in action_items:
        if isinstance(a, dict):
            source_timestamps = _parse_timestamps(a.get("来源时间戳", a.get("source_timestamps", [])))
            result.append(ActionItem(
                todo=a.get("待办内容", a.get("todo", "")),
                source_timestamps=source_timestamps
            ))
    return result


def _parse_chapters(chapters: List[Dict[str, Any]]) -> List[Chapter]:
    """解析章节列表"""
    result = []
    for c in chapters:
        if isinstance(c, dict):
            result.append(Chapter(
                title=c.get("章节标题", c.get("title", "")),
                start_time=c.get("起始时间", c.get("start_time", 0)),
                end_time=c.get("结束时间", c.get("end_time", 0)),
                summary=c.get("本章摘要", c.get("summary", "")),
                speaker_summaries=_parse_speaker_summaries(
                    c.get("发言概要", c.get("speaker_summaries", []))
                ),
                decisions=_parse_decisions(c.get("决策点", c.get("decisions", []))),
                action_items=_parse_action_items(c.get("待办事项", c.get("action_items", [])))
            ))
    return result


def _parse_speaker_roles(roles: List[Dict[str, Any]]) -> List[SpeakerRole]:
    """解析发言人员角色列表"""
    result = []
    for r in roles:
        if isinstance(r, dict):
            result.append(SpeakerRole(
                speaker=r.get("说话人标识", r.get("speaker", "")),
                role=r.get("角色", r.get("role", "")),
                reasoning=r.get("判断依据", r.get("reasoning", ""))
            ))
    return result


def analyze_content(state: AudioAnalysisState, llm_client: LLMClient) -> AudioAnalysisState:
    """调用 LLM 分析音频内容"""
    session_id = getattr(state, "session_id", None) or f"llm_{uuid.uuid4().hex[:8]}"

    try:
        # 构建提示词
        prompt = build_analysis_prompt(state.transcript_text)

        # 调用 LLM
        response = llm_client.invoke(prompt)
        state.raw_response = response

        # 保存缓存
        _save_llm_cache(session_id, prompt, response)

        # 解析 JSON 响应
        json_text = _extract_json(response)
        result = json.loads(json_text)

        # 填充结果
        state.theme = result.get("主题", result.get("theme", ""))
        state.summary = result.get("内容摘要", result.get("summary", ""))

        # 解析章节
        state.chapters = _parse_chapters(result.get("章节划分", result.get("chapters", [])))

        # 解析发言人员角色
        state.speaker_roles = _parse_speaker_roles(
            result.get("发言人员角色", result.get("speaker_roles", []))
        )

        logger.info(f"[AudioAnalyzer] Analysis completed: theme={state.theme[:50]}..., chapters={len(state.chapters)}")

    except json.JSONDecodeError as e:
        logger.error(f"[AudioAnalyzer] JSON parse error: {e}, response: {response[:500] if state.raw_response else 'N/A'}")
        state.error = f"JSON 解析错误: {e}"
    except Exception as e:
        logger.error(f"[AudioAnalyzer] Analysis error: {e}")
        state.error = f"分析错误: {e}"

    return state


def should_retry(state: AudioAnalysisState) -> bool:
    """判断是否需要重试"""
    return state.error is not None and "API" in (state.error or "")


def build_analysis_graph(llm_client: LLMClient) -> StateGraph:
    """构建分析工作流图"""

    # 定义节点
    def extract_speakers_node(state: AudioAnalysisState) -> AudioAnalysisState:
        return extract_speakers(state)

    def analyze_node(state: AudioAnalysisState) -> AudioAnalysisState:
        return analyze_content(state, llm_client)

    # 创建图
    workflow = StateGraph(AudioAnalysisState)

    # 添加节点
    workflow.add_node("extract_speakers", extract_speakers_node)
    workflow.add_node("analyze", analyze_node)

    # 设置入口点
    workflow.set_entry_point("extract_speakers")
    workflow.add_edge("extract_speakers", "analyze")
    workflow.add_edge("analyze", END)

    return workflow.compile()


class AudioAnalysisGraph:
    """音频分析图运行器"""

    def __init__(self, llm_client: LLMClient):
        self.graph = build_analysis_graph(llm_client)

    def run(self, state: AudioAnalysisState) -> AudioAnalysisState:
        """运行工作流"""
        result = self.graph.invoke(state)
        # langgraph returns a dict, convert back to AudioAnalysisState
        if isinstance(result, dict):
            state.transcript_text = result.get("transcript_text", state.transcript_text)
            state.segments = result.get("segments", state.segments)
            state.speakers = result.get("speakers", state.speakers)
            state.theme = result.get("theme", state.theme)
            state.chapters = result.get("chapters", state.chapters)
            state.summary = result.get("summary", state.summary)
            state.speaker_roles = result.get("speaker_roles", state.speaker_roles)
            state.error = result.get("error", state.error)
            state.raw_response = result.get("raw_response", state.raw_response)
        return state
