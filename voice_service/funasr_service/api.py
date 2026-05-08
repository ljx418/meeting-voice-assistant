import logging

from fastapi import APIRouter, UploadFile, File, HTTPException

from funasr_service.service import RecognizeResponse, recognize_upload

logger = logging.getLogger("funasr_service.api")

router = APIRouter()


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
    try:
        return recognize_upload(file.file, file.filename or "audio")
    except Exception as e:
        logger.error(f"[FunASR API] Recognition failed: {e}")
        import traceback
        logger.error(f"[FunASR API] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
