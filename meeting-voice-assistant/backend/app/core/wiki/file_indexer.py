"""
Wiki-GraphRAG 文件索引器

功能：
- 零散文件信息提取
- Wiki 页面自动同步到 GraphRAG 索引
- 多文件关联索引
- 与 file_watcher 集成实现自动同步
"""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Callable, Awaitable
from dataclasses import dataclass, field
import hashlib
import json

from app.config import config
from app.storage.wiki_db import get_wiki_db, WikiDatabase

logger = logging.getLogger("wiki.file_indexer")


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class FileInfo:
    """文件信息"""
    file_path: str
    content: str
    file_type: str
    extracted_entities: List[Dict[str, Any]] = field(default_factory=list)
    extracted_relations: List[Dict[str, Any]] = field(default_factory=list)
    extracted_tasks: List[Dict[str, Any]] = field(default_factory=list)
    last_modified: datetime = field(default_factory=datetime.now)
    content_hash: str = ""


@dataclass
class IndexSyncResult:
    """索引同步结果"""
    success: bool
    synced_files: int = 0
    new_entities: int = 0
    updated_entities: int = 0
    errors: List[str] = field(default_factory=list)


# ============================================================================
# 零散文件信息提取器
# ============================================================================

class ScatteredFileExtractor:
    """
    零散文件信息提取器

    从各种格式的文件中提取结构化信息：
    - 实体（人物、组织、项目、任务等）
    - 关系（实体之间的关联）
    - 任务（行动项、待办事项等）
    """

    # 支持的文件类型
    SUPPORTED_TYPES = {
        '.txt', '.md', '.markdown',
        '.json', '.jsonl',
        '.csv',
        '.yaml', '.yml',
        '.xml',
        '.eml', '.msg',
    }

    # 实体模式（用于正则提取）
    ENTITY_PATTERNS = {
        # 项目名称 (#123, PROJECT-NAME, etc.)
        'project': re.compile(r'(?:^|[\s\(\[])([A-Z][A-Z0-9]+-[0-9]+|PROJECT-[A-Z]+)(?:[\s\)\]]|$)'),
        # 邮箱
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        # URL
        'url': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
        # 日期
        'date': re.compile(r'\d{4}[-/]\d{2}[-/]\d{2}'),
        # 版本号
        'version': re.compile(r'\bv?(\d+\.)+\d+\b'),
        # 任务引用 [TODO-123], #123
        'task_ref': re.compile(r'(?:\[([A-Z]+-[0-9]+)\]|#(\d+))'),
    }

    # 任务模式
    TASK_PATTERNS = [
        re.compile(r'[-*]\s*\[ \]\s*(.+)'),  # - [ ] Task
        re.compile(r'[-*]\s*\[x\]\s*(.+)'),  # - [x] Completed task
        re.compile(r'(?:TODO|FIXME|HACK|XXX):\s*(.+)', re.IGNORECASE),
        re.compile(r'@task\s+(.+)', re.IGNORECASE),
        re.compile(r'@action\s+(.+)', re.IGNORECASE),
    ]

    def __init__(self):
        self._entity_cache: Dict[str, List[Dict[str, Any]]] = {}

    def can_extract(self, file_path: str) -> bool:
        """检查是否支持提取该文件"""
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_TYPES

    def extract(self, file_path: str, content: Optional[str] = None) -> FileInfo:
        """
        从文件中提取信息

        Args:
            file_path: 文件路径
            content: 文件内容（如果为 None，从文件读取）

        Returns:
            FileInfo: 提取的文件信息
        """
        path = Path(file_path)
        file_type = path.suffix.lower()

        # 读取内容
        if content is None:
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
            except Exception as e:
                logger.warning(f"[ScatteredFileExtractor] Failed to read {file_path}: {e}")
                content = ""

        # 计算 hash
        content_hash = hashlib.md5(content.encode()).hexdigest()

        # 提取实体
        entities = self._extract_entities(content)

        # 提取关系
        relations = self._extract_relations(content, entities)

        # 提取任务
        tasks = self._extract_tasks(content)

        # 获取最后修改时间
        last_modified = datetime.fromtimestamp(path.stat().st_mtime) if path.exists() else datetime.now()

        return FileInfo(
            file_path=str(path),
            content=content,
            file_type=file_type,
            extracted_entities=entities,
            extracted_relations=relations,
            extracted_tasks=tasks,
            last_modified=last_modified,
            content_hash=content_hash,
        )

    def _extract_entities(self, content: str) -> List[Dict[str, Any]]:
        """提取实体"""
        entities = []

        for entity_type, pattern in self.ENTITY_PATTERNS.items():
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1] if match[1] else ""
                if match:
                    entities.append({
                        "name": match.strip(),
                        "type": entity_type,
                        "source": "pattern",
                    })

        # 去重
        seen = set()
        unique_entities = []
        for ent in entities:
            key = (ent["name"], ent["type"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(ent)

        return unique_entities

    def _extract_relations(self, content: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取关系"""
        relations = []

        # 从实体列表中提取共现关系
        entity_names = [e["name"] for e in entities[:20]]  # 限制数量

        # 简单的共现检测：如果两个实体在同一段落中出现，认为有关系
        lines = content.split('\n\n')
        for line in lines:
            line_entities = []
            for name in entity_names:
                if name in line:
                    line_entities.append(name)

            # 同一段落中的实体对有关系
            for i, e1 in enumerate(line_entities):
                for e2 in line_entities[i+1:]:
                    relations.append({
                        "source": e1,
                        "target": e2,
                        "type": "co_occurrence",
                        "context": line.strip()[:100],
                    })

        return relations

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """提取任务"""
        tasks = []

        for pattern in self.TASK_PATTERNS:
            matches = pattern.findall(content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else ""
                if match:
                    tasks.append({
                        "title": match.strip(),
                        "status": "pending" if "[ ]" in match else "completed",
                        "source": "pattern",
                    })

        return tasks


# ============================================================================
# Wiki 索引同步器
# ============================================================================

class WikiIndexer:
    """
    Wiki 索引同步器

    功能：
    - Wiki 页面内容自动同步到 GraphRAG
    - 文件变更自动触发索引更新
    - 多文件关联索引
    """

    def __init__(
        self,
        wiki_db: Optional[WikiDatabase] = None,
        graphrag_service_url: Optional[str] = None,
    ):
        self._db = wiki_db or get_wiki_db()
        self._graphrag_url = graphrag_service_url or config.graphrag.service_url
        self._extractor = ScatteredFileExtractor()
        self._sync_callbacks: List[Callable[[str, FileInfo], Awaitable[None]]] = []

    def add_sync_callback(self, callback: Callable[[str, FileInfo], Awaitable[None]]):
        """添加同步回调函数"""
        self._sync_callbacks.append(callback)

    async def index_wiki_page(self, page_id: str) -> bool:
        """
        索引 Wiki 页面到 GraphRAG

        Args:
            page_id: Wiki 页面 ID

        Returns:
            bool: 是否成功
        """
        import httpx

        page = self._db.get_page(page_id)
        if not page:
            logger.warning(f"[WikiIndexer] Page not found: {page_id}")
            return False

        try:
            # 构建索引内容
            content = f"# {page['title']}\n\n{page['content']}"

            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                prefix=f'wiki_{page_id}_',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(content)
                temp_path = f.name

            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(temp_path, 'rb') as f:
                    files = {'doc': (f'{page_id}_wiki.txt', f, 'text/plain')}
                    response = await client.post(
                        f"{self._graphrag_url}/api/v1/index/",
                        files=files
                    )

            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)

            if response.status_code == 200:
                logger.info(f"[WikiIndexer] Indexed page: {page_id}")
                return True
            else:
                logger.error(f"[WikiIndexer] Index failed for {page_id}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"[WikiIndexer] Index error for {page_id}: {e}")
            return False

    async def index_file(self, file_path: str, content: Optional[str] = None) -> bool:
        """
        索引单个文件到 GraphRAG

        Args:
            file_path: 文件路径
            content: 文件内容（可选）

        Returns:
            bool: 是否成功
        """
        import httpx

        if not self._extractor.can_extract(file_path):
            logger.debug(f"[WikiIndexer] Unsupported file type: {file_path}")
            return False

        try:
            # 提取文件信息
            file_info = self._extractor.extract(file_path, content)

            # 构建索引内容
            index_content = self._build_index_content(file_info)

            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.txt',
                prefix=f'file_{Path(file_path).stem}_',
                delete=False,
                encoding='utf-8'
            ) as f:
                f.write(index_content)
                temp_path = f.name

            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(temp_path, 'rb') as f:
                    files = {'doc': (Path(file_path).name, f, 'text/plain')}
                    response = await client.post(
                        f"{self._graphrag_url}/api/v1/index/",
                        files=files
                    )

            # 清理临时文件
            Path(temp_path).unlink(missing_ok=True)

            if response.status_code == 200:
                logger.info(f"[WikiIndexer] Indexed file: {file_path}")

                # 调用同步回调
                for callback in self._sync_callbacks:
                    try:
                        await callback(file_path, file_info)
                    except Exception as e:
                        logger.error(f"[WikiIndexer] Sync callback error: {e}")

                return True
            else:
                logger.error(f"[WikiIndexer] Index failed for {file_path}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"[WikiIndexer] Index error for {file_path}: {e}")
            return False

    def _build_index_content(self, file_info: FileInfo) -> str:
        """构建索引内容"""
        lines = [
            f"# File: {Path(file_info.file_path).name}",
            f"Path: {file_info.file_path}",
            f"Type: {file_info.file_type}",
            "",
        ]

        # 添加提取的实体
        if file_info.extracted_entities:
            lines.append("## Entities")
            for ent in file_info.extracted_entities[:50]:  # 限制数量
                lines.append(f"- {ent['name']} ({ent['type']})")
            lines.append("")

        # 添加提取的任务
        if file_info.extracted_tasks:
            lines.append("## Tasks")
            for task in file_info.extracted_tasks[:50]:
                status = "TODO" if task.get("status") == "pending" else "DONE"
                lines.append(f"- [{status}] {task['title']}")
            lines.append("")

        # 添加原始内容摘要
        lines.append("## Content")
        lines.append(file_info.content[:5000])  # 限制长度

        return "\n".join(lines)

    async def index_multiple_files(self, file_paths: List[str]) -> IndexSyncResult:
        """
        批量索引多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            IndexSyncResult: 索引结果
        """
        result = IndexSyncResult(success=True)

        for file_path in file_paths:
            try:
                if await self.index_file(file_path):
                    result.synced_files += 1
                else:
                    result.errors.append(f"Failed to index: {file_path}")
            except Exception as e:
                result.errors.append(f"Error indexing {file_path}: {e}")

        result.success = len(result.errors) == 0
        return result

    async def sync_all_wiki_pages(self) -> IndexSyncResult:
        """
        同步所有 Wiki 页面到 GraphRAG

        Returns:
            IndexSyncResult: 同步结果
        """
        result = IndexSyncResult(success=True)

        try:
            # 获取所有 Wiki 页面
            pages, total = self._db.list_pages(page=1, page_size=1000, include_unpublished=True)

            for page in pages:
                try:
                    if await self.index_wiki_page(page["id"]):
                        result.synced_files += 1
                    else:
                        result.errors.append(f"Failed to index page: {page['id']}")
                except Exception as e:
                    result.errors.append(f"Error indexing page {page['id']}: {e}")

            result.success = len(result.errors) == 0

        except Exception as e:
            result.success = False
            result.errors.append(f"Sync error: {e}")

        return result


# ============================================================================
# 文件变更监听器集成
# ============================================================================

class WikiFileWatcherIntegration:
    """
    Wiki 与 FileWatcher 集成

    当 file_watcher 检测到文件变化时，自动同步到 Wiki 和 GraphRAG
    """

    def __init__(
        self,
        wiki_indexer: Optional[WikiIndexer] = None,
        version_control: Optional[Any] = None,
    ):
        self._indexer = wiki_indexer or WikiIndexer()
        self._version_control = version_control

    async def on_file_created(self, file_path: str) -> bool:
        """文件创建时处理"""
        logger.info(f"[WikiFileWatcherIntegration] File created: {file_path}")

        # 索引新文件
        success = await self._indexer.index_file(file_path)

        # 记录版本
        if self._version_control and success:
            try:
                self._version_control.record_version(file_path, comment="Initial version")
            except Exception as e:
                logger.error(f"[WikiFileWatcherIntegration] Failed to record version: {e}")

        return success

    async def on_file_modified(self, file_path: str) -> bool:
        """文件修改时处理"""
        logger.info(f"[WikiFileWatcherIntegration] File modified: {file_path}")

        # 记录版本
        if self._version_control:
            try:
                self._version_control.record_version(file_path, comment="Auto-saved")
            except Exception as e:
                logger.error(f"[WikiFileWatcherIntegration] Failed to record version: {e}")

        # 重新索引
        return await self._indexer.index_file(file_path)

    async def on_file_deleted(self, file_path: str) -> bool:
        """文件删除时处理"""
        logger.info(f"[WikiFileWatcherIntegration] File deleted: {file_path}")

        # GraphRAG 不支持删除单个文件索引，仅记录日志
        logger.info(f"[WikiFileWatcherIntegration] GraphRAG auto-cleanup not supported for: {file_path}")
        return True


# ============================================================================
# 全局实例
# ============================================================================

_global_indexer: Optional[WikiIndexer] = None


def get_wiki_indexer() -> WikiIndexer:
    """获取全局 WikiIndexer 实例"""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = WikiIndexer()
    return _global_indexer


def get_wiki_file_watcher_integration(
    version_control: Optional[Any] = None,
) -> WikiFileWatcherIntegration:
    """获取 Wiki-FileWatcher 集成实例"""
    return WikiFileWatcherIntegration(
        wiki_indexer=get_wiki_indexer(),
        version_control=version_control,
    )