"""
LLM 分析模块

负责调用大模型对会议内容进行分析
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """会议分析结果"""
    summary: str           # 会议总结
    key_points: list[str]  # 关键点
    action_items: list[str]  # 行动项
    topics: list[str]      # 主题


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
        prompt = self._build_prompt(transcript_text)

        try:
            # 调用 LLM API
            response_text = await self._call_llm_api(prompt)

            # 解析结果
            result = self._parse_response(response_text)

            logger.info(f"[LLMAnalyzer] Analysis completed: summary={result.summary[:50]}...")
            return result

        except Exception as e:
            logger.error(f"[LLMAnalyzer] Analysis failed: {e}")
            # 返回默认结果
            return AnalysisResult(
                summary="分析失败，请稍后重试。",
                key_points=[],
                action_items=[],
                topics=[]
            )

    def _build_prompt(self, transcript_text: str) -> str:
        """构建分析提示词"""
        return f"""你是一个专业的会议助手。请分析以下会议记录，提取关键信息。

会议记录：
{transcript_text}

请以 JSON 格式返回分析结果，包含以下字段：
- summary: 会议总结（100字以内）
- key_points: 关键点列表（3-5个）
- action_items: 行动项列表（如有）
- topics: 主题标签列表（2-4个）

请直接返回 JSON，不要添加其他解释文字。"""

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

    def _parse_response(self, response_text: str) -> AnalysisResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            json_str = self._extract_json(response_text)
            data = json.loads(json_str)

            return AnalysisResult(
                summary=data.get("summary", "（无总结）"),
                key_points=data.get("key_points", []),
                action_items=data.get("action_items", []),
                topics=data.get("topics", [])
            )
        except json.JSONDecodeError as e:
            logger.warning(f"[LLMAnalyzer] Failed to parse JSON: {e}, response: {response_text}")
            # 返回基于原始文本的结果
            return AnalysisResult(
                summary=response_text[:200] if response_text else "（解析失败）",
                key_points=[],
                action_items=[],
                topics=[]
            )

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
