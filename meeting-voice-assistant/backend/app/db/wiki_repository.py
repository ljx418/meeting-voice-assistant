"""
Wiki 数据库存储层

使用 SQLite + SQLAlchemy 实现 Wiki 文档的持久化存储
"""

import sqlite3
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger("app.db.wiki_repository")


class WikiRepository:
    """Wiki 文档仓库 - SQLite 实现"""

    def __init__(self, db_path: Optional[Path] = None):
        """初始化 Wiki 仓库"""
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent.parent / "audio_cache" / "wiki.db"
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """初始化数据库表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Wiki 文档表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiki_documents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    doc_type TEXT NOT NULL,
                    parent_id TEXT,
                    meeting_id TEXT,
                    tags TEXT DEFAULT '[]',
                    version INTEGER DEFAULT 1,
                    is_deleted INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    entities TEXT DEFAULT '[]',
                    relationships TEXT DEFAULT '[]',
                    graphrag_doc_id TEXT,
                    last_indexed_at TEXT
                )
            """)

            # 版本历史表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiki_document_versions (
                    id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    change_summary TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT
                )
            """)

            # 文档关系表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wiki_relationships (
                    id TEXT PRIMARY KEY,
                    source_doc_id TEXT NOT NULL,
                    target_doc_id TEXT NOT NULL,
                    relationship_type TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # FTS5 虚拟表用于全文搜索
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(
                    id,
                    title,
                    content,
                    tags,
                    content='wiki_documents',
                    content_rowid='rowid'
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_doc_meeting ON wiki_documents(meeting_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_doc_parent ON wiki_documents(parent_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_doc_type ON wiki_documents(doc_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_versions_doc ON wiki_document_versions(document_id)")

            conn.commit()
            logger.info(f"[WikiRepository] Database initialized at {self.db_path}")

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """将 Row 转换为 dict"""
        d = dict(row)
        if 'tags' in d and d['tags']:
            d['tags'] = json.loads(d['tags'])
        elif 'tags' in d:
            d['tags'] = []
        if 'is_deleted' in d:
            d['is_deleted'] = bool(d['is_deleted'])
        # Parse GraphRAG entities/relationships
        if 'entities' in d and d['entities']:
            try:
                d['entities'] = json.loads(d['entities'])
            except:
                d['entities'] = []
        elif 'entities' in d:
            d['entities'] = []
        if 'relationships' in d and d['relationships']:
            try:
                d['relationships'] = json.loads(d['relationships'])
            except:
                d['relationships'] = []
        elif 'relationships' in d:
            d['relationships'] = []
        return d

    # ========== 文档 CRUD ==========

    def create_document(
        self,
        title: str,
        content: str,
        doc_type: str,
        parent_id: Optional[str] = None,
        meeting_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None,
        entities: Optional[List[dict]] = None,
        relationships: Optional[List[dict]] = None,
        graphrag_doc_id: Optional[str] = None,
    ) -> dict:
        """创建文档"""
        doc_id = f"wiki_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()
        tags_json = json.dumps(tags or [])
        entities_json = json.dumps(entities or [])
        relationships_json = json.dumps(relationships or [])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO wiki_documents
                (id, title, content, doc_type, parent_id, meeting_id, tags, created_at, updated_at, created_by, entities, relationships, graphrag_doc_id, last_indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (doc_id, title, content, doc_type, parent_id, meeting_id, tags_json, now, now, created_by, entities_json, relationships_json, graphrag_doc_id, now if graphrag_doc_id else None))

            # 同步 FTS 索引
            cursor.execute("""
                INSERT INTO wiki_fts (id, title, content, tags)
                VALUES (?, ?, ?, ?)
            """, (doc_id, title, content, tags_json))

            conn.commit()

        return self.get_document(doc_id)

    def get_document(self, doc_id: str) -> Optional[dict]:
        """获取文档"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM wiki_documents WHERE id = ? AND is_deleted = 0",
                (doc_id,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_document_by_graphrag_id(self, graphrag_doc_id: str) -> Optional[dict]:
        """通过 GraphRAG doc_id 获取文档"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM wiki_documents WHERE graphrag_doc_id = ? AND is_deleted = 0",
                (graphrag_doc_id,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def update_graphrag_index(
        self,
        doc_id: str,
        entities: List[dict],
        relationships: List[dict],
        graphrag_doc_id: Optional[str] = None
    ) -> bool:
        """更新文档的 GraphRAG 索引信息"""
        now = datetime.utcnow().isoformat()
        entities_json = json.dumps(entities)
        relationships_json = json.dumps(relationships)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            if graphrag_doc_id:
                cursor.execute("""
                    UPDATE wiki_documents
                    SET entities = ?, relationships = ?, graphrag_doc_id = ?, last_indexed_at = ?
                    WHERE id = ? AND is_deleted = 0
                """, (entities_json, relationships_json, graphrag_doc_id, now, doc_id))
            else:
                cursor.execute("""
                    UPDATE wiki_documents
                    SET entities = ?, relationships = ?, last_indexed_at = ?
                    WHERE id = ? AND is_deleted = 0
                """, (entities_json, relationships_json, now, doc_id))
            conn.commit()
            return cursor.rowcount > 0

    def clear_graphrag_index(self, doc_id: str) -> bool:
        """清除文档的 GraphRAG 索引信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE wiki_documents
                SET entities = '[]', relationships = '[]', graphrag_doc_id = NULL, last_indexed_at = NULL
                WHERE id = ? AND is_deleted = 0
            """, (doc_id,))
            conn.commit()
            return cursor.rowcount > 0

    def update_document(
        self,
        doc_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        parent_id: Optional[str] = None,
        change_summary: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> Optional[dict]:
        """更新文档（自动创建版本）"""
        # 获取当前文档
        current = self.get_document(doc_id)
        if not current:
            return None

        # 创建版本快照
        self._create_version_snapshot(current, change_summary, updated_by)

        # 更新文档
        now = datetime.utcnow().isoformat()
        new_title = title if title is not None else current['title']
        new_content = content if content is not None else current['content']
        new_tags = json.dumps(tags) if tags is not None else current['tags']
        new_parent_id = parent_id if parent_id is not None else current['parent_id']
        new_version = current['version'] + 1

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE wiki_documents
                SET title = ?, content = ?, tags = ?, parent_id = ?,
                    version = ?, updated_at = ?
                WHERE id = ?
            """, (new_title, new_content, new_tags, new_parent_id, new_version, now, doc_id))

            # 更新 FTS 索引
            cursor.execute("DELETE FROM wiki_fts WHERE id = ?", (doc_id,))
            cursor.execute("""
                INSERT INTO wiki_fts (id, title, content, tags)
                VALUES (?, ?, ?, ?)
            """, (doc_id, new_title, new_content, new_tags))

            conn.commit()

        return self.get_document(doc_id)

    def delete_document(self, doc_id: str) -> bool:
        """删除文档（软删除）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE wiki_documents SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, (datetime.utcnow().isoformat(), doc_id))

            # 从 FTS 删除
            cursor.execute("DELETE FROM wiki_fts WHERE id = ?", (doc_id,))

            conn.commit()
            return cursor.rowcount > 0

    def list_documents(
        self,
        doc_type: Optional[str] = None,
        meeting_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[dict], int]:
        """列出文档（支持分页和过滤）"""
        conditions = ["is_deleted = 0"]
        params = []

        if doc_type:
            conditions.append("doc_type = ?")
            params.append(doc_type)

        if meeting_id:
            conditions.append("meeting_id = ?")
            params.append(meeting_id)

        if parent_id is not None:
            conditions.append("parent_id = ?")
            params.append(parent_id)

        if tags:
            for tag in tags:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')

        where_clause = " AND ".join(conditions)

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 获取总数
            cursor.execute(f"SELECT COUNT(*) FROM wiki_documents WHERE {where_clause}", params)
            total = cursor.fetchone()[0]

            # 获取分页数据
            offset = (page - 1) * size
            cursor.execute(f"""
                SELECT * FROM wiki_documents
                WHERE {where_clause}
                ORDER BY updated_at DESC
                LIMIT ? OFFSET ?
            """, (*params, size, offset))

            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows], total

    # ========== 版本管理 ==========

    def _create_version_snapshot(
        self,
        document: dict,
        change_summary: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> None:
        """创建版本快照"""
        version_id = f"wv_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO wiki_document_versions
                (id, document_id, version, title, content, change_summary, created_at, created_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                version_id,
                document['id'],
                document['version'],
                document['title'],
                document['content'],
                change_summary,
                now,
                created_by,
            ))
            conn.commit()

    def get_document_versions(self, doc_id: str) -> List[dict]:
        """获取文档版本历史"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM wiki_document_versions
                WHERE document_id = ?
                ORDER BY version DESC
            """, (doc_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def restore_version(self, doc_id: str, version: int) -> Optional[dict]:
        """恢复到指定版本"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM wiki_document_versions
                WHERE document_id = ? AND version = ?
            """, (doc_id, version))
            row = cursor.fetchone()

            if not row:
                return None

            version_data = dict(row)
            return self.update_document(
                doc_id,
                title=version_data['title'],
                content=version_data['content'],
                change_summary=f"Restored from version {version}",
            )

    # ========== 搜索 ==========

    def search(
        self,
        query: str,
        doc_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        page: int = 1,
        size: int = 20,
    ) -> Tuple[List[dict], int]:
        """全文搜索"""
        if not query:
            return [], 0

        # FTS5 搜索
        fts_query = query.replace('"', '""')

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 搜索条件
            search_conditions = [f'title LIKE "%{fts_query}%" OR content LIKE "%{fts_query}%"']

            if doc_type:
                # 需要联合查询
                sql = f"""
                    SELECT d.*, wiki_fts.rank
                    FROM wiki_fts
                    JOIN wiki_documents d ON wiki_fts.id = d.id
                    WHERE wiki_fts MATCH ?
                    AND d.is_deleted = 0
                    AND d.doc_type = ?
                    ORDER BY rank
                """
                params = [f'"{fts_query}"', doc_type]
            else:
                sql = f"""
                    SELECT d.*, wiki_fts.rank
                    FROM wiki_fts
                    JOIN wiki_documents d ON wiki_fts.id = d.id
                    WHERE wiki_fts MATCH ?
                    AND d.is_deleted = 0
                    ORDER BY rank
                """
                params = [f'"{fts_query}"']

            # 获取总数
            count_sql = sql.replace("SELECT d.*, wiki_fts.rank", "SELECT COUNT(*)")
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0] if cursor.fetchone() else 0

            # 分页
            offset = (page - 1) * size
            paginated_sql = f"{sql} LIMIT ? OFFSET ?"
            params.extend([size, offset])

            cursor.execute(paginated_sql, params)
            rows = cursor.fetchall()

            results = []
            for row in rows:
                d = self._row_to_dict(row)
                # 生成 snippet
                d['snippet'] = self._generate_snippet(d['content'], query)
                results.append(d)

            return results, total

    def _generate_snippet(self, content: str, query: str, length: int = 200) -> str:
        """生成搜索结果片段"""
        idx = content.lower().find(query.lower())
        if idx == -1:
            return content[:length] + "..." if len(content) > length else content

        start = max(0, idx - 50)
        end = min(len(content), idx + len(query) + 150)
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
        return snippet

    # ========== 关系管理 ==========

    def create_relationship(
        self,
        source_doc_id: str,
        target_doc_id: str,
        relationship_type: str,
    ) -> dict:
        """创建文档关联"""
        rel_id = f"wr_{uuid.uuid4().hex[:12]}"
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO wiki_relationships
                (id, source_doc_id, target_doc_id, relationship_type, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (rel_id, source_doc_id, target_doc_id, relationship_type, now))
            conn.commit()

        return {
            "id": rel_id,
            "source_doc_id": source_doc_id,
            "target_doc_id": target_doc_id,
            "relationship_type": relationship_type,
            "created_at": now,
        }

    def get_document_relationships(self, doc_id: str) -> List[dict]:
        """获取文档的所有关联"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM wiki_relationships
                WHERE source_doc_id = ? OR target_doc_id = ?
            """, (doc_id, doc_id))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_document_children(self, doc_id: str) -> List[dict]:
        """获取子文档"""
        conditions = ["parent_id = ?", "is_deleted = 0"]
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM wiki_documents
                WHERE {' AND '.join(conditions)}
                ORDER BY updated_at DESC
            """, (doc_id,))
            rows = cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]

    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT tags FROM wiki_documents WHERE is_deleted = 0")
            rows = cursor.fetchall()
            all_tags = set()
            for row in rows:
                try:
                    tags = json.loads(row[0])
                    all_tags.update(tags)
                except:
                    pass
            return sorted(list(all_tags))