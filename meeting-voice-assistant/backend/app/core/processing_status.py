"""
处理状态管理器

用于追踪长时间运行的任务状态，支持 SSE 实时推送
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Callable, Dict, List
from enum import Enum

logger = logging.getLogger("processing_status")


class ProcessingStage(str, Enum):
    """处理阶段"""
    IDLE = "idle"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ProcessingInfo:
    """处理信息"""
    session_id: str
    stage: ProcessingStage = ProcessingStage.IDLE
    progress: int = 0  # 0-100
    message: str = ""
    started_at: Optional[datetime] = None
    stage_started_at: Optional[datetime] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "stage": self.stage.value,
            "progress": self.progress,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "stage_started_at": self.stage_started_at.isoformat() if self.stage_started_at else None,
            "elapsed_seconds": (datetime.now() - self.started_at).total_seconds() if self.started_at else 0,
            "stage_elapsed_seconds": (datetime.now() - self.stage_started_at).total_seconds() if self.stage_started_at else 0,
            "error": self.error,
        }


class ProcessingStatusManager:
    """
    处理状态管理器

    使用示例:
        manager = ProcessingStatusManager()

        # 开始处理
        manager.start(session_id="upload_123")

        # 更新状态
        manager.update(session_id="upload_123", stage=ProcessingStage.TRANSCRIBING, progress=30, message="正在识别语音...")

        # 结束处理
        manager.complete(session_id="upload_123", message="处理完成")

        # SSE 订阅
        async def on_update(info: ProcessingInfo):
            print(f"Status: {info.stage} - {info.progress}%")

        manager.subscribe("upload_123", on_update)
    """

    def __init__(self):
        self._status: Dict[str, ProcessingInfo] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()

    def start(self, session_id: str) -> ProcessingInfo:
        """开始新的处理任务"""
        info = ProcessingInfo(
            session_id=session_id,
            stage=ProcessingStage.UPLOADING,
            progress=0,
            message="开始上传文件...",
            started_at=datetime.now(),
            stage_started_at=datetime.now(),
        )
        self._status[session_id] = info
        self._notify(session_id)
        logger.info(f"[ProcessingStatus] Started: {session_id}")
        return info

    def update(
        self,
        session_id: str,
        stage: Optional[ProcessingStage] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
    ) -> ProcessingInfo:
        """更新处理状态"""
        if session_id not in self._status:
            self.start(session_id)

        info = self._status[session_id]

        if stage is not None and stage != info.stage:
            info.stage = stage
            info.stage_started_at = datetime.now()
            logger.info(f"[ProcessingStatus] Stage changed: {session_id} -> {stage.value}")

        if progress is not None:
            info.progress = max(0, min(100, progress))

        if message is not None:
            info.message = message

        self._notify(session_id)
        return info

    def complete(self, session_id: str, message: str = "处理完成") -> ProcessingInfo:
        """标记处理完成"""
        if session_id in self._status:
            info = self._status[session_id]
            info.stage = ProcessingStage.COMPLETED
            info.progress = 100
            info.message = message
            info.stage_started_at = datetime.now()
            self._notify(session_id)
            logger.info(f"[ProcessingStatus] Completed: {session_id}")
        return self._status.get(session_id)

    def error(self, session_id: str, error_message: str) -> ProcessingInfo:
        """标记处理出错"""
        if session_id in self._status:
            info = self._status[session_id]
            info.stage = ProcessingStage.ERROR
            info.error = error_message
            info.message = f"错误: {error_message}"
            info.stage_started_at = datetime.now()
            self._notify(session_id)
            logger.error(f"[ProcessingStatus] Error: {session_id} - {error_message}")
        return self._status.get(session_id)

    def get(self, session_id: str) -> Optional[ProcessingInfo]:
        """获取处理状态"""
        return self._status.get(session_id)

    def subscribe(self, session_id: str, callback: Callable[[ProcessingInfo], None]):
        """订阅状态更新"""
        if session_id not in self._subscribers:
            self._subscribers[session_id] = []
        self._subscribers[session_id].append(callback)

    def unsubscribe(self, session_id: str, callback: Callable):
        """取消订阅"""
        if session_id in self._subscribers:
            self._subscribers[session_id] = [
                cb for cb in self._subscribers[session_id] if cb != callback
            ]

    def _notify(self, session_id: str):
        """通知订阅者"""
        if session_id in self._subscribers:
            info = self._status.get(session_id)
            if info:
                for callback in self._subscribers[session_id]:
                    try:
                        callback(info)
                    except Exception as e:
                        logger.error(f"[ProcessingStatus] Notify error: {e}")

    def remove(self, session_id: str):
        """移除处理状态"""
        if session_id in self._status:
            del self._status[session_id]
        if session_id in self._subscribers:
            del self._subscribers[session_id]


# 全局单例
_global_manager: Optional[ProcessingStatusManager] = None


def get_processing_status_manager() -> ProcessingStatusManager:
    """获取全局处理状态管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = ProcessingStatusManager()
    return _global_manager
