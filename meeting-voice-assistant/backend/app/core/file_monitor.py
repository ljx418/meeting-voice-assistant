"""
目录监控模块

使用 watchdog 实现目录监控，支持文件变更通知和级联删除。
功能：
- watchdog 递归监控（防抖动+文件大小检测）
- 级联删除（源文件→DB→GraphRAG索引）
- 回收站(30天)
"""

import asyncio
import json
import logging
import os
import shutil
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import uuid

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEvent,
    FileSystemEventHandler,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
    DirCreatedEvent,
    DirDeletedEvent,
    DirMovedEvent,
)

logger = logging.getLogger("file_monitor")


# ============================================================================
# 常量配置
# ============================================================================

RECYCLE_BIN_NAME = ".recycle_bin"
RECYCLE_BIN_RETENTION_DAYS = 30  # 回收站保留 30 天
MIN_FILE_SIZE_FOR_TRACKING = 1024  # 最小 1KB 文件才进行追踪


# ============================================================================
# 数据结构
# ============================================================================

class FileEventType(Enum):
    """文件事件类型"""
    CREATED = "created"
    DELETED = "deleted"
    MODIFIED = "modified"
    MOVED = "moved"
    DIR_CREATED = "dir_created"
    DIR_DELETED = "dir_deleted"
    DIR_MOVED = "dir_moved"


@dataclass
class FileChangeEvent:
    """文件变更事件"""
    event_type: FileEventType
    path: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_directory: bool = False
    src_path: Optional[str] = None  # 用于 MOVED 事件
    dest_path: Optional[str] = None  # 用于 MOVED 事件
    file_size: int = 0  # 文件大小


@dataclass
class MonitoredDirectory:
    """被监控的目录"""
    path: str
    recursive: bool = True
    patterns: Optional[List[str]] = None  # 文件名模式过滤
    ignore_patterns: Optional[List[str]] = None  # 忽略的模式
    on_change: Optional[Callable[[FileChangeEvent], None]] = None
    min_file_size: int = MIN_FILE_SIZE_FOR_TRACKING  # 最小文件大小


# ============================================================================
# 回收站管理
# ============================================================================

class RecycleBin:
    """
    回收站管理器

    将删除的文件移动到回收站而非直接删除，支持 30 天后自动清理。
    """

    def __init__(self, root_dir: Path, retention_days: int = RECYCLE_BIN_RETENTION_DAYS):
        self.root_dir = root_dir / RECYCLE_BIN_NAME
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self._metadata_file = self.root_dir / ".metadata.json"
        self._metadata: Dict[str, dict] = self._load_metadata()

    def _load_metadata(self) -> Dict[str, dict]:
        """加载元数据"""
        if self._metadata_file.exists():
            try:
                return json.loads(self._metadata_file.read_text())
            except Exception:
                return {}
        return {}

    def _save_metadata(self):
        """保存元数据"""
        self._metadata_file.write_text(json.dumps(self._metadata, ensure_ascii=False))

    def _get_trash_path(self, original_path: str) -> Path:
        """生成回收站中的唯一路径"""
        original = Path(original_path)
        unique_id = uuid.uuid4().hex[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trash_name = f"{original.stem}_{timestamp}_{unique_id}{original.suffix}"
        return self.root_dir / str(original.parent.name) / trash_name

    def move_to_trash(self, file_path: str) -> Optional[str]:
        """
        将文件移动到回收站

        Args:
            file_path: 原始文件路径

        Returns:
            str: 回收站中的新路径，失败返回 None
        """
        original = Path(file_path)
        if not original.exists():
            return None

        try:
            trash_path = self._get_trash_path(file_path)
            trash_path.parent.mkdir(parents=True, exist_ok=True)

            # 移动文件
            shutil.move(str(original), str(trash_path))

            # 记录元数据
            self._metadata[str(trash_path)] = {
                "original_path": str(original),
                "deleted_at": datetime.now().isoformat(),
                "file_size": original.stat().st_size if original.exists() else 0,
                "expires_at": (
                    datetime.now() + timedelta(days=self.retention_days)
                ).isoformat(),
            }
            self._save_metadata()

            logger.info(f"[RecycleBin] Moved to trash: {original} -> {trash_path}")
            return str(trash_path)

        except Exception as e:
            logger.error(f"[RecycleBin] Failed to move to trash: {e}")
            return None

    def restore_from_trash(self, trash_path: str) -> Optional[str]:
        """
        从回收站恢复文件

        Args:
            trash_path: 回收站中的路径

        Returns:
            str: 恢复后的原始路径，失败返回 None
        """
        trash_file = Path(trash_path)
        if not trash_file.exists() or trash_path not in self._metadata:
            return None

        try:
            original_path = self._metadata[trash_path]["original_path"]
            original = Path(original_path)
            original.parent.mkdir(parents=True, exist_ok=True)

            # 移动回原位置
            shutil.move(trash_path, str(original))

            # 删除元数据
            del self._metadata[trash_path]
            self._save_metadata()

            logger.info(f"[RecycleBin] Restored from trash: {trash_path} -> {original_path}")
            return str(original)

        except Exception as e:
            logger.error(f"[RecycleBin] Failed to restore: {e}")
            return None

    def cleanup_expired(self) -> List[str]:
        """
        清理过期的回收站文件

        Returns:
            List[str]: 已删除的文件路径列表
        """
        deleted = []
        now = datetime.now()

        for trash_path, meta in list(self._metadata.items()):
            try:
                expires_at = datetime.fromisoformat(meta["expires_at"])
                if now >= expires_at:
                    trash_file = Path(trash_path)
                    if trash_file.exists():
                        trash_file.unlink()
                    del self._metadata[trash_path]
                    deleted.append(trash_path)
                    logger.info(f"[RecycleBin] Cleaned up expired: {trash_path}")
            except Exception as e:
                logger.error(f"[RecycleBin] Failed to cleanup {trash_path}: {e}")

        if deleted:
            self._save_metadata()

        return deleted

    def list_trash(self) -> List[dict]:
        """列出回收站中的所有文件"""
        result = []
        for trash_path, meta in self._metadata.items():
            trash_file = Path(trash_path)
            result.append({
                "trash_path": trash_path,
                "original_path": meta["original_path"],
                "deleted_at": meta["deleted_at"],
                "expires_at": meta["expires_at"],
                "file_size": meta.get("file_size", 0),
                "exists": trash_file.exists(),
            })
        return result


# ============================================================================
# 文件系统事件处理器
# ============================================================================

class FileMonitorHandler(FileSystemEventHandler):
    """
    文件系统事件处理器

    特性：
    - 事件去抖动（debounce）
    - 文件大小检测
    """

    def __init__(
        self,
        monitored_dir: MonitoredDirectory,
        callback: Callable[[FileChangeEvent], None]
    ):
        super().__init__()
        self.monitored_dir = monitored_dir
        self.callback = callback
        self._pending_events: Dict[str, FileChangeEvent] = {}
        self._debounce_seconds = 0.5  # 事件去抖时间
        self._last_event_time: Dict[str, float] = {}

    def _should_process(self, path: str) -> bool:
        """检查是否应该处理该路径"""
        # 检查文件大小
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                if size < self.monitored_dir.min_file_size:
                    logger.debug(f"[FileMonitorHandler] Skipping small file: {path} ({size} bytes)")
                    return False
        except Exception:
            pass

        # 检查忽略模式
        if self.monitored_dir.ignore_patterns:
            from fnmatch import fnmatch
            filename = os.path.basename(path)
            dir_parts = path.split(os.sep)

            for pattern in self.monitored_dir.ignore_patterns:
                if fnmatch(filename, pattern):
                    return False
                if pattern.endswith("/*") and pattern[:-2] in dir_parts:
                    return False

        # 检查包含模式
        if self.monitored_dir.patterns:
            from fnmatch import fnmatch
            filename = os.path.basename(path)
            for pattern in self.monitored_dir.patterns:
                if fnmatch(filename, pattern):
                    return True
            return False

        return True

    def _should_debounce(self, path: str) -> bool:
        """检查是否应该去抖"""
        now = time.time()
        last_time = self._last_event_time.get(path, 0)

        if now - last_time < self._debounce_seconds:
            return True

        self._last_event_time[path] = now
        return False

    def _create_event(
        self,
        event_type: FileEventType,
        path: str,
        **kwargs
    ) -> FileChangeEvent:
        """创建文件变更事件"""
        file_size = 0
        try:
            if os.path.isfile(path):
                file_size = os.path.getsize(path)
        except Exception:
            pass

        return FileChangeEvent(
            event_type=event_type,
            path=path,
            is_directory=kwargs.get("is_directory", False),
            src_path=kwargs.get("src_path"),
            dest_path=kwargs.get("dest_path"),
            file_size=file_size,
        )

    def _dispatch(self, event: FileSystemEvent):
        """分发事件（带去抖）"""
        path = getattr(event, "path", None) or getattr(event, "src_path", "")

        if not path or not self._should_process(path):
            return

        # 去抖检查
        if self._should_debounce(path):
            logger.debug(f"[FileMonitorHandler] Debouncing event: {path}")
            return

        # 转换为统一事件类型
        if isinstance(event, FileCreatedEvent):
            evt = self._create_event(
                FileEventType.DIR_CREATED if event.is_directory else FileEventType.CREATED,
                path, is_directory=event.is_directory
            )
        elif isinstance(event, FileDeletedEvent):
            evt = self._create_event(
                FileEventType.DIR_DELETED if event.is_directory else FileEventType.DELETED,
                path, is_directory=event.is_directory
            )
        elif isinstance(event, FileModifiedEvent):
            evt = self._create_event(FileEventType.MODIFIED, path)
        elif isinstance(event, FileMovedEvent):
            dest_path = getattr(event, "dest_path", "")
            evt = self._create_event(
                FileEventType.DIR_MOVED if event.is_directory else FileEventType.MOVED,
                path,
                is_directory=event.is_directory,
                src_path=path,
                dest_path=dest_path,
            )
        else:
            return

        # 调用回调
        try:
            self.callback(evt)
        except Exception as e:
            logger.error(f"[FileMonitorHandler] Callback error: {e}")

    def on_created(self, event: FileCreatedEvent):
        self._dispatch(event)

    def on_deleted(self, event: FileDeletedEvent):
        self._dispatch(event)

    def on_modified(self, event: FileModifiedEvent):
        self._dispatch(event)

    def on_moved(self, event: FileMovedEvent):
        self._dispatch(event)


# ============================================================================
# 目录监控器
# ============================================================================

class FileMonitor:
    """
    目录监控器

    使用 watchdog 监控目录变化。
    特性：
    - 递归监控
    - 事件去抖
    - 文件大小过滤
    """

    def __init__(self):
        self._observer: Optional[Observer] = None
        self._monitored_dirs: Dict[str, MonitoredDirectory] = {}
        self._handlers: Dict[str, FileMonitorHandler] = {}
        self._watches: Dict[str, Any] = {}  # 保存 schedule() 返回的 watch 对象
        self._running = False

    def add_directory(
        self,
        path: str,
        recursive: bool = True,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
        on_change: Optional[Callable[[FileChangeEvent], None]] = None,
        min_file_size: int = MIN_FILE_SIZE_FOR_TRACKING,
    ) -> bool:
        """
        添加监控目录

        Args:
            path: 目录路径
            recursive: 是否递归监控子目录
            patterns: 文件名模式过滤
            ignore_patterns: 忽略的文件模式
            on_change: 变更回调函数
            min_file_size: 最小文件大小（字节），小于此大小的文件将被忽略

        Returns:
            bool: 是否添加成功
        """
        abs_path = str(Path(path).resolve())

        if abs_path in self._monitored_dirs:
            logger.warning(f"[FileMonitor] Directory already monitored: {abs_path}")
            return False

        monitored_dir = MonitoredDirectory(
            path=abs_path,
            recursive=recursive,
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            on_change=on_change,
            min_file_size=min_file_size,
        )

        self._monitored_dirs[abs_path] = monitored_dir
        logger.info(
            f"[FileMonitor] Added directory: {abs_path} "
            f"(recursive={recursive}, min_size={min_file_size})"
        )
        return True

    def remove_directory(self, path: str) -> bool:
        """移除监控目录"""
        abs_path = str(Path(path).resolve())

        if abs_path not in self._monitored_dirs:
            return False

        if self._running:
            self._observer.unschedule(self._watches[abs_path])

        del self._monitored_dirs[abs_path]
        del self._handlers[abs_path]
        if abs_path in self._watches:
            del self._watches[abs_path]
        logger.info(f"[FileMonitor] Removed directory: {abs_path}")
        return True

    def start(self) -> bool:
        """启动监控"""
        if self._running:
            return False

        if not self._monitored_dirs:
            logger.warning("[FileMonitor] No directories to monitor")
            return False

        self._observer = Observer()

        for abs_path, monitored_dir in self._monitored_dirs.items():
            handler = FileMonitorHandler(monitored_dir, self._on_change)
            self._handlers[abs_path] = handler

            watch = self._observer.schedule(
                handler,
                abs_path,
                recursive=monitored_dir.recursive
            )
            self._watches[abs_path] = watch

        self._observer.start()
        self._running = True
        logger.info(f"[FileMonitor] Started monitoring {len(self._monitored_dirs)} directories")
        return True

    def stop(self) -> bool:
        """停止监控"""
        if not self._running:
            return True

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=5)
            self._observer = None

        self._running = False
        logger.info("[FileMonitor] Stopped monitoring")
        return True

    def _on_change(self, event: FileChangeEvent):
        """处理文件变更事件"""
        logger.debug(f"[FileMonitor] File event: {event.event_type.value} - {event.path}")

        for abs_path, monitored_dir in self._monitored_dirs.items():
            if event.path.startswith(abs_path):
                if monitored_dir.on_change:
                    try:
                        monitored_dir.on_change(event)
                    except Exception as e:
                        logger.error(f"[FileMonitor] Event callback error: {e}")
                break

    def get_monitored_directories(self) -> List[str]:
        """获取所有监控目录"""
        return list(self._monitored_dirs.keys())

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running


# ============================================================================
# 级联删除管理器
# ============================================================================

class CascadeDeleteManager:
    """
    级联删除管理器

    实现源文件→DB→GraphRAG索引的级联删除。
    支持回收站功能。
    """

    # 音频文件扩展名
    AUDIO_EXTENSIONS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac", ".webm"}

    # 关联文件扩展名
    ASSOCIATED_EXTENSIONS = {".json", ".txt", ".vtt", ".srt", ".transcript"}

    def __init__(self, workspace_root: Optional[Path] = None):
        self._workspace_root = workspace_root or Path("./")
        self._recycle_bin: Optional[RecycleBin] = None
        self._delete_callbacks: List[Callable[[str], None]] = []
        self._use_recycle_bin = True

    @property
    def recycle_bin(self) -> RecycleBin:
        """获取回收站实例"""
        if self._recycle_bin is None:
            self._recycle_bin = RecycleBin(self._workspace_root)
        return self._recycle_bin

    def enable_recycle_bin(self, enabled: bool = True):
        """启用/禁用回收站"""
        self._use_recycle_bin = enabled

    def add_delete_callback(self, callback: Callable[[str], None]):
        """添加删除回调函数"""
        self._delete_callbacks.append(callback)

    def _get_associated_files(self, file_path: str) -> List[str]:
        """获取关联文件列表"""
        path = Path(file_path)
        stem = path.stem
        directory = path.parent
        associated = []

        for related_ext in self.ASSOCIATED_EXTENSIONS:
            related_path = directory / f"{stem}{related_ext}"
            if related_path.exists():
                associated.append(str(related_path))

        return associated

    async def delete_file_cascade(self, file_path: str) -> List[str]:
        """
        执行级联删除

        删除顺序：
        1. 源文件本身
        2. 关联文件（json/txt/vtt/srt等）
        3. DB 记录（通过回调）
        4. GraphRAG 索引（通过回调）

        Args:
            file_path: 要删除的文件路径

        Returns:
            List[str]: 已删除的文件路径列表
        """
        deleted = []
        path = Path(file_path)

        # 1. 处理源文件
        if path.exists():
            try:
                if self._use_recycle_bin:
                    # 移动到回收站
                    trash_path = self.recycle_bin.move_to_trash(str(path))
                    if trash_path:
                        deleted.append(trash_path)
                else:
                    path.unlink()
                    deleted.append(str(path))
                logger.info(f"[CascadeDelete] Deleted: {file_path}")
            except Exception as e:
                logger.error(f"[CascadeDelete] Failed to delete {file_path}: {e}")

        # 2. 删除关联文件
        associated_files = self._get_associated_files(file_path)
        for assoc_file in associated_files:
            try:
                assoc_path = Path(assoc_file)
                if self._use_recycle_bin:
                    trash_path = self.recycle_bin.move_to_trash(assoc_file)
                    if trash_path:
                        deleted.append(trash_path)
                else:
                    assoc_path.unlink()
                    deleted.append(assoc_file)
                logger.info(f"[CascadeDelete] Deleted associated: {assoc_file}")
            except Exception as e:
                logger.error(f"[CascadeDelete] Failed to delete {assoc_file}: {e}")

        # 3. 删除 session 目录（如果有）
        session_dir = path.parent
        if session_dir.exists() and session_dir.is_dir():
            # 检查是否为空或只有 .DS_Store 等隐藏文件
            remaining = [
                f for f in session_dir.iterdir()
                if not f.name.startswith(".")
            ]
            if not remaining:
                try:
                    if self._use_recycle_bin:
                        # 将空目录也移到回收站
                        trash_dir = self.recycle_bin.root_dir / session_dir.name
                        shutil.move(str(session_dir), str(trash_dir))
                    else:
                        session_dir.rmdir()
                    deleted.append(str(session_dir))
                    logger.info(f"[CascadeDelete] Removed empty session dir: {session_dir}")
                except Exception as e:
                    logger.error(f"[CascadeDelete] Failed to remove dir {session_dir}: {e}")

        # 4. 调用删除回调（用于删除 DB 和 GraphRAG 索引）
        for callback in self._delete_callbacks:
            try:
                callback(file_path)
            except Exception as e:
                logger.error(f"[CascadeDelete] Callback error: {e}")

        return deleted

    async def delete_graphrag_index(self, file_path: str) -> bool:
        """
        删除 GraphRAG 索引

        Args:
            file_path: 原始文件路径

        Returns:
            bool: 是否删除成功
        """
        try:
            # 获取文件名（不含扩展名）
            filename = Path(file_path).stem

            # GraphRAG 索引通常保存在 workspace/output/ 目录
            output_dir = self._workspace_root / "rag_workspace" / "output"
            if not output_dir.exists():
                return True

            # 查找相关的索引文件
            deleted_count = 0
            for ext in [".parquet", ".json", ".csv"]:
                # 查找以文件名开头的索引文件
                for index_file in output_dir.rglob(f"{filename}*{ext}"):
                    try:
                        index_file.unlink()
                        deleted_count += 1
                        logger.info(f"[CascadeDelete] Deleted GraphRAG index: {index_file}")
                    except Exception as e:
                        logger.error(f"[CascadeDelete] Failed to delete {index_file}: {e}")

            logger.info(f"[CascadeDelete] Deleted {deleted_count} GraphRAG index files for {filename}")
            return True

        except Exception as e:
            logger.error(f"[CascadeDelete] GraphRAG index deletion failed: {e}")
            return False

    def setup_monitoring(
        self,
        monitor: FileMonitor,
        directories: List[str],
        use_recycle_bin: bool = True
    ):
        """
        设置级联删除监控

        Args:
            monitor: FileMonitor 实例
            directories: 要监控的目录列表
            use_recycle_bin: 是否使用回收站
        """
        self._use_recycle_bin = use_recycle_bin

        async def on_file_deleted(event: FileChangeEvent):
            if event.event_type == FileEventType.DELETED and not event.is_directory:
                await self.delete_file_cascade(event.path)

        for directory in directories:
            monitor.add_directory(
                path=directory,
                recursive=True,
                on_change=lambda e: asyncio.create_task(
                    on_file_deleted(e)
                ) if e.event_type == FileEventType.DELETED else None,
            )

    def cleanup_recycle_bin(self) -> List[str]:
        """清理回收站过期文件"""
        return self.recycle_bin.cleanup_expired()


# ============================================================================
# 全局实例管理
# ============================================================================

_global_monitor: Optional[FileMonitor] = None
_global_cascade_manager: Optional[CascadeDeleteManager] = None


def get_file_monitor() -> FileMonitor:
    """获取全局文件监控器实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = FileMonitor()
    return _global_monitor


def get_cascade_delete_manager() -> CascadeDeleteManager:
    """获取全局级联删除管理器实例"""
    global _global_cascade_manager
    if _global_cascade_manager is None:
        _global_cascade_manager = CascadeDeleteManager()
    return _global_cascade_manager
