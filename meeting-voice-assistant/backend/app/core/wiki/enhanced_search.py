"""
LLMWiki 增强 - 搜索和知识关联

功能：
- Wiki 搜索增强（结合 GraphRAG 语义搜索）
- 零散文件关联
- 知识图谱增强查询
"""

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
import hashlib

from app.config import config
from app.storage.wiki_db import get_wiki_db, WikiDatabase

logger = logging.getLogger("wiki.enhanced_search")


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class SearchResult:
    """搜索结果"""
    result_type: str  # 'page', 'entity', 'file', 'task', 'workflow'
    id: str
    title: str
    snippet: str
    relevance_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeGraph:
    """知识图谱"""
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    communities: List[Dict[str, Any]] = field(default_factory=list)


# ============================================================================
# 增强搜索服务
# ============================================================================

class EnhancedWikiSearch:
    """
    增强 Wiki 搜索

    结合：
    - 传统数据库全文搜索
    - GraphRAG 语义搜索
    - 实体关联搜索
    """

    def __init__(self, wiki_db: Optional[WikiDatabase] = None):
        self._db = wiki_db or get_wiki_db()
        self._graphrag_url = config.graphrag.service_url
        self._search_cache: Dict[str, List[SearchResult]] = {}
        self._cache_ttl = 300  # 5 分钟缓存

    async def search(
        self,
        query: str,
        search_types: Optional[List[str]] = None,
        category_id: Optional[str] = None,
        limit: int = 20,
        use_semantic: bool = True,
    ) -> List[SearchResult]:
        """
        增强搜索

        Args:
            query: 搜索关键词
            search_types: 搜索类型 ['page', 'entity', 'file', 'task', 'workflow']
            category_id: 分类过滤
            limit: 返回结果数量
            use_semantic: 是否使用语义搜索

        Returns:
            List[SearchResult]: 搜索结果列表
        """
        if search_types is None:
            search_types = ['page', 'entity', 'file', 'task']

        results: List[SearchResult] = []
        seen_ids: Set[str] = set()

        # 1. 数据库全文搜索
        if 'page' in search_types:
            page_results = await self._search_pages(query, category_id, limit)
            for r in page_results:
                if r.id not in seen_ids:
                    results.append(r)
                    seen_ids.add(r.id)

        # 2. GraphRAG 语义搜索
        if use_semantic and 'page' in search_types:
            semantic_results = await self._search_semantic(query, limit)
            for r in semantic_results:
                if r.id not in seen_ids:
                    results.append(r)
                    seen_ids.add(r.id)

        # 3. 实体搜索
        if 'entity' in search_types:
            entity_results = await self._search_entities(query, limit)
            for r in entity_results:
                if r.id not in seen_ids:
                    results.append(r)
                    seen_ids.add(r.id)

        # 4. 任务搜索
        if 'task' in search_types:
            task_results = await self._search_tasks(query, limit)
            for r in task_results:
                if r.id not in seen_ids:
                    results.append(r)
                    seen_ids.add(r.id)

        # 按相关性排序
        results.sort(key=lambda r: r.relevance_score, reverse=True)

        return results[:limit]

    async def _search_pages(
        self,
        query: str,
        category_id: Optional[str],
        limit: int,
    ) -> List[SearchResult]:
        """数据库搜索 Wiki 页面"""
        results = []

        try:
            db_results = self._db.search_pages(query, category_id, limit)
            for r in db_results:
                results.append(SearchResult(
                    result_type='page',
                    id=r['id'],
                    title=r['title'],
                    snippet=r.get('snippet', ''),
                    relevance_score=0.8,
                    metadata={
                        'slug': r.get('slug'),
                        'category_id': r.get('category_id'),
                        'updated_at': r.get('updated_at'),
                    }
                ))
        except Exception as e:
            logger.error(f"[EnhancedWikiSearch] Page search error: {e}")

        return results

    async def _search_semantic(self, query: str, limit: int) -> List[SearchResult]:
        """GraphRAG 语义搜索"""
        results = []

        try:
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self._graphrag_url}/api/v1/query/",
                    json={
                        "query": query,
                        "session_id": "default",
                        "top_k": limit,
                    }
                )

                if response.status_code == 200:
                    data = response.json()

                    # 解析 GraphRAG 结果
                    for item in data.get('sources', []):
                        results.append(SearchResult(
                            result_type='page',
                            id=item.get('doc_id', ''),
                            title=item.get('title', 'Untitled'),
                            snippet=item.get('chunk', '')[:200],
                            relevance_score=0.9,
                            metadata=item,
                        ))
        except Exception as e:
            logger.error(f"[EnhancedWikiSearch] Semantic search error: {e}")

        return results

    async def _search_entities(self, query: str, limit: int) -> List[SearchResult]:
        """搜索实体"""
        results = []

        try:
            # 从数据库搜索实体
            from app.storage.database import search_entities
            entities = await search_entities(query, limit)

            for ent in entities:
                results.append(SearchResult(
                    result_type='entity',
                    id=ent.get('entity_id', ''),
                    title=ent.get('name', ''),
                    snippet=ent.get('description', '')[:200],
                    relevance_score=0.7,
                    metadata={
                        'entity_type': ent.get('entity_type'),
                        'community_id': ent.get('community_id'),
                    }
                ))
        except Exception as e:
            logger.error(f"[EnhancedWikiSearch] Entity search error: {e}")

        return results

    async def _search_tasks(self, query: str, limit: int) -> List[SearchResult]:
        """搜索任务"""
        results = []

        try:
            tasks = self._db.get_tracked_tasks(status=None)

            # 简单过滤（实际应该用全文搜索）
            query_lower = query.lower()
            for task in tasks:
                title = task.get('title', '').lower()
                if query_lower in title or query_lower in task.get('description', '').lower():
                    results.append(SearchResult(
                        result_type='task',
                        id=task.get('id', ''),
                        title=task.get('title', ''),
                        snippet=task.get('description', '')[:200],
                        relevance_score=0.6,
                        metadata={
                            'status': task.get('status'),
                            'priority': task.get('priority'),
                            'assignee': task.get('assignee'),
                        }
                    ))

                if len(results) >= limit:
                    break
        except Exception as e:
            logger.error(f"[EnhancedWikiSearch] Task search error: {e}")

        return results

    async def get_related_content(
        self,
        content_id: str,
        content_type: str = 'page',
        depth: int = 1,
    ) -> List[SearchResult]:
        """
        获取相关内容（知识关联）

        Args:
            content_id: 内容 ID
            content_type: 内容类型 ('page', 'entity', 'file')
            depth: 关联深度

        Returns:
            List[SearchResult]: 关联内容列表
        """
        results = []

        try:
            if content_type == 'page':
                # 获取页面关联的实体
                entities = self._db.get_page_entities(content_id)
                for ent in entities:
                    results.append(SearchResult(
                        result_type='entity',
                        id=ent.get('id', ''),
                        title=ent.get('name', ''),
                        snippet=ent.get('description', '')[:200],
                        relevance_score=0.8,
                        metadata={'entity_type': ent.get('entity_type')},
                    ))

                # 获取页面关联的任务
                tasks = self._db.get_tracked_tasks(page_id=content_id)
                for task in tasks:
                    results.append(SearchResult(
                        result_type='task',
                        id=task.get('id', ''),
                        title=task.get('title', ''),
                        snippet=task.get('description', '')[:200],
                        relevance_score=0.7,
                        metadata={'status': task.get('status')},
                    ))

                # 获取页面关联的工作流
                workflows = self._db.get_page_workflows(content_id)
                for wf in workflows:
                    results.append(SearchResult(
                        result_type='workflow',
                        id=wf.get('id', ''),
                        title=wf.get('name', ''),
                        snippet=wf.get('description', '')[:200],
                        relevance_score=0.6,
                        metadata={'workflow_type': wf.get('workflow_type')},
                    ))

            elif content_type == 'entity':
                # 获取实体关联的关系
                from app.storage.database import get_entity_relationships
                relations = await get_entity_relationships(content_id)
                for rel in relations:
                    results.append(SearchResult(
                        result_type='entity',
                        id=rel.get('target_entity_id', ''),
                        title=rel.get('target_entity_id', ''),
                        snippet=rel.get('description', '')[:200],
                        relevance_score=0.8,
                        metadata={'relation_type': rel.get('relation_type')},
                    ))

        except Exception as e:
            logger.error(f"[EnhancedWikiSearch] Related content error: {e}")

        return results


# ============================================================================
# 知识关联分析器
# ============================================================================

class KnowledgeAssociator:
    """
    知识关联分析器

    分析零散文件之间的关联，生成知识网络
    """

    def __init__(self):
        self._association_cache: Dict[str, List[Dict[str, Any]]] = {}

    def find_associations(
        self,
        source_content: str,
        source_title: str,
        target_files: List[str],
    ) -> List[Dict[str, Any]]:
        """
        查找源内容与目标文件之间的关联

        Args:
            source_content: 源内容
            source_title: 源标题
            target_files: 目标文件路径列表

        Returns:
            List[Dict[str, Any]]: 关联列表
        """
        associations = []

        # 提取源内容的关键词
        source_keywords = self._extract_keywords(source_content)

        for file_path in target_files:
            try:
                # 读取目标文件
                content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
                target_keywords = self._extract_keywords(content)

                # 计算相似度
                similarity = self._calculate_similarity(source_keywords, target_keywords)

                if similarity > 0.3:  # 阈值
                    associations.append({
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'similarity': similarity,
                        'shared_keywords': list(source_keywords & target_keywords),
                        'association_type': self._classify_association(source_keywords, target_keywords),
                    })
            except Exception as e:
                logger.error(f"[KnowledgeAssociator] Failed to analyze {file_path}: {e}")

        # 按相似度排序
        associations.sort(key=lambda x: x['similarity'], reverse=True)
        return associations

    def _extract_keywords(self, content: str) -> Set[str]:
        """提取关键词"""
        # 简单分词
        words = re.findall(r'\b\w{3,}\b', content.lower())

        # 停用词
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'this',
            'that', 'with', 'have', 'from', 'they', 'been', 'have',
            'been', 'were', 'said', 'each', 'she', 'which', 'their',
        }

        # 过滤停用词和短词
        keywords = {w for w in words if w not in stop_words}

        # 提取重要的词组
        phrases = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content)
        keywords.update(p.lower() for p in phrases)

        return keywords

    def _calculate_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """计算集合相似度 (Jaccard)"""
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def _classify_association(
        self,
        keywords1: Set[str],
        keywords2: Set[str],
    ) -> str:
        """分类关联类型"""
        shared = keywords1 & keywords2

        # 基于共享关键词分类
        if any(w in shared for w in {'project', 'task', 'deadline', 'milestone'}):
            return 'project_related'
        elif any(w in shared for w in {'meeting', 'discuss', 'action', 'decision'}):
            return 'meeting_related'
        elif any(w in shared for w in {'code', 'bug', 'feature', 'refactor'}):
            return 'development_related'
        elif any(w in shared for w in {'design', 'ui', 'ux', 'prototype'}):
            return 'design_related'
        else:
            return 'general_related'


# ============================================================================
# 全局实例
# ============================================================================

_global_search: Optional[EnhancedWikiSearch] = None
_global_associator: Optional[KnowledgeAssociator] = None


def get_enhanced_wiki_search() -> EnhancedWikiSearch:
    """获取增强搜索实例"""
    global _global_search
    if _global_search is None:
        _global_search = EnhancedWikiSearch()
    return _global_search


def get_knowledge_associator() -> KnowledgeAssociator:
    """获取知识关联器实例"""
    global _global_associator
    if _global_associator is None:
        _global_associator = KnowledgeAssociator()
    return _global_associator