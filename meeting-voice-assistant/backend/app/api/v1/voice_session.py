"""
VoiceSession 组件模块

将 VoiceSession 拆分为多个职责单一的组件：
- AudioBuffer: 音频缓冲管理
- TranscriptionHandler: ASR 结果处理
- MeetingAnalyzer: LLM 分析协调
- SessionStateManager: 状态持久化
- GraphRAGNotifier: GraphRAG 事件通知
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable, Awaitable

import httpx

from app.core.asr import ASRResult
from app.core.audio_cache import AudioCache
from app.core.llm_analyzer import LLMAnalyzer, AnalysisResult
from app.core.session_store import (
    SessionStore, SessionStatus, TranscriptRecord,
    get_session_store_sync
)
from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger("ws.session")


class AudioBuffer:
    """音频缓冲管理器"""

    def __init__(
        self,
        cache_dir: Path,
        max_chunks: int = 1000,
        max_total_bytes: int = 100 * 1024 * 1024
    ):
        self.audio_cache = AudioCache(cache_dir)
        self.chunks: list[bytes] = []
        self.max_chunks = max_chunks
        self.max_total_bytes = max_total_bytes
        self._closed = False

    @property
    def is_empty(self) -> bool:
        return len(self.chunks) == 0

    @property
    def total_bytes(self) -> int:
        return sum(len(c) for c in self.chunks)

    def append(self, audio_data: bytes) -> None:
        """添加音频数据到缓冲区"""
        if self._closed:
            return

        total_bytes = self.total_bytes + len(audio_data)
        if len(self.chunks) >= self.max_chunks or total_bytes > self.max_total_bytes:
            logger.warning(
                f"Audio buffer full (chunks={len(self.chunks)}, bytes={total_bytes}), "
                "dropping oldest chunk"
            )
            if self.chunks:
                self.chunks.pop(0)

        self.chunks.append(audio_data)
        logger.debug(
            f"process_audio: chunks len={len(self.chunks)}, "
            f"total_bytes={self.total_bytes}"
        )

    async def save(self, session_id: str) -> Optional[Path]:
        """保存音频到缓存"""
        if not config.cache.enabled or not self.chunks:
            logger.warning(
                f"Audio not saved: chunks empty or cache disabled"
            )
            return None

        audio_data = b''.join(self.chunks)
        logger.info(
            f"Saving audio: {len(self.chunks)} chunks, {len(audio_data)} bytes"
        )
        audio_path = await self.audio_cache.save_audio(session_id, audio_data)
        logger.info(f"Audio cached: {audio_path}")
        return audio_path

    def clear(self) -> None:
        """清空缓冲区"""
        self.chunks.clear()

    def close(self) -> None:
        """关闭缓冲区"""
        self._closed = True
        self.clear()

    def get_all_audio(self) -> bytes:
        """获取所有音频数据"""
        return b''.join(self.chunks)


class TranscriptionHandler:
    """转写结果处理器"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.seq = 0
        self.transcripts: list[ASRResult] = []
        self._closed = False

    @property
    def is_closed(self) -> bool:
        return self._closed

    def set_closed(self, closed: bool) -> None:
        self._closed = closed

    async def handle_result(
        self,
        result: ASRResult,
        sender: Callable[[dict], Awaitable[None]]
    ) -> None:
        """处理 ASR 识别结果"""
        if self._closed:
            return

        self.seq += 1
        self.transcripts.append(result)

        try:
            await sender({
                "type": "transcript",
                "seq": self.seq,
                "data": {
                    "text": result.text,
                    "start_time": result.start_time,
                    "end_time": result.end_time,
                    "speaker": result.speaker,
                    "confidence": result.confidence,
                    "is_final": True
                }
            })
            logger.info(
                f"[Session {self.session_id}] Interim transcript: "
                f"{result.text[:50]}..."
            )
        except Exception as e:
            logger.warning(
                f"[Session {self.session_id}] Failed to send transcript: {e}"
            )
            self._closed = True

    async def send_all_transcripts(
        self,
        sender: Callable[[dict], Awaitable[None]]
    ) -> None:
        """发送所有转写结果（stop 后调用）"""
        for seg in self.transcripts:
            if self._closed:
                break
            try:
                await sender({
                    "type": "transcript",
                    "seq": self.seq,
                    "data": {
                        "text": seg.text,
                        "start_time": seg.start_time,
                        "end_time": seg.end_time,
                        "speaker": seg.speaker,
                        "confidence": seg.confidence,
                        "is_final": True
                    }
                })
            except Exception as e:
                logger.warning(
                    f"[Session {self.session_id}] Failed to send transcript: {e}"
                )
                self._closed = True
                break

    def clear(self) -> None:
        """清空转写记录"""
        self.transcripts.clear()
        self.seq = 0


class SessionStateManager:
    """会话状态管理器"""

    def __init__(self, session_id: str, started_at: datetime):
        self.session_id = session_id
        self.started_at = started_at
        self._session_store = get_session_store_sync()
        self._restore_completed = False

    def create(self) -> None:
        """创建新会话"""
        self._session_store.create_session(self.session_id)

    def restore(self) -> bool:
        """恢复会话状态"""
        state = self._session_store.get_session(self.session_id)
        if state:
            logger.info(
                f"[Session {self.session_id}] Restored state: "
                f"{len(state.get_transcripts())} transcripts, seq={state.seq}"
            )
            return True

        logger.warning(
            f"[Session {self.session_id}] Session not found in store"
        )
        return False

    async def save(
        self,
        status: SessionStatus,
        transcripts: list[ASRResult],
        audio_chunks_count: int,
        seq: int
    ) -> None:
        """保存会话状态"""
        try:
            transcripts_to_save = [
                TranscriptRecord(
                    text=t.text,
                    start_time=t.start_time,
                    end_time=t.end_time,
                    speaker=t.speaker,
                    confidence=t.confidence,
                    is_final=t.is_final
                )
                for t in transcripts
            ]

            self._session_store.update_session(
                self.session_id,
                status=status,
                transcripts=transcripts_to_save,
                audio_chunks_count=audio_chunks_count,
                seq=seq
            )
        except Exception as e:
            logger.warning(
                f"[Session {self.session_id}] Failed to save state: {e}"
            )

    def get_transcripts_for_restore(self) -> list[ASRResult]:
        """获取用于恢复的转写记录"""
        state = self._session_store.get_session(self.session_id)
        if not state:
            return []

        return [
            ASRResult(
                text=t.text,
                start_time=t.start_time,
                end_time=t.end_time,
                speaker=t.speaker,
                confidence=t.confidence,
                is_final=t.is_final
            )
            for t in state.get_transcripts()
        ]

    def get_seq_for_restore(self) -> int:
        """获取用于恢复的 seq"""
        state = self._session_store.get_session(self.session_id)
        return state.seq if state else 0


class MeetingAnalyzer:
    """会议分析器"""

    def __init__(
        self,
        session_id: str,
        started_at: datetime,
        llm_analyzer: LLMAnalyzer,
        transcripts_holder: list[ASRResult]
    ):
        self.session_id = session_id
        self.started_at = started_at
        self.llm_analyzer = llm_analyzer
        self._transcripts = transcripts_holder

    def _format_speaker(self, speaker: str) -> str:
        """将说话人 ID 转换为可读标签"""
        if not speaker or speaker == "unknown":
            return "发言人"
        if speaker.startswith("speaker_"):
            try:
                idx = int(speaker.split("_")[1])
                label = chr(ord('A') + idx)
                return f"发言人 {label}"
            except (IndexError, ValueError):
                return "发言人"
        return speaker

    def _format_timestamp(self, seconds: float) -> str:
        """将秒数格式化为 HH:MM:SS"""
        if seconds <= 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    async def analyze(self, audio_path: Optional[Path]) -> AnalysisResult:
        """分析会议内容"""
        try:
            result = await self.llm_analyzer.analyze_meeting(
                audio_path,
                self._transcripts
            )
            return result
        except Exception as e:
            logger.error(f"[Session {self.session_id}] LLM analysis error: {e}")
            return AnalysisResult(
                summary="会议分析暂时不可用。",
                key_points=[],
                action_items=[],
                topics=[]
            )

    async def save_transcript_text(
        self,
        analysis_result: Optional[AnalysisResult]
    ) -> None:
        """保存转写文本到文件"""
        if not self._transcripts:
            logger.warning(
                f"[Session {self.session_id}] No transcripts to save"
            )
            return

        try:
            total_duration = max(t.end_time for t in self._transcripts) if self._transcripts else 0

            lines = []
            lines.append(f"# 会议转写文本")
            lines.append(f"# Session ID: {self.session_id}")
            lines.append(f"# 开始时间: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append(f"# 总时长: {self._format_timestamp(total_duration)}")
            lines.append(f"# 转写片段数: {len(self._transcripts)}")
            lines.append("")
            lines.append("=" * 60)
            lines.append("")

            for transcript in self._transcripts:
                speaker_label = self._format_speaker(transcript.speaker)
                start = self._format_timestamp(transcript.start_time)
                end = self._format_timestamp(transcript.end_time)
                lines.append(f"[{start} - {end}] {speaker_label}:")
                lines.append(f"  {transcript.text}")
                lines.append("")

            if analysis_result:
                lines.append("=" * 60)
                lines.append("")
                lines.append("# LLM 分析结果")
                lines.append("")

                if analysis_result.summary:
                    lines.append(f"## 摘要")
                    lines.append(f"{analysis_result.summary}")
                    lines.append("")

                if analysis_result.key_points:
                    lines.append(f"## 关键点")
                    for point in analysis_result.key_points:
                        lines.append(f"- {point}")
                    lines.append("")

                if analysis_result.action_items:
                    lines.append(f"## 行动项")
                    for item in analysis_result.action_items:
                        lines.append(f"- [ ] {item}")
                    lines.append("")

                if analysis_result.topics:
                    lines.append(f"## 主题标签")
                    lines.append(f"、".join(f"`{t}`" for t in analysis_result.topics))
                    lines.append("")

            transcript_text = "\n".join(lines)

            transcript_path = config.transcripts_dir / f"{self.session_id}_transcript.txt"
            transcript_path.write_text(transcript_text, encoding='utf-8')
            logger.info(
                f"[Session {self.session_id}] Transcript saved to: {transcript_path}"
            )

        except Exception as e:
            logger.error(
                f"[Session {self.session_id}] Failed to save transcript: {e}"
            )


class GraphRAGNotifier:
    """GraphRAG 事件通知器"""

    def __init__(
        self,
        session_id: str,
        started_at: datetime,
        transcripts_holder: list[ASRResult]
    ):
        self.session_id = session_id
        self.started_at = started_at
        self._transcripts = transcripts_holder

    def _format_speaker(self, speaker: str) -> str:
        """将说话人 ID 转换为可读标签"""
        if not speaker or speaker == "unknown":
            return "发言人"
        if speaker.startswith("speaker_"):
            try:
                idx = int(speaker.split("_")[1])
                label = chr(ord('A') + idx)
                return f"发言人 {label}"
            except (IndexError, ValueError):
                return "发言人"
        return speaker

    def _format_timestamp(self, seconds: float) -> str:
        """将秒数格式化为 HH:MM:SS"""
        if seconds <= 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def _build_index_document(self, analysis_result: AnalysisResult) -> str:
        """构建 GraphRAG 索引文档内容"""
        if not self._transcripts:
            return ""

        lines = []
        lines.append(f"# 会议记录 - Session: {self.session_id}")
        lines.append(f"# 时间: {self.started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        if analysis_result.summary:
            lines.append("## 摘要")
            lines.append(analysis_result.summary)
            lines.append("")

        if analysis_result.key_points:
            lines.append("## 关键点")
            for point in analysis_result.key_points:
                lines.append(f"- {point}")
            lines.append("")

        if analysis_result.action_items:
            lines.append("## 行动项")
            for item in analysis_result.action_items:
                lines.append(f"- [ ] {item}")
            lines.append("")

        if analysis_result.topics:
            lines.append(f"## 主题: {', '.join(analysis_result.topics)}")
            lines.append("")

        lines.append("## 转写记录")
        for t in self._transcripts:
            speaker = self._format_speaker(t.speaker)
            lines.append(
                f"[{self._format_timestamp(t.start_time)}] {speaker}: {t.text}"
            )

        return "\n".join(lines)

    async def notify(self, analysis_result: AnalysisResult) -> None:
        """触发 GraphRAG 索引"""
        try:
            doc_content = self._build_index_document(analysis_result)
            if not doc_content:
                logger.warning(
                    f"[Session {self.session_id}] No content to index for GraphRAG"
                )
                return

            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                prefix=f'meeting_{self.session_id}_',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(doc_content)
                temp_path = f.name

            logger.info(
                f"[Session {self.session_id}] Triggering GraphRAG index for: {temp_path}"
            )

            graphrag_index_timeout = config.timeout.graphrag_index_timeout if hasattr(config, 'timeout') else 300.0
            async with httpx.AsyncClient(timeout=graphrag_index_timeout) as client:
                with open(temp_path, 'rb') as f:
                    files = {
                        'doc': (f'{self.session_id}_meeting.txt', f, 'text/plain')
                    }
                    try:
                        response = await client.post(
                            f"{config.graphrag.service_url}/api/v1/index/",
                            files=files
                        )
                        if response.status_code == 200:
                            result = response.json()
                            logger.info(
                                f"[Session {self.session_id}] GraphRAG index completed: "
                                f"entities={result.get('entities_count', 0)}, "
                                f"relationships={result.get('relationships_count', 0)}"
                            )
                        else:
                            logger.warning(
                                f"[Session {self.session_id}] GraphRAG index failed: "
                                f"status={response.status_code}, body={response.text}"
                            )
                    except httpx.TimeoutException:
                        logger.warning(
                            f"[Session {self.session_id}] GraphRAG index timeout"
                        )
                    except httpx.HTTPError as e:
                        logger.error(
                            f"[Session {self.session_id}] GraphRAG index HTTP error: {e}"
                        )

            try:
                Path(temp_path).unlink()
            except Exception:
                pass

        except Exception as e:
            logger.error(f"[Session {self.session_id}] GraphRAG index error: {e}")