"""
GraphRAG 增强模块

功能：
- 文档自动索引（基于文件监听触发）
- 知识查询API优化
- 多文件关联
- 与 file_watcher 集成
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable, Awaitable
from dataclasses import dataclass, field
import json
import hashlib

from app.config import config

logger = logging.getLogger("graphrag.enhancements")


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class DocumentIndex:
    """文档索引记录"""
    doc_id: str
    file_path: str
    file_hash: str
    indexed_at: datetime
    entity_count: int = 0
    relationship_count: int = 0
    community_count: int = 0
    status: str = "pending"  # pending, indexing, completed, failed


@dataclass
class MultiFileIndexResult:
    """多文件索引结果"""
    total_files: int
    indexed: int
    failed: int
    errors: List[str] = field(default_factory=list)


# ============================================================================
# 索引状态管理器
# ============================================================================

class IndexStateManager:
    """
    索引状态管理器

    跟踪文件索引状态，支持增量索引和变更检测
    """

    def __init__(self, state_file: Optional[Path] = None):
        self._state_file = state_file or Path("./data/index_state.json")
        self._state_file.parent.mkdir(parents=True, exist_ok=True)
        self._indexed_files: Dict[str, DocumentIndex] = {}
        self._load_state()

    def _load_state(self):
        """加载索引状态"""
        if self._state_file.exists():
            try:
                data = json.loads(self._state_file.read_text())
                for doc_id, info in data.get('indexed_files', {}).items():
                    info['indexed_at'] = datetime.fromisoformat(info['indexed_at'])
                    self._indexed_files[doc_id] = DocumentIndex(**info)
            except Exception as e:
                logger.error(f"[IndexStateManager] Failed to load state: {e}")

    def _save_state(self):
        """保存索引状态"""
        try:
            data = {
                'indexed_files': {
                    doc_id: {
                        'doc_id': info.doc_id,
                        'file_path': info.file_path,
                        'file_hash': info.file_hash,
                        'indexed_at': info.indexed_at.isoformat(),
                        'entity_count': info.entity_count,
                        'relationship_count': info.relationship_count,
                        'community_count': info.community_count,
                        'status': info.status,
                    }
                    for doc_id, info in self._indexed_files.items()
                }
            }
            self._state_file.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception as e:
            logger.error(f"[IndexStateManager] Failed to save state: {e}")

    def get_file_hash(self, file_path: str) -> str:
        """计算文件 hash"""
        hasher = hashlib.md5()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
        except Exception as e:
            logger.error(f"[IndexStateManager] Failed to hash {file_path}: {e}")
        return hasher.hexdigest()

    def is_file_changed(self, file_path: str) -> bool:
        """检查文件是否已变更"""
        doc_id = str(Path(file_path).resolve())

        if doc_id not in self._indexed_files:
            return True

        current_hash = self.get_file_hash(file_path)
        return current_hash != self._indexed_files[doc_id].file_hash

    def mark_indexing(self, file_path: str) -> str:
        """标记文件开始索引"""
        doc_id = str(Path(file_path).resolve())
        file_hash = self.get_file_hash(file_path)

        self._indexed_files[doc_id] = DocumentIndex(
            doc_id=doc_id,
            file_path=file_path,
            file_hash=file_hash,
            indexed_at=datetime.now(),
            status="indexing",
        )
        self._save_state()
        return doc_id

    def mark_completed(
        self,
        doc_id: str,
        entity_count: int = 0,
        relationship_count: int = 0,
        community_count: int = 0,
    ):
        """标记索引完成"""
        if doc_id in self._indexed_files:
            self._indexed_files[doc_id].status = "completed"
            self._indexed_files[doc_id].entity_count = entity_count
            self._indexed_files[doc_id].relationship_count = relationship_count
            self._indexed_files[doc_id].community_count = community_count
            self._save_state()

    def mark_failed(self, doc_id: str, error: str = ""):
        """标记索引失败"""
        if doc_id in self._indexed_files:
            self._indexed_files[doc_id].status = "failed"
            self._save_state()

    def get_status(self, file_path: str) -> Optional[str]:
        """获取文件索引状态"""
        doc_id = str(Path(file_path).resolve())
        return self._indexed_files.get(doc_id, None)

    def get_all_indexed(self) -> List[DocumentIndex]:
        """获取所有已索引文件"""
        return list(self._indexed_files.values())


# ============================================================================
# 自动索引器
# ============================================================================

class AutoIndexer:
    """
    自动索引器

    响应文件变化自动触发 GraphRAG 索引
    """

    # 支持的文件类型
    SUPPORTED_EXTENSIONS = {
        '.txt', '.md', '.markdown', '.pdf', '.docx', '.doc',
        '.pptx', '.xlsx', '.csv', '.json', '.jsonl',
        '.html', '.xml', '.eml', '.msg',
    }

    def __init__(
        self,
        state_manager: Optional[IndexStateManager] = None,
        graphrag_service_url: Optional[str] = None,
    ):
        self._state_manager = state_manager or IndexStateManager()
        self._graphrag_url = graphrag_service_url or config.graphrag.service_url
        self._index_callbacks: List[Callable[[str, dict], Awaitable[None]]] = []

    def add_index_callback(self, callback: Callable[[str, dict], Awaitable[None]]):
        """添加索引完成回调"""
        self._index_callbacks.append(callback)

    def can_index(self, file_path: str) -> bool:
        """检查文件是否可索引"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS

    async def index_file(self, file_path: str) -> bool:
        """
        索引单个文件

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否成功
        """
        if not self.can_index(file_path):
            logger.debug(f"[AutoIndexer] Unsupported file type: {file_path}")
            return False

        # 检查文件是否变更
        if not self._state_manager.is_file_changed(file_path):
            logger.debug(f"[AutoIndexer] File unchanged, skipping: {file_path}")
            return True

        # 标记开始索引
        doc_id = self._state_manager.mark_indexing(file_path)

        try:
            import httpx

            async with httpx.AsyncClient(timeout=120.0) as client:
                with open(file_path, 'rb') as f:
                    files = {'doc': (Path(file_path).name, f)}
                    data = {'session_id': 'default'}

                    response = await client.post(
                        f"{self._graphrag_url}/api/v1/index/",
                        files=files,
                        data=data,
                    )

                if response.status_code == 200:
                    result = response.json()
                    self._state_manager.mark_completed(
                        doc_id,
                        entity_count=result.get('entities_count', 0),
                        relationship_count=result.get('relationships_count', 0),
                        community_count=result.get('communities_count', 0),
                    )

                    logger.info(
                        f"[AutoIndexer] Indexed: {file_path} "
                        f"(entities={result.get('entities_count', 0)})"
                    )

                    # 触发回调
                    for callback in self._index_callbacks:
                        try:
                            await callback(doc_id, result)
                        except Exception as e:
                            logger.error(f"[AutoIndexer] Callback error: {e}")

                    return True
                else:
                    self._state_manager.mark_failed(doc_id)
                    logger.error(
                        f"[AutoIndexer] Index failed for {file_path}: "
                        f"HTTP {response.status_code}"
                    )
                    return False

        except Exception as e:
            self._state_manager.mark_failed(doc_id, str(e))
            logger.error(f"[AutoIndexer] Index error for {file_path}: {e}")
            return False

    async def index_batch(self, file_paths: List[str]) -> MultiFileIndexResult:
        """
        批量索引文件

        Args:
            file_paths: 文件路径列表

        Returns:
            MultiFileIndexResult: 索引结果
        """
        result = MultiFileIndexResult(total_files=len(file_paths))

        for file_path in file_paths:
            try:
                if await self.index_file(file_path):
                    result.indexed += 1
                else:
                    result.failed += 1
                    result.errors.append(f"Failed: {file_path}")
            except Exception as e:
                result.failed += 1
                result.errors.append(f"Error: {file_path} - {e}")

        return result

    async def reindex_all(self) -> MultiFileIndexResult:
        """
        重新索引所有已跟踪的文件

        Returns:
            MultiFileIndexResult: 索引结果
        """
        indexed = self._state_manager.get_all_indexed()
        file_paths = [info.file_path for info in indexed if Path(info.file_path).exists()]

        # 重置所有状态
        for info in indexed:
            info.status = "pending"

        return await self.index_batch(file_paths)


# ============================================================================
# 文件监听集成
# ============================================================================

class FileWatcherIndexIntegration:
    """
    FileWatcher 与 GraphRAG 索引集成

    当 file_watcher 检测到文件变化时，自动触发 GraphRAG 索引
    """

    def __init__(
        self,
        auto_indexer: Optional[AutoIndexer] = None,
        version_control: Optional[Any] = None,
    ):
        self._auto_indexer = auto_indexer or AutoIndexer()
        self._version_control = version_control
        self._is_initialized = False

    async def on_file_created(self, file_path: str) -> bool:
        """文件创建时触发索引"""
        logger.info(f"[FileWatcherIndexIntegration] File created: {file_path}")

        # 索引新文件
        success = await self._auto_indexer.index_file(file_path)

        # 记录初始版本
        if success and self._version_control:
            try:
                self._version_control.record_version(
                    file_path,
                    comment="Initial version from auto-index"
                )
            except Exception as e:
                logger.error(f"[FileWatcherIndexIntegration] Version record error: {e}")

        return success

    async def on_file_modified(self, file_path: str) -> bool:
        """文件修改时触发索引"""
        logger.info(f"[FileWatcherIndexIntegration] File modified: {file_path}")

        # 记录版本
        if self._version_control:
            try:
                self._version_control.record_version(
                    file_path,
                    comment="Auto-saved from modification"
                )
            except Exception as e:
                logger.error(f"[FileWatcherIndexIntegration] Version record error: {e}")

        # 重新索引
        return await self._auto_indexer.index_file(file_path)

    async def on_file_deleted(self, file_path: str) -> bool:
        """文件删除时处理"""
        logger.info(f"[FileWatcherIndexIntegration] File deleted: {file_path}")

        # GraphRAG 不支持删除单个文件索引
        logger.info(
            f"[FileWatcherIndexIntegration] GraphRAG single-file deletion "
            f"not supported, manual cleanup may be required for: {file_path}"
        )
        return True

    def get_integration_handlers(self) -> Dict[str, Callable]:
        """
        获取集成处理器（供 FileWatcher 使用）

        Returns:
            Dict[str, Callable]: 事件类型到处理函数的映射
        """
        return {
            "created": lambda path: asyncio.create_task(self.on_file_created(path)),
            "modified": lambda path: asyncio.create_task(self.on_file_modified(path)),
            "deleted": lambda path: asyncio.create_task(self.on_file_deleted(path)),
        }


# ============================================================================
# 查询增强
# ============================================================================

class QueryEnhancer:
    """
    查询增强器

    提供更强大的 GraphRAG 查询能力
    """

    def __init__(self, graphrag_service_url: Optional[str] = None):
        self._graphrag_url = graphrag_service_url or config.graphrag.service_url

    async def query_with_context(
        self,
        query: str,
        context_files: List[str],
        session_id: str = "default",
    ) -> dict:
        """
        带上下文的查询

        在查询前注入相关文件内容作为上下文

        Args:
            query: 查询文本
            context_files: 上下文文件路径列表
            session_id: 会话 ID

        Returns:
            dict: 查询结果
        """
        import httpx

        # 构建上下文
        context_parts = []
        for file_path in context_files:
            try:
                content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                context_parts.append(f"=== {Path(file_path).name} ===\n{content[:2000]}")
            except Exception as e:
                logger.error(f"[QueryEnhancer] Failed to read context file {file_path}: {e}")

        context = "\n\n".join(context_parts)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._graphrag_url}/api/v1/query/",
                json={
                    "query": query,
                    "session_id": session_id,
                    "context": context,
                }
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Query failed: HTTP {response.status_code}"}

    async def query_multi_hop(
        self,
        query: str,
        session_id: str = "default",
    ) -> dict:
        """
        多跳查询

        执行多步推理查询

        Args:
            query: 查询文本
            session_id: 会话 ID

        Returns:
            dict: 多跳查询结果
        """
        import httpx

        # 先进行本地查询
        async with httpx.AsyncClient(timeout=60.0) as client:
            local_response = await client.post(
                f"{self._graphrag_url}/api/v1/query/",
                json={
                    "query": query,
                    "session_id": session_id,
                    "top_k": 10,
                }
            )

            if local_response.status_code != 200:
                return {"error": f"Local query failed: {local_response.status_code}"}

            local_result = local_response.json()

            # 如果本地结果不足，进行全局查询
            if len(local_result.get('sources', [])) < 3:
                global_response = await client.post(
                    f"{self._graphrag_url}/api/v1/query/",
                    json={
                        "query": query,
                        "session_id": session_id,
                        "method": "global",
                    }
                )

                if global_response.status_code == 200:
                    global_result = global_response.json()
                    # 合并结果
                    local_result['sources'].extend(global_result.get('sources', []))
                    local_result['answer'] = (
                        local_result.get('answer', '') +
                        "\n\n---\n\n[Global Context]\n" +
                        global_result.get('answer', '')
                    )

            return local_result


# ============================================================================
# 全局实例管理
# ============================================================================

_global_state_manager: Optional[IndexStateManager] = None
_global_auto_indexer: Optional[AutoIndexer] = None
_global_file_watcher_integration: Optional[FileWatcherIndexIntegration] = None
_global_query_enhancer: Optional[QueryEnhancer] = None


def get_index_state_manager() -> IndexStateManager:
    """获取索引状态管理器"""
    global _global_state_manager
    if _global_state_manager is None:
        _global_state_manager = IndexStateManager()
    return _global_state_manager


def get_auto_indexer() -> AutoIndexer:
    """获取自动索引器"""
    global _global_auto_indexer
    if _global_auto_indexer is None:
        _global_auto_indexer = AutoIndexer(state_manager=get_index_state_manager())
    return _global_auto_indexer


def get_file_watcher_integration(
    version_control: Optional[Any] = None,
) -> FileWatcherIndexIntegration:
    """获取 FileWatcher 集成实例"""
    global _global_file_watcher_integration
    if _global_file_watcher_integration is None:
        _global_file_watcher_integration = FileWatcherIndexIntegration(
            auto_indexer=get_auto_indexer(),
            version_control=version_control,
        )
    return _global_file_watcher_integration


def get_query_enhancer() -> QueryEnhancer:
    """获取查询增强器"""
    global _global_query_enhancer
    if _global_query_enhancer is None:
        _global_query_enhancer = QueryEnhancer()
    return _global_query_enhancer