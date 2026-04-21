"""
文件上传路由

支持音频/视频文件上传并转写
"""

import asyncio
import uuid
import tempfile
import os
import json
import atexit
import time
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.core.asr import ASRFactory
from app.core.audio_cache import AudioCache
from app.core.llm_analyzer import LLMAnalyzer, AnalysisResult
from app.core.audio_analyzer import AudioAnalyzer, TranscriptSegment
from app.core.processing_status import get_processing_status_manager, ProcessingStage, ProcessingInfo
from app.config import config
from app.utils.logger import setup_logger
from app.api.v1.auth import verify_api_key

logger = setup_logger("upload.process")
upload_logger = logger  # Alias for clarity in this module

router = APIRouter()

# 跟踪所有上传的临时文件，用于清理
_upload_temp_files: set = set()
_max_temp_age_seconds = 3600  # 1小时后清理

# 并发上传限制
_upload_semaphore = asyncio.Semaphore(3)


def _cleanup_upload_temp_files():
    """清理所有上传临时文件（由 atexit 调用）"""
    import time
    cleaned = 0
    for temp_path in list(_upload_temp_files):
        try:
            if temp_path.exists():
                # 只清理超过 max_age 的文件
                file_age = time.time() - temp_path.stat().st_mtime
                if file_age > _max_temp_age_seconds:
                    temp_path.unlink()
                    cleaned += 1
                    logger.info(f"[Upload cleanup] Removed old temp file: {temp_path}")
        except Exception as e:
            logger.warning(f"[Upload cleanup] Failed to remove {temp_path}: {e}")
        finally:
            _upload_temp_files.discard(temp_path)
    if cleaned > 0:
        logger.info(f"[Upload cleanup] Cleaned {cleaned} temp files")


# 注册进程退出时的清理
atexit.register(_cleanup_upload_temp_files)


def _format_speaker(speaker: str) -> str:
    """将说话人 ID 转换为可读标签"""
    if not speaker or speaker == "unknown":
        return "发言人"
    if speaker.startswith("speaker_"):
        try:
            idx = int(speaker.split("_")[1])
            return f"发言人 {chr(ord('A') + idx)}"
        except (IndexError, ValueError):
            return "发言人"
    return speaker


def _format_timestamp(seconds: float) -> str:
    """将秒数格式化为 HH:MM:SS"""
    if seconds <= 0:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def _recalculate_chapter_timestamps(chapters: List[Dict[str, Any]], segments: List) -> List[Dict[str, Any]]:
    """
    根据实际 ASR segment 时间戳重新计算章节的 start_time 和 end_time

    LLM 生成的章节时间可能不准确（如 hallucinate 导致 end_time < start_time
    或 end_time 超过实际音频时长）。此函数通过 speaker_summary.source_timestamps
    重新计算每个章节的起止时间。

    策略：
    - 遍历所有 speaker_summary 的 source_timestamps
    - 取所有 speaker 的最早 start 和最晚 end 作为章节边界
    - 确保 end_time 不超过音频实际时长
    """
    if not chapters or not segments:
        logger.warning("[ChapterTimestamp] Empty chapters or segments, returning as-is")
        return chapters

    # 计算实际音频时长（基于最后一个 segment 的 end_time）
    # segments 可能是 TranscriptSegmentResponse 或 TranscriptSegment 对象
    try:
        audio_duration = segments[-1].end_time if segments else 0.0
        logger.info(f"[ChapterTimestamp] audio_duration from last segment: {audio_duration:.1f}s, segments count: {len(segments)}")
    except (AttributeError, IndexError):
        audio_duration = 0.0
        logger.warning("[ChapterTimestamp] Could not get audio_duration from segments")

    # 辅助函数：从 source_timestamps 获取起止时间（处理 dict 和对象）
    def _get_bounds(stamps) -> tuple:
        if not stamps:
            return (0.0, 0.0)
        starts, ends = [], []
        for ts in stamps:
            if isinstance(ts, dict):
                starts.append(ts.get("开始", ts.get("start", 0)))
                ends.append(ts.get("结束", ts.get("end", 0)))
            elif hasattr(ts, 'start') and hasattr(ts, 'end'):
                starts.append(ts.start)
                ends.append(ts.end)
        return (min(starts) if starts else 0.0, max(ends) if ends else 0.0)

    corrected = []
    for chapter in chapters:
        original_start = chapter.get("start_time", 0)
        original_end = chapter.get("end_time", 0)
        logger.info(f"[ChapterTimestamp] Chapter '{chapter.get('title', 'N/A')}': original start={original_start}, end={original_end}")

        # 从 speaker_summaries 获取时间范围
        speaker_summaries = chapter.get("speaker_summaries", [])
        all_starts = []
        all_ends = []

        for ss in speaker_summaries:
            source_ts = ss.get("source_timestamps", [])
            s, e = _get_bounds(source_ts)
            logger.info(f"[ChapterTimestamp]   Speaker '{ss.get('speaker', 'N/A')}': source_timestamps={source_ts}, bounds=({s:.1f}, {e:.1f})")
            if s > 0 or e > 0:
                all_starts.append(s)
                all_ends.append(e)

        if all_starts and all_ends:
            new_start = min(all_starts)
            new_end = min(max(all_ends), audio_duration if audio_duration > 0 else max(all_ends))
            logger.info(f"[ChapterTimestamp]   Recalculated from timestamps: start={new_start:.1f}, end={new_end:.1f}")
        else:
            # 无法从 speaker_summaries 计算，保持原值（后续保护）
            new_start = original_start
            new_end = original_end
            logger.warning(f"[ChapterTimestamp]   No valid timestamps, keeping original: start={new_start}, end={new_end}")
            # 保护：end 不超过 audio_duration
            if audio_duration > 0 and new_end > audio_duration:
                new_end = audio_duration
                logger.info(f"[ChapterTimestamp]   Capped end to audio_duration: {new_end:.1f}")
            # 保护：start 不超过 end
            if new_start > new_end:
                new_start = max(0, new_end - 60.0)  # fallback: 至少给 60 秒时长
                logger.warning(f"[ChapterTimestamp]   Fixed start > end, new_start={new_start:.1f}")

        corrected.append({
            **chapter,
            "start_time": new_start,
            "end_time": new_end,
        })

    logger.info(
        f"[ChapterTimestamp] Recalculated {len(corrected)} chapters, "
        f"audio_duration={audio_duration:.1f}s"
    )
    for i, ch in enumerate(corrected):
        logger.info(f"[ChapterTimestamp]   Final chapter[{i}] '{ch.get('title', 'N/A')}': start={ch.get('start_time', 0):.1f}, end={ch.get('end_time', 0):.1f}")
    return corrected


def _save_intermediate_result(session_id: str, stage: str, data: Dict[str, Any]) -> None:
    """保存中间结果到 workspace/output/{session_id}/{stage}.json"""
    try:
        session_dir = config.workspace_output_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        file_path = session_dir / f"{stage}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"[Upload {session_id}] Saved {stage} to {file_path}")
    except Exception as e:
        logger.warning(f"[Upload {session_id}] Failed to save {stage}: {e}")


async def _save_upload_transcript(session_id: str, transcript_results: List, analysis_result=None) -> None:
    """保存上传文件的转写文本到文件"""
    if not transcript_results:
        logger.warning(f"[Upload {session_id}] No transcripts to save")
        return

    try:
        started_at = datetime.now()
        total_duration = max(r.end_time for r in transcript_results) if transcript_results else 0

        # 构建文本内容
        lines = []
        lines.append(f"# 会议转写文本")
        lines.append(f"# Session ID: {session_id}")
        lines.append(f"# 开始时间: {started_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"# 总时长: {_format_timestamp(total_duration)}")
        lines.append(f"# 转写片段数: {len(transcript_results)}")
        lines.append(f"# 来源: 文件上传")
        lines.append("")
        lines.append("=" * 60)
        lines.append("")

        for i, result in enumerate(transcript_results, 1):
            speaker_label = _format_speaker(result.speaker)
            start = _format_timestamp(result.start_time)
            end = _format_timestamp(result.end_time)
            lines.append(f"[{start} - {end}] {speaker_label}:")
            lines.append(f"  {result.text}")
            lines.append("")

        # 添加 LLM 分析结果
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

        # 保存到文件
        transcript_path = config.transcripts_dir / f"{session_id}_transcript.txt"
        transcript_path.write_text(transcript_text, encoding='utf-8')
        logger.info(f"[Upload {session_id}] Transcript saved to: {transcript_path}")

    except Exception as e:
        logger.error(f"[Upload {session_id}] Failed to save transcript: {e}")


class TranscriptSegmentResponse(BaseModel):
    """转写片段"""
    text: str
    speaker: str
    start_time: float
    end_time: float


class UploadResponse(BaseModel):
    """上传响应"""
    success: bool
    session_id: str
    message: str
    transcript: Optional[str] = None
    segments: Optional[List[TranscriptSegmentResponse]] = None  # 结构化转写片段
    # 统一格式字段
    chapters: Optional[List[Dict[str, Any]]] = None
    theme: Optional[str] = None
    topics: Optional[List[str]] = None
    speaker_roles: Optional[List[Dict[str, str]]] = None
    # 兼容字段
    analysis: Optional[dict] = None
    # 音频 URL（用于前端播放）
    audio_url: Optional[str] = None


class UploadAcceptedResponse(BaseModel):
    """上传接受响应（异步模式）"""
    session_id: str
    message: str
    status: str = "processing"


async def _process_upload_file(
    session_id: str,
    temp_file: Path,
    ext: str,
    file_size: int,
    language: Optional[str],
    prompt: Optional[str],
    request: Optional[Request],
):
    """
    后台任务：处理上传文件

    实际执行 ASR → GraphRAG → LLM → AudioAnalyzer 的完整处理流程
    通过 status_manager.update() 推送中间状态到 SSE 端点
    """
    upload_start_time = time.time()
    logger.info(f"[Upload {session_id}] ========== Background Processing Started ==========")
    status_manager = get_processing_status_manager()
    logger.info(f"[Upload {session_id}] status_manager obtained")

    asr_adapter = None
    try:
        # 更新状态：开始转写
        logger.info(f"[Upload {session_id}] Calling status_manager.update: stage=TRANSCRIBING, progress=10")
        status_manager.update(
            session_id,
            stage=ProcessingStage.TRANSCRIBING,
            progress=10,
            message=f"文件已保存({file_size / (1024*1024):.1f}MB)，开始语音识别..."
        )
        logger.info(f"[Upload {session_id}] status_manager.update completed, stage=TRANSCRIBING")
        logger.info(f"[Upload {session_id}] ========== ASR Processing Starting ==========")

        # 初始化 ASR
        asr_engine = config.asr.engine
        if asr_engine == "funasr_realtime":
            asr_engine = "funasr"
        asr_adapter = ASRFactory.create(asr_engine)
        await asr_adapter.initialize()

        # 读取并转写音频
        asr_start_time = time.time()
        logger.info(f"[Upload {session_id}] Starting transcription...")

        transcript_results: List = []
        speakers: set = set()
        total_duration = 0.0

        # 异步迭代 ASR 结果
        async for result in asr_adapter.recognize_file(temp_file):
            transcript_results.append(result)
            if result.speaker:
                speakers.add(result.speaker)
            if result.end_time > total_duration:
                total_duration = result.end_time

            # 计算预估剩余时间
            elapsed = (datetime.now() - status_manager.get(session_id).started_at).total_seconds() if status_manager.get(session_id) else 1
            processed_count = len(transcript_results)
            if processed_count > 0 and total_duration > 0:
                denominator = min(0.4, 0.1 + processed_count * 0.02)
                if denominator > 0 and elapsed > 0:
                    estimated_total = elapsed / denominator
                    remaining = max(0, int(estimated_total - elapsed))
                else:
                    remaining = None
            else:
                remaining = None

            # 更新进度：转写中 (10-40%)
            status_manager.update(
                session_id,
                progress=min(40, 10 + len(transcript_results) * 2),
                message=f"正在识别语音... 已识别 {len(transcript_results)} 段",
                remaining_time_seconds=remaining,
                speaker_count=len(speakers),
                segment_count=len(transcript_results),
            )
            logger.info(f"[Upload {session_id}] Transcribed: {result.text[:50]}...")

        await asr_adapter.close()
        asr_adapter = None  # 标记已关闭

        asr_elapsed = time.time() - asr_start_time
        logger.info(f"[Upload {session_id}] ========== ASR Completed in {asr_elapsed:.2f}s ==========")
        logger.info(f"[Upload {session_id}] ASR results: {len(transcript_results)} segments, {len(speakers)} speakers, total_duration={total_duration:.1f}s")

        # 更新状态：转写完成，开始分析
        status_manager.update(
            session_id,
            stage=ProcessingStage.ANALYZING,
            progress=50,
            message=f"语音识别完成，共 {len(transcript_results)} 段，开始深度分析...",
            speaker_count=len(speakers),
            segment_count=len(transcript_results),
        )

        # 构建转写文本和片段
        transcript_text = " ".join(r.text for r in transcript_results)
        segments = [
            TranscriptSegmentResponse(
                text=r.text,
                speaker=r.speaker or "unknown",
                start_time=r.start_time,
                end_time=r.end_time
            )
            for r in transcript_results
        ]

        # 保存转写中间结果
        _save_intermediate_result(session_id, "transcript", {
            "stage": "transcription",
            "segment_count": len(transcript_results),
            "speaker_count": len(speakers),
            "total_duration": total_duration,
            "segments": [
                {
                    "text": r.text,
                    "speaker": r.speaker or "unknown",
                    "start_time": r.start_time,
                    "end_time": r.end_time
                }
                for r in transcript_results
            ]
        })

        # 分析流程
        analysis_result = None
        audio_analysis_result = None
        graphrag_context = None

        if transcript_text:
            # Step 1: GraphRAG 实体识别
            graphrag_start_time = time.time()
            logger.info(f"[Upload {session_id}] ========== GraphRAG Processing Starting ==========")
            try:
                status_manager.update(
                    session_id,
                    progress=52,
                    message="正在进行实体识别和关系抽取..."
                )
                import httpx
                graphrag_service_url = config.graphrag.service_url
                graphrag_timeout = config.timeout.graphrag_timeout if hasattr(config, 'timeout') else 30.0
                async with httpx.AsyncClient(timeout=graphrag_timeout) as client:
                    try:
                        logger.info(f"[Upload {session_id}] Calling GraphRAG extract API: {graphrag_service_url}/api/v1/extract/")
                        graphrag_response = await client.post(
                            f"{graphrag_service_url}/api/v1/extract/",
                            json={
                                "text": transcript_text,
                                "session_id": session_id,
                                "namespace": "meetings"
                            }
                        )
                        if graphrag_response.status_code == 200:
                            graphrag_data = graphrag_response.json()
                            graphrag_context = graphrag_data
                            entity_count = len(graphrag_data.get('entities', []))
                            logger.info(f"[Upload {session_id}] GraphRAG extracted {entity_count} entities")
                    except httpx.TimeoutException:
                        logger.warning(f"[Upload {session_id}] GraphRAG entity extraction timeout")
                        graphrag_context = None
            except Exception as e:
                logger.warning(f"[Upload {session_id}] GraphRAG entity extraction failed: {e}")
                graphrag_context = None
            finally:
                graphrag_elapsed = time.time() - graphrag_start_time
                logger.info(f"[Upload {session_id}] ========== GraphRAG Completed in {graphrag_elapsed:.2f}s ==========")

            # Step 2: LLM 分析
            llm_start_time = time.time()
            logger.info(f"[Upload {session_id}] ========== LLM Analysis Starting ==========")
            try:
                status_manager.update(
                    session_id,
                    progress=55,
                    message="正在进行内容摘要分析..."
                )
                llm_analyzer = LLMAnalyzer(
                    provider=config.llm.provider,
                    api_key=config.llm.dashscope_api_key,
                    endpoint=config.llm.dashscope_endpoint,
                    model=config.llm.dashscope_model
                )
                try:
                    logger.info(f"[Upload {session_id}] Calling LLMAnalyzer.analyze_text_with_graphrag_context()")
                    analysis_result = await llm_analyzer.analyze_text_with_graphrag_context(
                        transcript_text, graphrag_context
                    )
                    logger.info(f"[Upload {session_id}] LLM analysis completed: theme={analysis_result.theme[:50] if analysis_result and analysis_result.theme else 'N/A'}")
                except Exception as e:
                    error_msg = str(e)
                    if "timeout" in error_msg.lower():
                        logger.warning(f"[Upload {session_id}] LLM analysis timeout")
                        analysis_result = None
                    else:
                        raise
                finally:
                    await llm_analyzer.close()
                    llm_elapsed = time.time() - llm_start_time
                    logger.info(f"[Upload {session_id}] ========== LLM Analysis Completed in {llm_elapsed:.2f}s ==========")
            except Exception as e:
                logger.warning(f"[Upload {session_id}] LLM analysis failed: {e}")
                analysis_result = None

            # Step 3: AudioAnalyzer 深度分析
            audio_analyzer_start_time = time.time()
            logger.info(f"[Upload {session_id}] ========== AudioAnalyzer (Deep Analysis) Starting ==========")
            try:
                status_manager.update(
                    session_id,
                    progress=65,
                    message="正在进行深度语义分析..."
                )
                audio_analyzer = AudioAnalyzer()
                segs = [
                    TranscriptSegment(
                        text=r.text,
                        speaker=r.speaker or "unknown",
                        start_time=r.start_time,
                        end_time=r.end_time
                    )
                    for r in transcript_results
                ]
                audio_analysis_result = audio_analyzer.analyze_segments(segs)
                audio_analyzer_elapsed = time.time() - audio_analyzer_start_time
                logger.info(f"[Upload {session_id}] AudioAnalyzer completed in {audio_analyzer_elapsed:.2f}s")

                status_manager.update(
                    session_id,
                    progress=90,
                    message="分析完成，正在整理结果..."
                )
            except Exception as e:
                audio_analyzer_elapsed = time.time() - audio_analyzer_start_time
                logger.warning(f"[Upload {session_id}] AudioAnalyzer failed after {audio_analyzer_elapsed:.2f}s: {e}")

        # 保存转写文本到文件
        await _save_upload_transcript(session_id, transcript_results, analysis_result)

        # 优先使用 audio_analysis_result
        primary_result = audio_analysis_result or analysis_result

        def to_dict_list(items, to_dict_attr='to_dict'):
            result = []
            for item in items:
                if hasattr(item, to_dict_attr):
                    result.append(getattr(item, to_dict_attr)())
                elif isinstance(item, dict):
                    result.append(item)
            return result

        chapters_dict = to_dict_list(primary_result.chapters) if primary_result else []
        speaker_roles_dict = to_dict_list(primary_result.speaker_roles) if primary_result else []

        # 重新计算章节时间戳
        if chapters_dict and segments:
            logger.info(f"[Upload {session_id}] Recalculating chapter timestamps...")
            chapters_dict = _recalculate_chapter_timestamps(chapters_dict, segments)

        # 保存分析中间结果
        if primary_result:
            _save_intermediate_result(session_id, "analysis", {
                "stage": "analysis",
                "theme": primary_result.theme,
                "summary": primary_result.summary,
                "chapters": chapters_dict,
                "speaker_roles": speaker_roles_dict,
                "topics": primary_result.topics,
                "key_points": primary_result.key_points,
                "action_items": primary_result.action_items,
            })

        # 构建音频 URL
        if request:
            scheme = request.headers.get("x-forwarded-proto", "http")
            host = request.headers.get("host", "localhost:8000")
            audio_url = f"{scheme}://{host}/api/v1/upload/{session_id}/audio"
        else:
            audio_url = f"/api/v1/upload/{session_id}/audio"

        # 保存最终结果
        _save_intermediate_result(session_id, "result", {
            "session_id": session_id,
            "transcript": transcript_text,
            "segments": [s.model_dump() for s in segments],
            "chapters": chapters_dict,
            "theme": primary_result.theme if primary_result else None,
            "topics": primary_result.topics if primary_result else [],
            "speaker_roles": speaker_roles_dict,
            "summary": primary_result.summary if primary_result else None,
            "key_points": primary_result.key_points if primary_result else [],
            "action_items": primary_result.action_items if primary_result else [],
            "audio_url": audio_url,
        })

        # 标记处理完成
        status_manager.complete(session_id, "文件处理完成")
        total_elapsed = time.time() - upload_start_time
        logger.info(f"[Upload {session_id}] ========== Background Processing Completed in {total_elapsed:.2f}s ==========")
        logger.info(f"[Upload {session_id}] Summary: segments={len(transcript_results)}, speakers={len(speakers)}, chapters={len(chapters_dict)}")

    except Exception as e:
        total_elapsed = time.time() - upload_start_time
        logger.error(f"[Upload {session_id}] Background processing error after {total_elapsed:.2f}s: {e}")
        import traceback
        logger.error(f"[Upload {session_id}] Traceback: {traceback.format_exc()}")
        status_manager.error(session_id, str(e))

    finally:
        # 确保 ASR 适配器被关闭
        if asr_adapter is not None:
            try:
                await asr_adapter.close()
            except Exception:
                pass
        logger.info(f"[Upload {session_id}] Background task finished")


@router.post("/upload", response_model=UploadAcceptedResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    _auth: str = Depends(verify_api_key)
):
    """
    上传音频/视频文件进行转写（异步模式）

    支持格式: mp3, mp4, wav, m4a, ogg, flac, webm
    注意: 文件大小限制 512MB

    立即返回 session_id，实际处理在后台进行
    通过 GET /upload/{session_id}/status SSE 端点订阅处理进度

    Args:
        file: 上传的文件
        language: 可选语言代码 (如 "zh", "en")
        prompt: 可选提示词，帮助识别

    Returns:
        UploadAcceptedResponse: 包含 session_id，用于订阅状态
    """
    session_id = f"upload_{uuid.uuid4().hex[:8]}"
    upload_start_time = time.time()
    logger.info(f"[Upload] ========== Upload started for session {session_id} ==========")
    logger.info(f"[Upload {session_id}] File received: filename={file.filename}, content_type={file.content_type}")

    # 初始化处理状态管理器
    status_manager = get_processing_status_manager()
    status_manager.start(session_id)

    # 检查文件类型
    allowed_types = {
        'audio/mpeg': 'mp3',
        'audio/mp3': 'mp3',
        'audio/mp4': 'mp4',
        'audio/wav': 'wav',
        'audio/x-wav': 'wav',
        'audio/m4a': 'm4a',
        'audio/x-m4a': 'm4a',
        'audio/ogg': 'ogg',
        'audio/flac': 'flac',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'application/octet-stream': None,
    }

    content_type = file.content_type
    ext = allowed_types.get(content_type)

    if ext is None and content_type == 'application/octet-stream':
        filename = file.filename or ''
        for allowed_ext in ['mp3', 'mp4', 'wav', 'm4a', 'ogg', 'flac', 'webm']:
            if filename.lower().endswith(f'.{allowed_ext}'):
                ext = allowed_ext
                break

    if ext is None:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {content_type}. 支持: mp3, mp4, wav, m4a, ogg, flac, webm"
        )

    # 创建临时文件
    temp_dir = Path(tempfile.gettempdir()) / "voice_upload"
    temp_dir.mkdir(exist_ok=True)
    temp_file = temp_dir / f"{session_id}.{ext}"

    try:
        # 保存上传的文件（流式写入，避免大文件 OOM）
        logger.info(f"[Upload {session_id}] Saving file: {temp_file}")
        max_size = 512 * 1024 * 1024  # 512MB
        file_size = 0

        with open(temp_file, 'wb') as f:
            initial_chunk = await file.read(1024 * 1024)  # 1MB 头
            if len(initial_chunk) > max_size:
                f.close()
                os.remove(temp_file)
                raise HTTPException(
                    status_code=400,
                    detail=f"文件太大: {len(initial_chunk) / (1024*1024):.1f}MB。最大支持 512MB。"
                )
            f.write(initial_chunk)
            file_size = len(initial_chunk)

            while True:
                chunk = await file.read(64 * 1024 * 1024)  # 每次 64MB
                if not chunk:
                    break
                if file_size + len(chunk) > max_size:
                    f.close()
                    os.remove(temp_file)
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件太大: {(file_size + len(chunk)) / (1024*1024):.1f}MB。最大支持 512MB。"
                    )
                f.write(chunk)
                file_size += len(chunk)

        logger.info(f"[Upload {session_id}] File saved: {file_size} bytes in {time.time() - upload_start_time:.2f}s")

        # 注册临时文件到清理队列
        _upload_temp_files.add(temp_file)

        # 启动后台任务（受 semaphore 限制并发数）
        asyncio.create_task(_process_upload_file(
            session_id=session_id,
            temp_file=temp_file,
            ext=ext,
            file_size=file_size,
            language=language,
            prompt=prompt,
            request=None,  # 后台任务不需要 request
        ))

        # 立即返回 202 Accepted
        return UploadAcceptedResponse(
            session_id=session_id,
            message="文件上传成功，正在后台处理中",
            status="processing"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[Upload {session_id}] Upload error: {e}")
        if temp_file.exists():
            os.remove(temp_file)
        raise HTTPException(status_code=500, detail="文件上传失败，请稍后重试。")


@router.delete("/upload/{session_id}")
async def delete_upload_session(session_id: str, _auth: str = Depends(verify_api_key)):
    """
    删除上传会话的临时文件和会话数据

    Args:
        session_id: 上传会话 ID (格式: upload_{8_hex_chars})

    Returns:
        删除结果
    """
    import re
    if not re.match(r'^upload_[0-9a-f]{8}$', session_id):
        logger.warning(f"[Delete] Invalid session_id format: {session_id}")
        raise HTTPException(status_code=400, detail="无效的会话 ID")

    deleted_files = []
    errors = []

    # 删除临时音频文件
    temp_dir = (Path(tempfile.gettempdir()) / "voice_upload").resolve()
    for ext in ['mp3', 'mp4', 'wav', 'm4a', 'ogg', 'flac', 'webm']:
        f = temp_dir / f"{session_id}.{ext}"
        try:
            resolved = f.resolve()
            if str(resolved).startswith(str(temp_dir)) and resolved.exists():
                resolved.unlink()
                _upload_temp_files.discard(resolved)
                deleted_files.append(str(f.name))
                logger.info(f"[Delete {session_id}] Removed temp file: {resolved}")
        except Exception as e:
            errors.append(f"temp file {ext}: {e}")

    # 删除中间结果目录
    try:
        session_dir = config.workspace_output_dir / session_id
        if session_dir.exists():
            import shutil
            shutil.rmtree(session_dir)
            deleted_files.append(f"output/{session_id}/")
            logger.info(f"[Delete {session_id}] Removed output dir: {session_dir}")
    except Exception as e:
        errors.append(f"output dir: {e}")

    # 删除转写文本文件
    try:
        transcript_path = config.transcripts_dir / f"{session_id}_transcript.txt"
        if transcript_path.exists():
            transcript_path.unlink()
            deleted_files.append(f"{session_id}_transcript.txt")
            logger.info(f"[Delete {session_id}] Removed transcript: {transcript_path}")
    except Exception as e:
        errors.append(f"transcript: {e}")

    # 清理处理状态
    try:
        status_manager = get_processing_status_manager()
        status_manager.remove(session_id)
    except Exception:
        pass

    if not deleted_files and not errors:
        raise HTTPException(status_code=404, detail="会话不存在或已清理")

    return {
        "success": True,
        "session_id": session_id,
        "deleted": deleted_files,
        "errors": errors if errors else None,
    }


@router.get("/upload/formats")
async def get_supported_formats():
    """获取支持的文件格式"""
    return {
        "formats": [
            {"extension": "mp3", "mime_type": "audio/mpeg", "description": "MP3 音频"},
            {"extension": "mp4", "mime_type": "audio/mp4", "description": "MP4 音频/视频"},
            {"extension": "wav", "mime_type": "audio/wav", "description": "WAV 音频"},
            {"extension": "m4a", "mime_type": "audio/m4a", "description": "M4A 音频"},
            {"extension": "ogg", "mime_type": "audio/ogg", "description": "OGG 音频"},
            {"extension": "flac", "mime_type": "audio/flac", "description": "FLAC 无损音频"},
            {"extension": "webm", "mime_type": "video/webm", "description": "WebM 视频"},
        ],
        "max_file_size_mb": 100
    }


@router.get("/upload/{session_id}/audio")
async def get_uploaded_audio(session_id: str, _auth: str = Depends(verify_api_key)):
    """
    获取上传的音频文件（用于前端播放）

    Args:
        session_id: 上传会话 ID

    Returns:
        Audio file stream
    """
    # 安全验证: session_id 格式为 upload_{8_hex_chars}，防止路径遍历
    import re
    if not re.match(r'^upload_[0-9a-f]{8}$', session_id):
        logger.warning(f"[Audio] Invalid session_id format: {session_id}")
        raise HTTPException(status_code=400, detail="无效的会话 ID")


@router.get("/upload/{session_id}")
async def get_upload_session(session_id: str, _auth: str = Depends(verify_api_key)):
    """
    获取上传会话的完整数据（用于恢复会话或获取完整分析结果）

    Args:
        session_id: 上传会话 ID

    Returns:
        Session data including segments, chapters, analysis, etc.
    """
    import re
    if not re.match(r'^upload_[0-9a-f]{8}$', session_id):
        logger.warning(f"[Session] Invalid session_id format: {session_id}")
        raise HTTPException(status_code=400, detail="无效的会话 ID")

    # 尝试从 workspace/output/ 读取中间结果
    session_dir = config.workspace_output_dir / session_id

    result = {
        "session_id": session_id,
        "segments": None,
        "chapters": None,
        "analysis": None,
    }

    # 读取 transcript 中间结果
    transcript_file = session_dir / "transcript.json"
    if transcript_file.exists():
        try:
            with open(transcript_file, 'r', encoding='utf-8') as f:
                result["segments"] = json.load(f).get("segments", [])
        except Exception as e:
            logger.warning(f"[Session] Failed to read transcript: {e}")

    # 读取 analysis 中间结果
    analysis_file = session_dir / "analysis.json"
    if analysis_file.exists():
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                result["analysis"] = json.load(f)
                result["chapters"] = result["analysis"].get("chapters", [])
        except Exception as e:
            logger.warning(f"[Session] Failed to read analysis: {e}")

    return result

    # 临时文件存储在 temp_dir / session_id . ext
    temp_dir = Path(tempfile.gettempdir()) / "voice_upload"
    # 解析 temp_dir 为绝对路径，防止符号链接攻击
    temp_dir = temp_dir.resolve()

    # 查找对应的音频文件（尝试各种可能的扩展名）
    possible_files = []
    for ext in ['mp3', 'mp4', 'wav', 'm4a', 'ogg', 'flac', 'webm']:
        f = temp_dir / f"{session_id}.{ext}"
        # 使用 resolve() 解析符号链接，确保文件在预期目录内
        try:
            resolved_path = f.resolve()
            # 安全检查：确保解析后的路径仍在 temp_dir 内
            if not str(resolved_path).startswith(str(temp_dir)):
                logger.warning(f"[Audio] Path traversal attempt detected: {resolved_path}")
                continue
            if resolved_path.exists():
                possible_files.append(resolved_path)
        except (OSError, RuntimeError):
            # 处理符号链接断裂等情况
            continue

    if not possible_files:
        logger.warning(f"[Audio] File not found for session {session_id}")
        raise HTTPException(status_code=404, detail="音频文件不存在或已过期")

    audio_file = possible_files[0]
    ext = audio_file.suffix.lower()

    # 根据扩展名确定 content-type
    content_types = {
        '.mp3': 'audio/mpeg',
        '.mp4': 'audio/mp4',
        '.m4a': 'audio/m4a',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        '.webm': 'video/webm',
    }
    content_type = content_types.get(ext, 'application/octet-stream')

    logger.info(f"[Audio] Streaming audio for session {session_id}: {audio_file}")

    from fastapi.responses import FileResponse
    return FileResponse(
        path=audio_file,
        media_type=content_type,
        filename=audio_file.name
    )


# ============ 文本分析接口 ============

class AnalyzeRequest(BaseModel):
    """文本分析请求"""
    text: str = Field(..., description="待分析的文本内容")
    session_id: Optional[str] = Field(None, description="可选的会话 ID，用于缓存")


class AnalyzeResponse(BaseModel):
    """文本分析响应"""
    success: bool
    theme: Optional[str] = None
    summary: Optional[str] = None
    chapters: list = []
    speaker_roles: list = []
    topics: list = []
    key_points: list = []
    action_items: list = []
    raw_response: Optional[str] = None


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest, _auth: str = Depends(verify_api_key)):
    """
    分析文本内容

    输入转写文本，返回结构化的分析结果：
    - 会议主题
    - 章节划分
    - 发言人员角色
    - 摘要
    - 关键要点
    - 行动项
    """
    session_id = request.session_id or f"analyze_{uuid.uuid4().hex[:8]}"

    if not request.text or len(request.text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="文本内容太少，至少需要 10 个字符"
        )

    try:
        audio_analyzer = AudioAnalyzer()
        result = audio_analyzer.analyze_transcript(request.text)

        # 转换 AnalysisResult 中的对象为字典
        def to_dict_list(items):
            result_list = []
            for item in items:
                if hasattr(item, 'to_dict'):
                    result_list.append(item.to_dict())
                elif isinstance(item, dict):
                    result_list.append(item)
            return result_list

        return AnalyzeResponse(
            success=True,
            theme=result.theme,
            summary=result.summary,
            chapters=to_dict_list(result.chapters),
            speaker_roles=to_dict_list(result.speaker_roles),
            topics=result.topics,
            key_points=result.key_points,
            action_items=result.action_items,
            raw_response=result.raw_response,
        )

    except Exception as e:
        logger.error(f"[Analyze {session_id}] Error: {e}")
        import traceback
        logger.error(f"[Analyze {session_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 处理状态轮询接口 (JSON) ============

@router.get("/upload/{session_id}/progress")
async def upload_progress(session_id: str, _auth: str = Depends(verify_api_key)):
    """
    获取上传处理进度 (JSON 格式，用于轮询)

    Args:
        session_id: 上传会话 ID

    Returns:
        ProcessingInfo as JSON
    """
    import re
    if not re.match(r'^upload_[0-9a-f]{8}$', session_id):
        raise HTTPException(status_code=400, detail="无效的会话 ID")

    status_manager = get_processing_status_manager()
    info = status_manager.get(session_id)

    if not info:
        raise HTTPException(status_code=404, detail="会话不存在或已过期")

    return info.to_dict()


# ============ 处理状态 SSE 接口 ============

@router.get("/upload/{session_id}/status")
async def upload_status_stream(session_id: str, _auth: str = Depends(verify_api_key)):
    """
    订阅上传处理状态更新 (SSE)

    用于前端实时获取处理进度

    返回格式:
        event: status
        data: {"session_id": "...", "stage": "...", "progress": 50, "message": "...", ...}
    """
    status_manager = get_processing_status_manager()

    async def event_generator():
        # 创建队列用于传递状态更新
        queue: asyncio.Queue = asyncio.Queue()
        update_event = asyncio.Event()

        def on_update(info: ProcessingInfo):
            logger.info(f"[Upload {session_id}] SSE on_update callback: stage={info.stage}, progress={info.progress}")
            asyncio.create_task(queue.put(info))
            update_event.set()

        # 订阅状态更新
        status_manager.subscribe(session_id, on_update)
        logger.info(f"[Upload {session_id}] SSE subscribed to status updates")

        try:
            # 发送初始状态
            initial_info = status_manager.get(session_id)
            logger.info(f"[Upload {session_id}] SSE initial_info: {initial_info}")
            if initial_info:
                yield f"event: status\ndata: {json.dumps(initial_info.to_dict())}\n\n"

            # 持续发送更新直到完成或出错
            while True:
                # 等待新状态或超时
                try:
                    info = await asyncio.wait_for(queue.get(), timeout=30.0)
                    logger.info(f"[Upload {session_id}] SSE sending: stage={info.stage}, progress={info.progress}")
                    yield f"event: status\ndata: {json.dumps(info.to_dict())}\n\n"

                    # 如果处理完成或出错，发送最终状态后关闭
                    if info.stage in (ProcessingStage.COMPLETED, ProcessingStage.ERROR):
                        logger.info(f"[Upload {session_id}] SSE stream ending: {info.stage}")
                        break
                except asyncio.TimeoutError:
                    # 发送心跳
                    yield f"event: heartbeat\ndata: {json.dumps({'time': datetime.now().isoformat()})}\n\n"

        finally:
            # 取消订阅
            status_manager.unsubscribe(session_id, on_update)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
