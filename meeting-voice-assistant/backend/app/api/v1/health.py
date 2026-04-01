"""
健康检查路由
"""

from fastapi import APIRouter
from datetime import datetime

import sys
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from app.core.asr import ASRFactory
from app.models import HealthResponse

router = APIRouter()

# 服务启动时间
_start_time = datetime.now()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    健康检查接口

    返回服务状态和 ASR 引擎信息
    """
    asr_adapter = ASRFactory.create()

    return HealthResponse(
        status="healthy",
        asr_engine=asr_adapter.engine_name,
        asr_mode=getattr(asr_adapter, "mode", "unknown"),
        uptime=(datetime.now() - _start_time).total_seconds()
    )
