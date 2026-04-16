"""
LLM 分析模块

负责调用大模型对会议内容进行分析
"""

import asyncio
import json
import logging
import re
from pathlib import Path
from typing import Optional, List, Dict, Any

import aiohttp

from app.core.models import (
    AnalysisResult,
    SourceTimestamp,
    SpeakerSummary,
    Decision,
    ActionItem,
    Chapter,
    SpeakerRole,
)

logger = logging.getLogger(__name__)


LLM_ANALYSIS_PROMPT = """# 角色与任务
你是一个专业的会议/音频内容分析助手。你的任务是根据用户提供的语音转写文本，进行深度分析，并严格按照指定格式输出结果。

# 输入说明
用户将提供一段或多段对话的转写文本，包含：
- 说话人标识（例如 `[0.0s - 5.2s] speaker_0: 你好`）
- 时间戳（`[开始时间 - 结束时间]`）
- 对话内容

你需要基于对话的实际内容进行客观分析，不要添加转写文本中不存在的信息。

# 输出格式
请严格按以下 JSON 格式输出，不要添加任何额外文字：

```json
{{
  "主题": "一句话概括整个音频的核心议题或主要内容",
  "内容摘要": "对整个会议内容的简要总结，概括主要讨论内容和结论",
  "章节划分": [
    {{
      "章节标题": "例如：开场介绍/讨论产品路线图/总结",
      "起始时间": 0,
      "结束时间": 120,
      "本章摘要": "本段的核心讨论内容和结论",
      "发言概要": [
        {{
          "说话人": "speaker_0",
          "摘要内容": "该说话人在本段的主要发言内容概括",
          "来源时间戳": [{{"开始": 5, "结束": 25}}, {{"开始": 45, "结束": 67}}]
        }}
      ],
      "决策点": [
        {{
          "决策内容": "确定Q3发布MVP",
          "来源时间戳": [{{"开始": 120, "结束": 135}}]
        }}
      ],
      "待办事项": [
        {{
          "待办内容": "调研竞品分析方案",
          "来源时间戳": [{{"开始": 250, "结束": 267}}]
        }}
      ]
    }}
  ],
  "发言人员角色": [
    {{
      "说话人标识": "speaker_0",
      "角色": "产品负责人",
      "判断依据": "基于其发言内容、提问方式、总结性话语等简要说明"
    }}
  ]
}}
```

# 重要提示
1. 只分析文本中实际存在的内容，不要推测未明确表达的信息
2. 章节划分应反映对话的自然逻辑分段，每段时长建议 3-10 分钟
3. "来源时间戳"必须精确到具体的转写片段时间范围，用于回溯原始内容
4. 如果某章节没有决策点或待办事项，对应数组可为空
5. 每个说话人的"来源时间戳"应列出该说话人在本章所有发言的时间段
6. 决策点是指明确做出的结论、决定或承诺，不是讨论中的意见


# 待分析的转写文本

{transcript_text}
"""


class LLMAnalyzer:
    """LLM 会议分析器"""

    def __init__(
        self,
        provider: str,
        api_key: Optional[str],
        endpoint: str,
        model: str
    ):
        self.provider = provider
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info(f"[LLMAnalyzer] Initialized with provider={provider}, model={model}")

    async def initialize(self) -> None:
        """初始化 HTTP 会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """关闭 HTTP 会话"""
        if self.session:
            await self.session.close()
            self.session = None

    @staticmethod
    def save_result(session_id: str, result: AnalysisResult, output_dir: Optional[Path] = None) -> None:
        """
        保存 LLM 分析结果到文件

        Args:
            session_id: 会话 ID
            result: 分析结果
            output_dir: 输出目录，默认使用 workspace/output/{session_id}/
        """
        try:
            from app.config import config
            if output_dir is None:
                output_dir = config.WORKSPACE_OUTPUT_DIR / session_id
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存完整分析结果 (analysis.json)
            analysis_path = output_dir / "analysis.json"
            analysis_path.write_text(json.dumps(result.to_dict(), ensure_ascii=False, indent=2), encoding='utf-8')
            logger.info(f"[LLMAnalyzer] Result saved to: {analysis_path}")

            # 保存原始 LLM 响应 (raw_response.txt)
            if result.raw_response:
                raw_path = output_dir / "raw_response.txt"
                raw_path.write_text(result.raw_response, encoding='utf-8')
                logger.info(f"[LLMAnalyzer] Raw response saved to: {raw_path}")

        except Exception as e:
            logger.error(f"[LLMAnalyzer] Failed to save result: {e}")

    async def analyze_meeting(
        self,
        audio_path: Path,
        transcripts: list
    ) -> AnalysisResult:
        """
        分析会议音频和文本

        Args:
            audio_path: 音频文件路径
            transcripts: 转写文本列表

        Returns:
            AnalysisResult: 分析结果
        """
        await self.initialize()

        # 构建转写文本
        transcript_text = "\n".join([
            f"[{t.start_time:.1f}s - {t.end_time:.1f}s] {t.text}"
            for t in transcripts
        ])

        # 如果没有转写文本，使用默认提示
        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        return await self.analyze_text(transcript_text)

    async def analyze_text(self, transcript_text: str) -> AnalysisResult:
        """
        分析纯文本转写内容

        Args:
            transcript_text: 转写文本

        Returns:
            AnalysisResult: 分析结果
        """
        await self.initialize()

        # 如果没有转写文本，使用默认提示
        if not transcript_text:
            transcript_text = "（暂无转写文本）"

        # 构建 prompt
        prompt = LLM_ANALYSIS_PROMPT.format(transcript_text=transcript_text)

        try:
            # 调用 LLM API
            response_text = await self._call_llm_api(prompt)

            # 解析结果
            result = self._parse_response(response_text)

            logger.info(f"[LLMAnalyzer] Analysis completed: theme={result.theme[:50] if result.theme else 'N/A'}...")
            return result

        except Exception as e:
            logger.error(f"[LLMAnalyzer] Analysis failed: {e}")
            # 返回默认结果
            return AnalysisResult(
                theme="",
                summary="分析失败，请稍后重试。",
                chapters=[],
                speaker_roles=[],
                topics=[],
                key_points=[],
                action_items=[],
                raw_response=""
            )

    def _build_prompt(self, transcript_text: str) -> str:
        """构建分析提示词（兼容旧接口）"""
        return LLM_ANALYSIS_PROMPT.format(transcript_text=transcript_text)

    async def _call_llm_api(self, prompt: str) -> str:
        """调用 LLM API"""
        if self.provider == "dashscope":
            return await self._call_dashscope(prompt)
        elif self.provider == "openai":
            return await self._call_openai(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    async def _call_dashscope(self, prompt: str) -> str:
        """调用 DashScope API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.7
            }
        }

        async with self.session.post(
            self.endpoint,
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"[LLMAnalyzer] DashScope API error: {response.status} - {error_text}")
                raise Exception(f"DashScope API error: {response.status}")

            result = await response.json()

            # 解析 DashScope 响应
            if "output" in result and "text" in result["output"]:
                return result["output"]["text"]
            elif "choices" in result:
                return result["choices"][0]["message"]["content"]
            else:
                logger.warning(f"[LLMAnalyzer] Unexpected DashScope response format: {result}")
                return json.dumps(result)

    async def _call_openai(self, prompt: str) -> str:
        """调用 OpenAI API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个专业的会议助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        async with self.session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                logger.error(f"[LLMAnalyzer] OpenAI API error: {response.status} - {error_text}")
                raise Exception(f"OpenAI API error: {response.status}")

            result = await response.json()
            return result["choices"][0]["message"]["content"]

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON"""
        # 尝试找 JSON 代码块
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            if end > start:
                return text[start:end].strip()

        # 尝试找 { 和 }
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return text[start:end+1]

        # 返回原始文本
        return text

    def _parse_timestamps(self, timestamps: List[Dict[str, Any]]) -> List[SourceTimestamp]:
        """解析时间戳列表"""
        result = []
        for ts in timestamps:
            if isinstance(ts, dict) and "开始" in ts and "结束" in ts:
                result.append(SourceTimestamp(start=ts["开始"], end=ts["结束"]))
        return result

    def _parse_speaker_summaries(self, summaries: List[Dict[str, Any]]) -> List[SpeakerSummary]:
        """解析说话人摘要列表"""
        result = []
        for s in summaries:
            if isinstance(s, dict):
                source_timestamps = self._parse_timestamps(
                    s.get("来源时间戳", [])
                )
                result.append(SpeakerSummary(
                    speaker=s.get("说话人", ""),
                    summary=s.get("摘要内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_decisions(self, decisions: List[Dict[str, Any]]) -> List[Decision]:
        """解析决策点列表"""
        result = []
        for d in decisions:
            if isinstance(d, dict):
                source_timestamps = self._parse_timestamps(
                    d.get("来源时间戳", [])
                )
                result.append(Decision(
                    decision=d.get("决策内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_action_items(self, action_items: List[Dict[str, Any]]) -> List[ActionItem]:
        """解析待办事项列表"""
        result = []
        for a in action_items:
            if isinstance(a, dict):
                source_timestamps = self._parse_timestamps(
                    a.get("来源时间戳", [])
                )
                result.append(ActionItem(
                    todo=a.get("待办内容", ""),
                    source_timestamps=source_timestamps
                ))
        return result

    def _parse_chapters(self, chapters: List[Dict[str, Any]]) -> List[Chapter]:
        """解析章节列表"""
        result = []
        for c in chapters:
            if isinstance(c, dict):
                result.append(Chapter(
                    title=c.get("章节标题", ""),
                    start_time=c.get("起始时间", 0),
                    end_time=c.get("结束时间", 0),
                    summary=c.get("本章摘要", ""),
                    speaker_summaries=self._parse_speaker_summaries(
                        c.get("发言概要", [])
                    ),
                    decisions=self._parse_decisions(c.get("决策点", [])),
                    action_items=self._parse_action_items(c.get("待办事项", []))
                ))
        return result

    def _parse_speaker_roles(self, roles: List[Dict[str, Any]]) -> List[SpeakerRole]:
        """解析发言人员角色列表"""
        result = []
        for r in roles:
            if isinstance(r, dict):
                result.append(SpeakerRole(
                    speaker=r.get("说话人标识", ""),
                    role=r.get("角色", ""),
                    reasoning=r.get("判断依据", "")
                ))
        return result

    def _parse_response(self, response_text: str) -> AnalysisResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)

            # 解析章节
            chapters = self._parse_chapters(data.get("章节划分", data.get("chapters", [])))

            # 解析发言人员角色
            speaker_roles = self._parse_speaker_roles(
                data.get("发言人员角色", data.get("speaker_roles", []))
            )

            # 提取主题
            theme = data.get("主题", "")
            summary = data.get("内容摘要", "")

            # 从章节提取 action_items
            all_action_items = []
            for chapter in chapters:
                for ai in chapter.action_items:
                    all_action_items.append({
                        "todo": ai.todo,
                        "source_timestamps": [
                            {"start": st.start, "end": st.end}
                            for st in ai.source_timestamps
                        ]
                    })

            # 提取 topics
            topics = data.get("topics", data.get("主题标签", []))
            if isinstance(topics, str):
                topics = [topics]

            return AnalysisResult(
                theme=theme,
                summary=summary,
                chapters=chapters,
                speaker_roles=speaker_roles,
                topics=topics,
                key_points=[],
                action_items=all_action_items,
                raw_response=response_text
            )

        except json.JSONDecodeError as e:
            logger.warning(f"[LLMAnalyzer] Failed to parse JSON: {e}, response: {response_text[:500]}")
            # 返回基于原始文本的结果
            return AnalysisResult(
                theme="",
                summary=response_text[:200] if response_text else "（解析失败）",
                chapters=[],
                speaker_roles=[],
                topics=[],
                key_points=[],
                action_items=[],
                raw_response=response_text
            )
