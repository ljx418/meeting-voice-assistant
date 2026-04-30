"""
日志收集 API

接收来自前端和其他服务的日志，统一定义到 logs 目录
"""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.utils.logger import setup_logger

router = APIRouter(prefix="/logs", tags=["日志"])

# 创建日志记录器
logger = setup_logger("frontend.logs", log_file="logs/frontend.log")


class LogEntry(BaseModel):
    """日志条目"""
    timestamp: str = Field(..., description="ISO 格式时间戳")
    level: str = Field(..., description="日志级别: debug, info, warn, error")
    message: str = Field(..., description="日志消息")
    context: Optional[dict] = Field(default=None, description="额外上下文")


class LogBatchRequest(BaseModel):
    """批量日志请求"""
    logs: list[LogEntry] = Field(..., max_length=100, description="日志条目列表")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def receive_log(entry: LogEntry):
    """
    接收单条日志

    - **timestamp**: ISO 格式时间戳
    - **level**: 日志级别 (debug/info/warn/error)
    - **message**: 日志消息
    - **context**: 可选的额外上下文
    """
    # 根据级别记录日志
    log_message = f"[{entry.level.upper()}] {entry.message}"
    if entry.context:
        log_message += f" | context: {entry.context}"

    if entry.level == "error":
        logger.error(log_message)
    elif entry.level == "warn":
        logger.warning(log_message)
    elif entry.level == "debug":
        logger.debug(log_message)
    else:
        logger.info(log_message)

    return {"status": "logged"}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def receive_batch(request: LogBatchRequest):
    """
    批量接收日志

    - **logs**: 日志条目列表 (最多 100 条)
    """
    count = 0
    for entry in request.logs:
        try:
            log_message = f"[{entry.level.upper()}] {entry.message}"
            if entry.context:
                log_message += f" | context: {entry.context}"

            if entry.level == "error":
                logger.error(log_message)
            elif entry.level == "warn":
                logger.warning(log_message)
            elif entry.level == "debug":
                logger.debug(log_message)
            else:
                logger.info(log_message)
            count += 1
        except Exception:
            continue

    return {"status": "logged", "count": count}