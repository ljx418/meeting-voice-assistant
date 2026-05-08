"""LLMWiki 搜索层 - FTS5 全文搜索"""
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..models import Passage, WikiPage


@dataclass
class SearchResult:
    """搜索结果"""
    result_id: str  # page slug 或 passage_id
    result_type: str  # "page" 或 "passage"
    title: str
    snippet: str
    score: float
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    """搜索响应"""
    query: str
    pages: List[SearchResult]  # 页面级别命中
    passages: List[SearchResult]  # 段落级别命中
    total_pages: int
    total_passages: int


class FTS5Search:
    """FTS5 全文搜索"""

    def __init__(self, db_path: Path):
        """初始化 FTS5 搜索

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path
        self._ensure_fts_tables()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_fts_tables(self) -> None:
        """确保 FTS5 表存在"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                slug,
                title,
                summary,
                body_md
            )
            """
        )
        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(
                passage_id,
                source_id,
                text,
                cjk_terms
            )
            """
        )

        conn.commit()
        conn.close()

    def search_pages(self, query: str, limit: int = 10) -> List[SearchResult]:
        """搜索页面

        Args:
            query: 搜索查询
            limit: 返回结果数量

        Returns:
            页面搜索结果
        """
        if not query or not query.strip():
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        # FTS5 搜索 - 处理中文和英文
        search_query = self._prepare_fts_query(query)

        try:
            cursor.execute("""
                SELECT
                    p.slug,
                    p.title,
                    p.summary,
                    p.body_md,
                    bm25(pages_fts) as rank,
                    snippet(pages_fts, 1, '<mark>', '</mark>', '...', 30) as snippet
                FROM pages_fts
                JOIN pages p ON pages_fts.slug = p.slug
                WHERE pages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (search_query, limit))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(SearchResult(
                    result_id=row["slug"],
                    result_type="page",
                    title=row["title"] or row["slug"],
                    snippet=row["snippet"] or (row["summary"] or "")[:200],
                    score=abs(row["rank"]) if row["rank"] else 0.0,
                    meta={"slug": row["slug"]},
                ))

            return results
        except sqlite3.Error:
            # FTS 查询失败，尝试 LIKE 降级
            return self._fallback_page_search(query, limit)
        finally:
            conn.close()

    def search_passages(self, query: str, limit: int = 20) -> List[SearchResult]:
        """搜索段落

        Args:
            query: 搜索查询
            limit: 返回结果数量

        Returns:
            段落搜索结果
        """
        if not query or not query.strip():
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        search_query = self._prepare_fts_query(query)

        try:
            cursor.execute("""
                SELECT
                    p.passage_id,
                    p.source_id,
                    p.text,
                    p.locator,
                    bm25(passages_fts) as rank,
                    snippet(passages_fts, 2, '<mark>', '</mark>', '...', 30) as snippet
                FROM passages_fts
                JOIN passages p ON passages_fts.passage_id = p.passage_id
                WHERE passages_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (search_query, limit))

            rows = cursor.fetchall()
            results = []
            for row in rows:
                results.append(SearchResult(
                    result_id=row["passage_id"],
                    result_type="passage",
                    title=f"Passage {row['passage_id'][:8]}",
                    snippet=row["snippet"] or row["text"][:200],
                    score=abs(row["rank"]) if row["rank"] else 0.0,
                    meta={
                        "passage_id": row["passage_id"],
                        "source_id": row["source_id"],
                        "locator": row["locator"],
                    },
                ))

            return results
        except sqlite3.Error:
            return self._fallback_passage_search(query, limit)
        finally:
            conn.close()

    def search_hybrid(
        self,
        query: str,
        page_limit: int = 10,
        passage_limit: int = 20,
    ) -> SearchResponse:
        """混合搜索 - 先查 pages 再查 passages

        Args:
            query: 搜索查询
            page_limit: 页面结果限制
            passage_limit: 段落结果限制

        Returns:
            搜索响应
        """
        page_results = self.search_pages(query, page_limit)
        passage_results = self.search_passages(query, passage_limit)

        return SearchResponse(
            query=query,
            pages=page_results,
            passages=passage_results,
            total_pages=len(page_results),
            total_passages=len(passage_results),
        )

    def _prepare_fts_query(self, query: str) -> str:
        """准备 FTS 查询字符串

        Args:
            query: 原始查询

        Returns:
            FTS5 查询字符串
        """
        # 转义特殊字符
        query = query.replace('"', '""')

        # 如果包含空格，转换为 OR 查询
        terms = query.split()
        if len(terms) > 1:
            # 使用 OR 连接多个词
            return " OR ".join(f'"{t}"' for t in terms if t)

        return f'"{query}"'

    def _fallback_page_search(self, query: str, limit: int) -> List[SearchResult]:
        """页面搜索降级 - 使用 LIKE"""
        conn = self._get_connection()
        cursor = conn.cursor()

        pattern = f"%{query}%"
        cursor.execute("""
            SELECT slug, title, summary, body_md
            FROM pages
            WHERE title LIKE ? OR summary LIKE ? OR body_md LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """, (pattern, pattern, pattern, limit))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            snippet = self._generate_snippet(row["body_md"] or row["summary"] or "", query)
            results.append(SearchResult(
                result_id=row["slug"],
                result_type="page",
                title=row["title"] or row["slug"],
                snippet=snippet,
                score=1.0,  # 降级搜索不给高分
                meta={"slug": row["slug"], "fallback": True},
            ))

        conn.close()
        return results

    def _fallback_passage_search(self, query: str, limit: int) -> List[SearchResult]:
        """段落搜索降级 - 使用 LIKE"""
        conn = self._get_connection()
        cursor = conn.cursor()

        pattern = f"%{query}%"
        cursor.execute("""
            SELECT passage_id, source_id, text, locator
            FROM passages
            WHERE text LIKE ?
            ORDER BY order_index
            LIMIT ?
        """, (pattern, limit))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            snippet = self._generate_snippet(row["text"], query)
            results.append(SearchResult(
                result_id=row["passage_id"],
                result_type="passage",
                title=f"Passage {row['passage_id'][:8]}",
                snippet=snippet,
                score=1.0,
                meta={
                    "passage_id": row["passage_id"],
                    "source_id": row["source_id"],
                    "locator": row["locator"],
                    "fallback": True,
                },
            ))

        conn.close()
        return results

    def _generate_snippet(self, text: str, query: str, max_length: int = 200) -> str:
        """生成搜索结果片段"""
        if not text:
            return ""

        query_lower = query.lower()
        text_lower = text.lower()

        # 查找查询词位置
        pos = text_lower.find(query_lower)
        if pos == -1:
            # 没找到，返回开头
            return text[:max_length] + "..." if len(text) > max_length else text

        # 在查询词附近截取
        start = max(0, pos - 50)
        end = min(len(text), pos + len(query) + 150)

        snippet = text[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def rebuild_fts_index(self) -> dict:
        """重建 FTS 索引

        Returns:
            重建统计
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 删除并重新创建 FTS 表
        cursor.execute("DROP TABLE IF EXISTS pages_fts")
        cursor.execute("DROP TABLE IF EXISTS passages_fts")
        conn.commit()
        conn.close()

        # 重新初始化
        self._ensure_fts_tables()

        # 重新填充数据
        self._repopulate_fts()

        return {"status": "rebuilt"}

    def _repopulate_fts(self) -> None:
        """重新填充 FTS 表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 填充 pages
        cursor.execute("""
            INSERT INTO pages_fts(slug, title, summary, body_md)
            SELECT slug, title, summary, body_md FROM pages
        """)

        # 填充 passages
        cursor.execute("""
            INSERT INTO passages_fts(passage_id, source_id, text, cjk_terms)
            SELECT passage_id, source_id, text, cjk_terms FROM passages
        """)

        conn.commit()
        conn.close()

    def search_with_cjk(self, query: str, limit: int = 10) -> List[SearchResult]:
        """中文分词搜索（基础版）

        对于中文查询，同时搜索 cjk_terms 字段

        Args:
            query: 搜索查询
            limit: 结果数量

        Returns:
            搜索结果
        """
        # 判断是否包含中文
        has_cjk = bool(re.search(r'[\u4e00-\u9fff]', query))

        if not has_cjk:
            return self.search_pages(query, limit)

        conn = self._get_connection()
        cursor = conn.cursor()

        # 提取查询中的中文词
        cjk_terms = re.findall(r'[\u4e00-\u9fff]+', query)

        results = self.search_pages(query, limit)

        # 如果没有结果，尝试用单个字符搜索
        if not results and len(cjk_terms) > 0:
            for term in cjk_terms:
                if len(term) >= 2:
                    term_results = self._search_by_cjk_term(term, limit)
                    results.extend(term_results)

        conn.close()
        return results[:limit]

    def _search_by_cjk_term(self, term: str, limit: int) -> List[SearchResult]:
        """按 CJK 词搜索"""
        conn = self._get_connection()
        cursor = conn.cursor()

        pattern = f"%{term}%"
        cursor.execute("""
            SELECT slug, title, summary, body_md
            FROM pages
            WHERE title LIKE ? OR summary LIKE ? OR body_md LIKE ?
            ORDER BY updated_at DESC
            LIMIT ?
        """, (pattern, pattern, pattern, limit))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            snippet = self._generate_snippet(row["body_md"] or row["summary"] or "", term)
            results.append(SearchResult(
                result_id=row["slug"],
                result_type="page",
                title=row["title"] or row["slug"],
                snippet=snippet,
                score=0.8,  # CJK 搜索降权
                meta={"slug": row["slug"], "cjk_match": True},
            ))

        conn.close()
        return results
