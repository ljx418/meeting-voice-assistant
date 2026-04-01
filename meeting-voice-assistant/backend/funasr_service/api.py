"""
FunASR API 路由
"""

import tempfile
import logging
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from funasr_service.model_loader import recognize_audio

logger = logging.getLogger("funasr_service.api")

router = APIRouter()


class SentenceInfo(BaseModel):
    """句子信息"""
    text: str
    spk: int
    start_time: float
    end_time: float


class RecognizeResponse(BaseModel):
    """识别响应"""
    success: bool
    text: str
    sentences: List[SentenceInfo]
    message: Optional[str] = None


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "funasr"}


@router.post("/recognize", response_model=RecognizeResponse)
async def recognize(file: UploadFile = File(...)):
    """
    识别音频文件（带说话人分离）

    支持格式: wav, mp3, m4a, flac, ogg, webm, mp4

    Returns:
        RecognizeResponse: 包含说话人标签的识别结果
    """
    # 保存上传的文件到临时位置
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    logger.info(f"[FunASR API] Processing file: {file.filename}, size: {len(content)} bytes")

    try:
        # 调用 FunASR 进行识别
        result = recognize_audio(tmp_path)

        if not result or len(result) == 0:
            raise HTTPException(status_code=500, detail="No recognition result returned")

        result = result[0]

        # 解析结果
        sentences = []
        full_text = []

        sentence_info = result.get("sentence_info", [])

        # 计算累积时间（用于时间戳后备）
        cumulative_time = 0.0

        for idx, sent in enumerate(sentence_info):
            # 尝试获取时间戳，如果为0则使用累积时间计算
            start_ts = sent.get("start_time", 0.0)
            end_ts = sent.get("end_time", 0.0)

            # FunASR 有时返回的时间戳是 0，需要用累积时间计算
            if start_ts <= 0 and end_ts <= 0:
                # 使用句子索引作为后备标记
                start_time = cumulative_time
                end_time = cumulative_time + 3.0  # 假设每句3秒
                cumulative_time = end_time
            else:
                start_time = start_ts / 1000.0 if start_ts > 0 else cumulative_time
                end_time = end_ts / 1000.0 if end_ts > 0 else (start_time + 3.0)
                cumulative_time = end_time

            sentences.append(SentenceInfo(
                text=sent.get("text", ""),
                spk=sent.get("spk", 0),
                start_time=start_time,
                end_time=end_time,
            ))
            full_text.append(sent.get("text", ""))

        logger.info(f"[FunASR API] Recognition completed: {len(sentences)} sentences")

        return RecognizeResponse(
            success=True,
            text="".join(full_text),
            sentences=sentences,
        )

    except Exception as e:
        logger.error(f"[FunASR API] Recognition failed: {e}")
        import traceback
        logger.error(f"[FunASR API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # 清理临时文件
        try:
            Path(tmp_path).unlink()
        except Exception:
            pass
