"""
文件上传路由

支持音频/视频文件上传并转写
"""

import asyncio
import uuid
import tempfile
import os
import json
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException
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
    analysis: Optional[dict] = None
    file_path: Optional[str] = None


@router.post("/upload", response_model=UploadResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    prompt: Optional[str] = None
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
        # 保存上传的文件
        logger.info(f"[Upload {session_id}] Saving file: {temp_file}")
        content = await file.read()
        file_size = len(content)

        # 检查文件大小 (DashScope 大文件 API 支持最大 512MB)
        max_size = 512 * 1024 * 1024  # 512MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"文件太大: {file_size / (1024*1024):.1f}MB。最大支持 512MB。"
            )

        with open(temp_file, 'wb') as f:
            f.write(content)
        logger.info(f"[Upload {session_id}] File saved: {file_size} bytes")

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
        try:
            # 读取音频文件并转写
            async for result in asr_adapter.recognize_file(temp_file):
                transcript_results.append(result)
                # 更新进度：转写中
                status_manager.update(
                    session_id,
                    progress=min(40, 10 + len(transcript_results) * 5),
                    message=f"正在识别语音... 已识别 {len(transcript_results)} 段"
                )
                logger.info(f"[Upload {session_id}] Transcribed: {result.text[:50]}...")

        finally:
            await asr_adapter.close()

        # 更新状态：转写完成，开始分析
        status_manager.update(
            session_id,
            stage=ProcessingStage.ANALYZING,
            progress=50,
            message=f"语音识别完成，共 {len(transcript_results)} 段，开始深度分析..."
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

        return UploadResponse(
            success=True,
            session_id=session_id,
            message="文件处理完成",
            transcript=transcript_text,
            segments=segments,
            analysis={
                # 原有分析结果（兼容）
                "summary": analysis_result.summary if analysis_result else None,
                "key_points": analysis_result.key_points if analysis_result else [],
                "action_items": analysis_result.action_items if analysis_result else [],
                "topics": analysis_result.topics if analysis_result else [],
                # 新的深度分析结果
                "theme": audio_analysis_result.theme if audio_analysis_result else None,
                "chapters": audio_analysis_result.chapters if audio_analysis_result else [],
                "speaker_roles": audio_analysis_result.speaker_roles if audio_analysis_result else [],
            } if analysis_result or audio_analysis_result else None,
            file_path=str(temp_file)
        )

    except Exception as e:
        logger.error(f"[Upload {session_id}] Error: {e}")
        import traceback
        logger.error(f"[Upload {session_id}] Traceback: {traceback.format_exc()}")
        status_manager.error(session_id, str(e))
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 清理临时文件
        try:
            if temp_file.exists():
                os.remove(temp_file)
                logger.info(f"[Upload {session_id}] Temp file cleaned up")
        except Exception as e:
            logger.warning(f"[Upload {session_id}] Failed to cleanup temp file: {e}")


@router.get("/upload/formats")
async def get_supported_formats():
    """获取支持的文件格式"""
    return {
        "supported_formats": [
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

        return AnalyzeResponse(
            success=True,
            theme=result.theme,
            summary=result.summary,
            chapters=result.chapters,
            speaker_roles=result.speaker_roles,
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
