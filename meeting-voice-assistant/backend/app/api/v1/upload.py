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
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
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

logger = setup_logger("ws.upload")

router = APIRouter()

# 跟踪所有上传的临时文件，用于清理
_upload_temp_files: set = set()
_max_temp_age_seconds = 3600  # 1小时后清理


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
        session_dir = config.WORKSPACE_OUTPUT_DIR / session_id
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
        transcript_path = config.TRANSCRIPTS_DIR / f"{session_id}_transcript.txt"
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
    file_path: Optional[str] = None
    # 音频 URL（用于前端播放）
    audio_url: Optional[str] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    request: Request = None
):
    """
    上传音频/视频文件进行转写

    支持格式: mp3, mp4, wav, m4a, ogg, flac, webm
    注意: 文件大小限制 512MB

    Args:
        file: 上传的文件
        language: 可选语言代码 (如 "zh", "en")
        prompt: 可选提示词，帮助识别

    Returns:
        UploadResponse: 处理结果
    """
    session_id = f"upload_{uuid.uuid4().hex[:8]}"

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
        'audio/x-m4a': 'm4a',  # 浏览器可能发送的 MIME 类型
        'audio/ogg': 'ogg',
        'audio/flac': 'flac',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'application/octet-stream': None,  # 需要根据扩展名判断
    }

    content_type = file.content_type
    ext = allowed_types.get(content_type)

    if ext is None and content_type == 'application/octet-stream':
        # 尝试从文件名判断
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
            # 先读取一小块检查文件是否过大
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

            # 流式读取剩余内容
            while True:
                chunk = await file.read(64 * 1024 * 1024)  # 每次 64MB
                if not chunk:
                    break
                f.write(chunk)
                file_size += len(chunk)
                # 写入时检查是否超限
                if file_size > max_size:
                    f.close()
                    os.remove(temp_file)
                    raise HTTPException(
                        status_code=400,
                        detail=f"文件太大: {file_size / (1024*1024):.1f}MB。最大支持 512MB。"
                    )
        logger.info(f"[Upload {session_id}] File saved: {file_size} bytes")

        # 注册临时文件到清理队列
        _upload_temp_files.add(temp_file)

        # 更新状态：文件保存完成，开始转写
        status_manager.update(
            session_id,
            stage=ProcessingStage.TRANSCRIBING,
            progress=10,
            message=f"文件已保存({file_size / (1024*1024):.1f}MB)，开始语音识别..."
        )

        # 初始化 ASR (使用配置的引擎以支持说话人分离)
        # 如果需要说话人分离，应设置 ASR_ENGINE=funasr
        asr_engine = config.ASR_ENGINE
        # 文件上传场景：如果配置是 funasr_realtime，改为 funasr（FunASRAdapter 支持文件识别）
        if asr_engine == "funasr_realtime":
            asr_engine = "funasr"
        asr_adapter = ASRFactory.create(asr_engine)
        await asr_adapter.initialize()

        # 读取并转写音频
        logger.info(f"[Upload {session_id}] Starting transcription...")

        transcript_results: List = []  # 收集所有 ASRResult
        speakers: set = set()  # 收集说话人
        total_duration = 0.0  # 音频总时长
        try:
            # 读取音频文件并转写
            async for result in asr_adapter.recognize_file(temp_file):
                transcript_results.append(result)
                # 收集说话人
                if result.speaker:
                    speakers.add(result.speaker)
                # 收集时长
                if result.end_time > total_duration:
                    total_duration = result.end_time
                # 计算预估剩余时间
                elapsed = (datetime.now() - status_manager.get(session_id).started_at).total_seconds() if status_manager.get(session_id) else 1
                processed_count = len(transcript_results)
                # 简单估算：假设 10% 进度时开始转写，每识别一段估算剩余时间
                if processed_count > 0 and total_duration > 0:
                    # 估算完成需要的时间，基于已识别片段占总时长的比例
                    # 添加边界检查避免除零和负数
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

        finally:
            await asr_adapter.close()

        # 更新状态：转写完成，开始分析
        status_manager.update(
            session_id,
            stage=ProcessingStage.ANALYZING,
            progress=50,
            message=f"语音识别完成，共 {len(transcript_results)} 段，开始深度分析...",
            speaker_count=len(speakers),
            segment_count=len(transcript_results),
        )

        # 构建转写文本
        transcript_text = " ".join(r.text for r in transcript_results)

        # 构建结构化转写片段
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

        # 如果有录音，调用 LLM 分析
        analysis_result = None
        audio_analysis_result = None
        if transcript_text:
            try:
                # 原有 LLM 分析器（兼容）
                status_manager.update(
                    session_id,
                    progress=55,
                    message="正在进行内容摘要分析..."
                )
                llm_analyzer = LLMAnalyzer(
                    provider=config.LLM_PROVIDER,
                    api_key=config.LLM_API_KEY,
                    endpoint=config.LLM_ENDPOINT,
                    model=config.LLM_MODEL
                )
                analysis_result = await llm_analyzer.analyze_text(transcript_text)
                await llm_analyzer.close()
            except Exception as e:
                logger.warning(f"[Upload {session_id}] LLM analysis failed: {e}")

            # 使用新的 audio_analyzer 进行深度分析
            try:
                status_manager.update(
                    session_id,
                    progress=65,
                    message="正在进行深度语义分析..."
                )
                audio_analyzer = AudioAnalyzer()
                # 构建结构化片段
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
                logger.info(f"[Upload {session_id}] Audio analysis completed: theme={audio_analysis_result.theme[:50] if audio_analysis_result.theme else 'N/A'}...")

                # 更新状态：分析完成
                status_manager.update(
                    session_id,
                    progress=90,
                    message="分析完成，正在整理结果..."
                )
            except Exception as e:
                logger.warning(f"[Upload {session_id}] Audio analysis failed: {e}")

        # 保存转写文本到文件
        await _save_upload_transcript(session_id, transcript_results, analysis_result)

        # 标记处理完成
        status_manager.complete(session_id, "文件处理完成")

        # 优先使用 audio_analysis_result（AudioAnalyzer 使用 MiniMax/DeepSeek，结构更完整）
        # 如果没有，则使用 analysis_result（LLMAnalyzer 使用 DashScope）
        primary_result = audio_analysis_result or analysis_result

        # 转换结果为字典格式
        def to_dict_list(items, to_dict_attr='to_dict'):
            """将对象列表转换为字典列表"""
            result = []
            for item in items:
                if hasattr(item, to_dict_attr):
                    result.append(getattr(item, to_dict_attr)())
                elif isinstance(item, dict):
                    result.append(item)
            return result

        chapters_dict = to_dict_list(primary_result.chapters) if primary_result else []
        logger.info(f"[Upload {session_id}] LLM returned {len(chapters_dict)} chapters, segments count: {len(segments) if segments else 0}")

        # 关键修复：用实际 ASR segment 时间戳重新计算章节 start_time/end_time
        # LLM 生成的章节时间可能 hallucinate（如 end_time < start_time 或超出音频时长）
        if chapters_dict and segments:
            logger.info(f"[Upload {session_id}] Recalculating chapter timestamps...")
            chapters_dict = _recalculate_chapter_timestamps(chapters_dict, segments)
            logger.info(f"[Upload {session_id}] After recalculation: {len(chapters_dict)} chapters")
        else:
            logger.warning(f"[Upload {session_id}] Skipping recalculation: chapters={bool(chapters_dict)}, segments={bool(segments)}")
        speaker_roles_dict = to_dict_list(primary_result.speaker_roles) if primary_result else []

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

        # 构建音频 URL（供前端播放使用）
        # 使用请求的 host，避免硬编码 localhost
        if request:
            scheme = request.headers.get("x-forwarded-proto", "http")
            host = request.headers.get("host", "localhost:8000")
            audio_url = f"{scheme}://{host}/api/v1/upload/{session_id}/audio"
        else:
            audio_url = f"/api/v1/upload/{session_id}/audio"
        logger.info(f"[Upload {session_id}] Audio URL: {audio_url}")

        return UploadResponse(
            success=True,
            session_id=session_id,
            message="文件处理完成",
            transcript=transcript_text,
            segments=segments,
            # 统一格式字段（按段落维度输出）
            chapters=chapters_dict,
            theme=primary_result.theme if primary_result else None,
            topics=primary_result.topics if primary_result else [],
            speaker_roles=speaker_roles_dict,
            # 兼容字段（新版统一格式）
            analysis={
                "summary": primary_result.summary if primary_result else None,
                "key_points": primary_result.key_points if primary_result else [],
                "action_items": primary_result.action_items if primary_result else [],
                "topics": primary_result.topics if primary_result else [],
                "theme": primary_result.theme if primary_result else None,
                "chapters": chapters_dict,
                "speaker_roles": speaker_roles_dict,
            } if primary_result else None,
            file_path=str(temp_file),
            audio_url=audio_url
        )

    except Exception as e:
        logger.error(f"[Upload {session_id}] Error: {e}")
        import traceback
        logger.error(f"[Upload {session_id}] Traceback: {traceback.format_exc()}")
        status_manager.error(session_id, str(e))
        raise HTTPException(status_code=500, detail="文件处理失败，请稍后重试。")

    finally:
        # 保留临时文件以便前端通过 /upload/{session_id}/audio 访问
        # 清理由 audio_cache cleanup 或定时任务完成
        logger.info(f"[Upload {session_id}] Temp file kept at {temp_file} for audio streaming")


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
async def get_uploaded_audio(session_id: str):
    """
    获取上传的音频文件（用于前端播放）

    Args:
        session_id: 上传会话 ID

    Returns:
        Audio file stream
    """
    # 临时文件存储在 temp_dir / session_id . ext
    temp_dir = Path(tempfile.gettempdir()) / "voice_upload"

    # 查找对应的音频文件（尝试各种可能的扩展名）
    possible_files = []
    for ext in ['mp3', 'mp4', 'wav', 'm4a', 'ogg', 'flac', 'webm']:
        f = temp_dir / f"{session_id}.{ext}"
        if f.exists():
            possible_files.append(f)

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
async def analyze_text(request: AnalyzeRequest):
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


# ============ 处理状态 SSE 接口 ============

@router.get("/upload/{session_id}/status")
async def upload_status_stream(session_id: str):
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
            asyncio.create_task(queue.put(info))
            update_event.set()

        # 订阅状态更新
        status_manager.subscribe(session_id, on_update)

        try:
            # 发送初始状态
            initial_info = status_manager.get(session_id)
            if initial_info:
                yield f"event: status\ndata: {json.dumps(initial_info.to_dict())}\n\n"

            # 持续发送更新直到完成或出错
            while True:
                # 等待新状态或超时
                try:
                    info = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"event: status\ndata: {json.dumps(info.to_dict())}\n\n"

                    # 如果处理完成或出错，发送最终状态后关闭
                    if info.stage in (ProcessingStage.COMPLETED, ProcessingStage.ERROR):
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
