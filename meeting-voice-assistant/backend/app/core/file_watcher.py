"""
文件监听器模块 - 基于 watchdog 的目录监控 + 外部知识服务索引

功能：
- 监听用户指定的本地文件夹变化
- 检测文件创建、修改、删除事件
- 自动触发独立 Local Knowledge Governance Service 增量导入/构建

使用方式:
    from app.core.file_watcher import FileWatcher, get_file_watcher

    # 初始化监听器
    watcher = FileWatcher()
    watcher.add_directory("/path/to/watch", recursive=True)
    watcher.start()

    # 或使用全局实例
    watcher = get_file_watcher()
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    FileCreatedEvent,
    FileDeletedEvent,
    FileModifiedEvent,
    FileMovedEvent,
)

from app.config import config
from .file_monitor import (
    FileMonitor,
    FileChangeEvent,
    FileEventType,
    get_file_monitor,
    get_cascade_delete_manager,
    CascadeDeleteManager,
)

logger = logging.getLogger("file_watcher")


# ============================================================================
# 配置验证
# ============================================================================

class WatchFolderConfigError(Exception):
    """监听文件夹配置错误"""
    pass


def validate_watch_folder(path: Optional[str]) -> Path:
    """
    验证监听文件夹配置

    Args:
        path: 文件夹路径

    Returns:
        Path: 验证通过的路径

    Raises:
        WatchFolderConfigError: 配置无效
    """
    if not path:
        raise WatchFolderConfigError(
            "WATCH_FOLDER_PATH is not configured. "
            "Please set WATCH_FOLDER_PATH in .env file to enable file watching."
        )

    folder_path = Path(path)

    # 检查是否存在
    if not folder_path.exists():
        raise WatchFolderConfigError(f"Watch folder does not exist: {path}")

    # 检查是否为目录
    if not folder_path.is_dir():
        raise WatchFolderConfigError(f"Watch path is not a directory: {path}")

    # 检查是否有读写权限
    if not os.access(folder_path, os.R_OK | os.W_OK):
        raise WatchFolderConfigError(f"Watch folder is not accessible: {path}")

    return folder_path


import os  # 确保 os 模块可用


# ============================================================================
# 外部知识服务触发器接口
# ============================================================================

class IndexTriggerBase:
    """索引触发器基类"""

    async def on_file_created(self, file_path: str) -> bool:
        """文件创建时触发索引"""
        raise NotImplementedError

    async def on_file_modified(self, file_path: str) -> bool:
        """文件修改时触发索引"""
        raise NotImplementedError

    async def on_file_deleted(self, file_path: str) -> bool:
        """文件删除时触发索引"""
        raise NotImplementedError


class KnowledgeServiceIndexTrigger(IndexTriggerBase):
    """
    知识服务索引触发器

    会议应用不再导入旧内嵌图谱模块；文件变化只通过 HTTP
    调用独立 data_service 的 source import / build contract。
    """

    # 支持索引的文件类型
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.pdf', '.docx', '.doc',
        '.pptx', '.xlsx', '.csv', '.json', '.jsonl',
        '.html', '.xml', '.eml', '.msg',
        '.mp3', '.mp4', '.wav', '.m4a', '.ogg', '.flac', '.webm',
    }

    def __init__(self, service_url: Optional[str] = None):
        self.service_url = (
            service_url
            or os.getenv("DATA_SERVICE_HTTP_BASE_URL")
            or "http://127.0.0.1:8003/api/v1/knowledge"
        ).rstrip("/")
        self._http_client: Optional[Any] = None
        self._session_id = "watcher"

    async def _get_http_client(self):
        """获取 HTTP 客户端"""
        if self._http_client is None:
            import httpx
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    def _is_indexable(self, file_path: str) -> bool:
        """检查文件是否可索引"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    def _workspace_for_file(self, file_path: str) -> str:
        return (
            os.getenv("DATA_SERVICE_WATCH_WORKSPACE")
            or os.getenv("DATA_SERVICE_WORKSPACE")
            or str(Path(file_path).parent)
        )

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        api_key = os.getenv("DATA_SERVICE_API_KEY", "").strip()
        if api_key:
            headers["x-api-key"] = api_key
        return headers

    async def _trigger_index(self, file_path: str) -> bool:
        """触发独立知识服务增量索引。"""
        if not self._is_indexable(file_path):
            logger.debug(f"[KnowledgeServiceTrigger] Skipping non-indexable file: {file_path}")
            return False

        try:
            client = await self._get_http_client()
            workspace = self._workspace_for_file(file_path)
            import_response = await client.post(
                f"{self.service_url}/sources/import",
                json={
                    "workspace": workspace,
                    "paths": [file_path],
                    "metadata": {"source": "meeting_file_watcher"},
                },
                headers=self._headers(),
            )
            import_response.raise_for_status()
            build_response = await client.post(
                f"{self.service_url}/build/start",
                json={"workspace": workspace, "mode": "incremental", "paths": [file_path]},
                headers=self._headers(),
            )
            build_response.raise_for_status()
            logger.info(f"[KnowledgeServiceTrigger] Delegated indexing to data_service: {file_path}")
            return True

        except Exception as e:
            logger.error(f"[KnowledgeServiceTrigger] Index error for {file_path}: {e}")
            return False

    async def on_file_created(self, file_path: str) -> bool:
        """文件创建时触发索引"""
        return await self._trigger_index(file_path)

    async def on_file_modified(self, file_path: str) -> bool:
        """文件修改时触发索引"""
        # 修改时先删后建，等价于重新索引
        return await self._trigger_index(file_path)

    async def on_file_deleted(self, file_path: str) -> bool:
        """文件删除时触发索引"""
        logger.info(f"[KnowledgeServiceTrigger] File deleted (external cleanup required): {file_path}")
        return True


# ============================================================================
# 文件监听器
# ============================================================================

class FileWatcher:
    """
    文件监听器

    基于 watchdog 的增强版监听器，支持：
    - 自动触发外部知识服务索引
    - 版本记录
    - 级联删除

    使用方式:
        watcher = FileWatcher()
        watcher.add_directory("/path/to/watch", recursive=True)
        watcher.start()
    """

    def __init__(
        self,
        watch_folder_path: Optional[str] = None,
        enabled: bool = True,
        auto_index_on_change: bool = True,
        index_trigger: Optional[IndexTriggerBase] = None,
    ):
        """
        初始化文件监听器

        Args:
            watch_folder_path: 监听文件夹路径（从配置或手动指定）
            enabled: 是否启用监听
            auto_index_on_change: 文件变化时是否自动触发索引
            index_trigger: 索引触发器实例
        """
        self._watch_folder_path: Optional[str] = watch_folder_path
        self._enabled = enabled
        self._auto_index_on_change = auto_index_on_change
        self._index_trigger = index_trigger or KnowledgeServiceIndexTrigger()

        self._file_monitor: Optional[FileMonitor] = None
        self._observer: Optional[Observer] = None
        self._running = False
        self._handlers: Dict[str, FileWatcherHandler] = {}

    def configure(
        self,
        watch_folder_path: Optional[str] = None,
        enabled: Optional[bool] = None,
        auto_index_on_change: Optional[bool] = None,
    ):
        """
        配置监听器

        Args:
            watch_folder_path: 监听文件夹路径
            enabled: 是否启用
            auto_index_on_change: 自动索引
        """
        if watch_folder_path is not None:
            self._watch_folder_path = watch_folder_path

        if enabled is not None:
            self._enabled = enabled

        if auto_index_on_change is not None:
            self._auto_index_on_change = auto_index_on_change

    @property
    def watch_folder_path(self) -> Optional[str]:
        """获取监听文件夹路径"""
        return self._watch_folder_path

    @property
    def is_enabled(self) -> bool:
        """是否启用"""
        return self._enabled

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running

    def add_directory(
        self,
        path: str,
        recursive: bool = True,
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
    ) -> bool:
        """
        添加监听目录

        Args:
            path: 目录路径
            recursive: 是否递归
            patterns: 文件名模式过滤
            ignore_patterns: 忽略模式

        Returns:
            bool: 是否成功
        """
        if not self._enabled:
            logger.warning("[FileWatcher] Watcher is disabled")
            return False

        if not path:
            logger.error("[FileWatcher] No path provided")
            return False

        # 验证路径
        try:
            folder_path = validate_watch_folder(path)
        except WatchFolderConfigError as e:
            logger.error(f"[FileWatcher] Invalid path: {e}")
            return False

        # 使用 FileMonitor 添加目录
        self._file_monitor = get_file_monitor()
        return self._file_monitor.add_directory(
            path=str(folder_path),
            recursive=recursive,
            patterns=patterns,
            ignore_patterns=ignore_patterns,
            on_change=self._on_file_change,
        )

    def _on_file_change(self, event: FileChangeEvent):
        """文件变化回调"""
        if not self._auto_index_on_change:
            return

        logger.info(
            f"[FileWatcher] File {event.event_type.value}: {event.path}"
        )

        # 异步触发索引
        asyncio.create_task(self._trigger_index_async(event))

    async def _trigger_index_async(self, event: FileChangeEvent):
        """异步触发索引"""
        try:
            if event.event_type == FileEventType.CREATED:
                await self._index_trigger.on_file_created(event.path)
            elif event.event_type == FileEventType.MODIFIED:
                await self._index_trigger.on_file_modified(event.path)
            elif event.event_type == FileEventType.DELETED:
                await self._index_trigger.on_file_deleted(event.path)
        except Exception as e:
            logger.error(f"[FileWatcher] Index trigger error: {e}")

    def start(self) -> bool:
        """
        启动监听

        Returns:
            bool: 是否成功
        """
        if not self._enabled:
            logger.warning("[FileWatcher] Watcher is disabled")
            return False

        if self._running:
            logger.warning("[FileWatcher] Already running")
            return False

        # 如果没有添加目录，使用配置的默认目录
        if not self._file_monitor or not self._file_monitor.get_monitored_directories():
            if self._watch_folder_path:
                if not self.add_directory(self._watch_folder_path):
                    logger.error("[FileWatcher] Failed to add default directory")
                    return False
            else:
                logger.warning("[FileWatcher] No directories to watch")
                return False

        # 启动 FileMonitor
        self._file_monitor = get_file_monitor()
        if self._file_monitor.start():
            self._running = True
            logger.info("[FileWatcher] Started")
            return True

        return False

    def stop(self) -> bool:
        """
        停止监听

        Returns:
            bool: 是否成功
        """
        if not self._running:
            return True

        if self._file_monitor:
            self._file_monitor.stop()

        self._running = False
        logger.info("[FileWatcher] Stopped")
        return True

    def get_status(self) -> dict:
        """
        获取监听器状态

        Returns:
            dict: 状态信息
        """
        return {
            "enabled": self._enabled,
            "running": self._running,
            "watch_folder_path": self._watch_folder_path,
            "auto_index_on_change": self._auto_index_on_change,
            "monitored_directories": (
                self._file_monitor.get_monitored_directories()
                if self._file_monitor else []
            ),
        }


class FileWatcherHandler(FileSystemEventHandler):
    """文件监听处理器"""

    def __init__(
        self,
        callback: Callable[[FileChangeEvent], None],
        patterns: Optional[List[str]] = None,
        ignore_patterns: Optional[List[str]] = None,
    ):
        super().__init__()
        self._callback = callback
        self._patterns = patterns
        self._ignore_patterns = ignore_patterns

    def _should_process(self, path: str) -> bool:
        """检查是否应该处理"""
        from fnmatch import fnmatch

        filename = os.path.basename(path)

        # 检查忽略模式
        if self._ignore_patterns:
            for pattern in self._ignore_patterns:
                if fnmatch(filename, pattern):
                    return False

        # 检查包含模式
        if self._patterns:
            for pattern in self._patterns:
                if fnmatch(filename, pattern):
                    return True
            return False

        return True

    def on_created(self, event: FileCreatedEvent):
        if self._should_process(event.path):
            self._callback(event.path, "created")

    def on_deleted(self, event: FileDeletedEvent):
        if self._should_process(event.path):
            self._callback(event.path, "deleted")

    def on_modified(self, event: FileModifiedEvent):
        if self._should_process(event.path):
            self._callback(event.path, "modified")

    def on_moved(self, event: FileMovedEvent):
        if self._should_process(event.path):
            self._callback(event.src_path, "deleted")
            self._callback(event.dest_path, "created")


# ============================================================================
# 全局实例管理
# ============================================================================

_global_watcher: Optional[FileWatcher] = None


def get_file_watcher(
    watch_folder_path: Optional[str] = None,
    enabled: bool = True,
    auto_index_on_change: bool = True,
) -> FileWatcher:
    """
    获取全局文件监听器实例

    Args:
        watch_folder_path: 监听文件夹路径
        enabled: 是否启用
        auto_index_on_change: 自动索引

    Returns:
        FileWatcher: 文件监听器实例
    """
    global _global_watcher

    if _global_watcher is None:
        # 从配置读取
        config_path = getattr(config, 'watch_folder_path', None)
        config_enabled = getattr(config, 'watch_folder_enabled', True)
        config_auto_index = getattr(config, 'auto_index_on_change', True)

        _global_watcher = FileWatcher(
            watch_folder_path=watch_folder_path or config_path,
            enabled=enabled and config_enabled,
            auto_index_on_change=auto_index_on_change and config_auto_index,
        )

    return _global_watcher


def start_file_watcher(watch_folder_path: Optional[str] = None) -> bool:
    """
    启动全局文件监听器

    Args:
        watch_folder_path: 监听文件夹路径

    Returns:
        bool: 是否成功
    """
    watcher = get_file_watcher(watch_folder_path=watch_folder_path)

    if watch_folder_path:
        watcher.configure(watch_folder_path=watch_folder_path)

    return watcher.start()


def stop_file_watcher() -> bool:
    """
    停止全局文件监听器

    Returns:
        bool: 是否成功
    """
    global _global_watcher

    if _global_watcher:
        result = _global_watcher.stop()
        _global_watcher = None
        return result

    return True
