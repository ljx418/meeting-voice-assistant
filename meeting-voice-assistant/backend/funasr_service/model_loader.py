"""
FunASR 模型加载器

加载 FunASR 模型用于说话人分离识别
"""

import logging
from functools import lru_cache

from funasr import AutoModel

from .config import (
    MODEL_DEVICE,
    MODEL_NAME,
    VAD_MODEL,
    SPEAKER_MODEL,
    PUNC_MODEL,
)

logger = logging.getLogger("funasr_service.model_loader")


@lru_cache(maxsize=1)
def load_model():
    """
    加载 FunASR 模型

    使用懒加载，首次调用时加载模型并缓存

    Returns:
        AutoModel: FunASR 模型实例
    """
    logger.info(f"[FunASR Model] Loading model: device={MODEL_DEVICE}")
    logger.info(f"[FunASR Model] Model: {MODEL_NAME}, VAD: {VAD_MODEL}, SPK: {SPEAKER_MODEL}, PUNC: {PUNC_MODEL}")

    try:
        model = AutoModel(
            model=MODEL_NAME,
            vad_model=VAD_MODEL,
            punc_model=PUNC_MODEL,
            spk_model=SPEAKER_MODEL,
            device=MODEL_DEVICE,
        )
        logger.info("[FunASR Model] Model loaded successfully")
        return model
    except Exception as e:
        logger.error(f"[FunASR Model] Failed to load model: {e}")
        raise


def recognize_audio(file_path: str):
    """
    识别音频文件

    Args:
        file_path: 音频文件路径

    Returns:
        dict: 识别结果，包含 sentence_info 列表
    """
    model = load_model()
    result = model.generate(
        input=file_path,
        batch_size_s=300,
        sentence_timestamp=True,  # 启用说话人分离
    )
    return result
