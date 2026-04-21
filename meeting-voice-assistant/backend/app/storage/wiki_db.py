"""
Wiki 存储层数据库操作

基于 ADR-002 设计文档实现
"""

import asyncio
import sqlite3
from typing import Optional, List, Tuple, Any
from pathlib import Path
from datetime import datetime
import json
import uuid
import logging

logger = logging.getLogger("wiki.storage")

# Wiki 数据库路径
WIKI_DB_PATH = Path(__file__).parent.parent.parent.parent / "wiki.db"


class WikiDatabase:
    """Wiki 数据库操作类"""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._db_path = WIKI_DB_PATH
        self._conn: Optional[sqlite3.Connection] = None
        self._initialized = True
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self) -> None:
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Wiki 页面表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wiki_pages (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                slug TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                summary TEXT,
                category_id TEXT,
                meeting_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT DEFAULT 'system',
                version INTEGER DEFAULT 1,
                is_published INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0
            )
        """)

        # 分类表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                slug TEXT UNIQUE NOT NULL,
                description TEXT,
                parent_id TEXT,
                sort_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 标签表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                slug TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#6B7280',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 页面-标签多对多关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_tags (
                page_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                PRIMARY KEY (page_id, tag_id),
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            )
        """)

        # 页面版本历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_versions (
                id TEXT PRIMARY KEY,
                page_id TEXT NOT NULL,
                version INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                change_summary TEXT,
                created_by TEXT DEFAULT 'system',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE
            )
        """)

        # Wiki 实体表 - 从 Wiki 内容中提取的实体
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wiki_entities (
                id TEXT PRIMARY KEY,
                page_id TEXT NOT NULL,
                name TEXT NOT NULL,
                entity_type TEXT NOT NULL,
                description TEXT,
                properties TEXT,
                confidence REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE
            )
        """)

        # Wiki 实体关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wiki_entity_relationships (
                id TEXT PRIMARY KEY,
                page_id TEXT NOT NULL,
                source_entity_id TEXT NOT NULL,
                target_entity_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                description TEXT,
                properties TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE,
                FOREIGN KEY (source_entity_id) REFERENCES wiki_entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_entity_id) REFERENCES wiki_entities(id) ON DELETE CASCADE
            )
        """)

        # 跟踪的任务表 - 跨会议跟踪的行动项
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_tasks (
                id TEXT PRIMARY KEY,
                page_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                assignee TEXT,
                due_date TEXT,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                related_meeting_ids TEXT,
                source_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE SET NULL
            )
        """)

        # 工作流模式表 - 识别到的工作流
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_patterns (
                id TEXT PRIMARY KEY,
                page_id TEXT NOT NULL,
                workflow_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                steps TEXT NOT NULL,
                entities TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_slug ON wiki_pages(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_category ON wiki_pages(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_pages_meeting ON wiki_pages(meeting_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_categories_parent ON categories(parent_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_page_versions_page ON page_versions(page_id, version DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_entities_page ON wiki_entities(page_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wiki_entities_type ON wiki_entities(entity_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracked_tasks_status ON tracked_tasks(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_patterns_page ON workflow_patterns(page_id)")

        conn.commit()
        logger.info(f"[WikiDB] Database initialized at {self._db_path}")

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """将 Row 转换为字典"""
        return dict(row)

    # ========== Wiki Page 操作 ==========

    def create_page(
        self,
        title: str,
        content: str,
        slug: str,
        category_id: Optional[str] = None,
        meeting_id: Optional[str] = None,
        created_by: str = "system",
        summary: Optional[str] = None,
        is_published: bool = False
    ) -> str:
        """创建 Wiki 页面"""
        page_id = f"wiki_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO wiki_pages (id, title, slug, content, summary, category_id, meeting_id, created_by, is_published, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (page_id, title, slug, content, summary, category_id, meeting_id, created_by, 1 if is_published else 0, now, now))

        conn.commit()
        logger.info(f"[WikiDB] Created page: {page_id} - {title}")
        return page_id

    def get_page(self, page_id: str) -> Optional[dict]:
        """获取单个页面"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wiki_pages WHERE id = ? AND is_deleted = 0", (page_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def get_page_by_slug(self, slug: str) -> Optional[dict]:
        """通过 slug 获取页面"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM wiki_pages WHERE slug = ? AND is_deleted = 0", (slug,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        category_id: Optional[str] = None,
        summary: Optional[str] = None,
        is_published: Optional[bool] = None,
        change_summary: Optional[str] = None
    ) -> bool:
        """更新 Wiki 页面"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 获取当前页面
        cursor.execute("SELECT * FROM wiki_pages WHERE id = ? AND is_deleted = 0", (page_id,))
        row = cursor.fetchone()
        if not row:
            return False

        current = self._row_to_dict(row)

        # 保存版本历史
        version_id = f"ver_{uuid.uuid4().hex[:8]}"
        cursor.execute("""
            INSERT INTO page_versions (id, page_id, version, title, content, change_summary, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            version_id,
            page_id,
            current["version"],
            current["title"],
            current["content"],
            change_summary or "Manual update",
            "system",
            current["updated_at"]
        ))

        # 更新页面
        new_title = title if title is not None else current["title"]
        new_content = content if content is not None else current["content"]
        new_summary = summary if summary is not None else current["summary"]
        new_category_id = category_id if category_id is not None else current["category_id"]
        new_published = is_published if is_published is not None else current["is_published"]

        cursor.execute("""
            UPDATE wiki_pages
            SET title = ?, content = ?, summary = ?, category_id = ?, is_published = ?, version = version + 1, updated_at = ?
            WHERE id = ?
        """, (new_title, new_content, new_summary, new_category_id, 1 if new_published else 0, datetime.utcnow().isoformat(), page_id))

        conn.commit()
        logger.info(f"[WikiDB] Updated page: {page_id}")
        return True

    def delete_page(self, page_id: str) -> bool:
        """删除 Wiki 页面 (软删除)"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE wiki_pages SET is_deleted = 1, updated_at = ? WHERE id = ?
        """, (datetime.utcnow().isoformat(), page_id))
        conn.commit()
        logger.info(f"[WikiDB] Deleted page: {page_id}")
        return cursor.rowcount > 0

    def list_pages(
        self,
        page: int = 1,
        page_size: int = 20,
        category_id: Optional[str] = None,
        tag_id: Optional[str] = None,
        search: Optional[str] = None,
        include_unpublished: bool = False
    ) -> Tuple[List[dict], int]:
        """列出 Wiki 页面（支持分页和过滤）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = ["is_deleted = 0"]
        params: List[Any] = []

        if not include_unpublished:
            conditions.append("is_published = 1")

        if category_id:
            conditions.append("category_id = ?")
            params.append(category_id)

        if tag_id:
            conditions.append("id IN (SELECT page_id FROM page_tags WHERE tag_id = ?)")
            params.append(tag_id)

        if search:
            conditions.append("(title LIKE ? OR content LIKE ?)")
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern])

        where_clause = " AND ".join(conditions)

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) FROM wiki_pages WHERE {where_clause}", params)
        total = cursor.fetchone()[0]

        # 分页查询
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM wiki_pages
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        pages = [self._row_to_dict(row) for row in rows]

        # 获取每个页面的标签
        for p in pages:
            p["tags"] = self.get_page_tags(p["id"])

        return pages, total

    # ========== Category 操作 ==========

    def create_category(
        self,
        name: str,
        slug: str,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        sort_order: int = 0
    ) -> str:
        """创建分类"""
        cat_id = f"cat_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO categories (id, name, slug, description, parent_id, sort_order, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (cat_id, name, slug, description, parent_id, sort_order, now))

        conn.commit()
        logger.info(f"[WikiDB] Created category: {cat_id} - {name}")
        return cat_id

    def get_category(self, cat_id: str) -> Optional[dict]:
        """获取分类"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def get_category_by_slug(self, slug: str) -> Optional[dict]:
        """通过 slug 获取分类"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def update_category(
        self,
        cat_id: str,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
        sort_order: Optional[int] = None
    ) -> bool:
        """更新分类"""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = cursor.fetchone()
        if not row:
            return False

        current = self._row_to_dict(row)

        cursor.execute("""
            UPDATE categories
            SET name = COALESCE(?, name),
                slug = COALESCE(?, slug),
                description = COALESCE(?, description),
                parent_id = COALESCE(?, parent_id),
                sort_order = COALESCE(?, sort_order)
            WHERE id = ?
        """, (name, slug, description, parent_id, sort_order, cat_id))

        conn.commit()
        logger.info(f"[WikiDB] Updated category: {cat_id}")
        return True

    def delete_category(self, cat_id: str) -> bool:
        """删除分类"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        logger.info(f"[WikiDB] Deleted category: {cat_id}")
        return cursor.rowcount > 0

    def list_categories(self) -> List[dict]:
        """列出所有分类"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY sort_order, name")
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_category_tree(self) -> List[dict]:
        """获取分类树形结构"""
        categories = self.list_categories()

        # 构建树形结构
        id_map = {c["id"]: {**c, "children": []} for c in categories}
        roots = []

        for cat in categories:
            if cat["parent_id"] and cat["parent_id"] in id_map:
                id_map[cat["parent_id"]]["children"].append(id_map[cat["id"]])
            else:
                roots.append(id_map[cat["id"]])

        return roots

    # ========== Tag 操作 ==========

    def create_tag(self, name: str, slug: str, color: str = "#6B7280") -> str:
        """创建标签"""
        tag_id = f"tag_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tags (id, name, slug, color, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (tag_id, name, slug, color, now))

        conn.commit()
        logger.info(f"[WikiDB] Created tag: {tag_id} - {name}")
        return tag_id

    def get_tag(self, tag_id: str) -> Optional[dict]:
        """获取标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags WHERE id = ?", (tag_id,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def get_tag_by_slug(self, slug: str) -> Optional[dict]:
        """通过 slug 获取标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags WHERE slug = ?", (slug,))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def update_tag(self, tag_id: str, name: Optional[str] = None, slug: Optional[str] = None, color: Optional[str] = None) -> bool:
        """更新标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tags
            SET name = COALESCE(?, name),
                slug = COALESCE(?, slug),
                color = COALESCE(?, color)
            WHERE id = ?
        """, (name, slug, color, tag_id))
        conn.commit()
        logger.info(f"[WikiDB] Updated tag: {tag_id}")
        return cursor.rowcount > 0

    def delete_tag(self, tag_id: str) -> bool:
        """删除标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
        conn.commit()
        logger.info(f"[WikiDB] Deleted tag: {tag_id}")
        return cursor.rowcount > 0

    def list_tags(self) -> List[dict]:
        """列出所有标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tags ORDER BY name")
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_or_create_tag(self, name: str, color: str = "#6B7280") -> str:
        """获取或创建标签"""
        slug = self._generate_slug(name)
        existing = self.get_tag_by_slug(slug)
        if existing:
            return existing["id"]
        return self.create_tag(name, slug, color)

    # ========== Page-Tag 关联操作 ==========

    def add_tag_to_page(self, page_id: str, tag_id: str) -> bool:
        """为页面添加标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO page_tags (page_id, tag_id) VALUES (?, ?)", (page_id, tag_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # 关系已存在

    def remove_tag_from_page(self, page_id: str, tag_id: str) -> bool:
        """从页面移除标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM page_tags WHERE page_id = ? AND tag_id = ?", (page_id, tag_id))
        conn.commit()
        return cursor.rowcount > 0

    def get_page_tags(self, page_id: str) -> List[dict]:
        """获取页面的所有标签"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.* FROM tags t
            JOIN page_tags pt ON t.id = pt.tag_id
            WHERE pt.page_id = ?
        """, (page_id,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def set_page_tags(self, page_id: str, tag_ids: List[str]) -> None:
        """设置页面的标签（覆盖）"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # 删除现有关联
        cursor.execute("DELETE FROM page_tags WHERE page_id = ?", (page_id,))

        # 添加新关联
        for tag_id in tag_ids:
            try:
                cursor.execute("INSERT INTO page_tags (page_id, tag_id) VALUES (?, ?)", (page_id, tag_id))
            except sqlite3.IntegrityError:
                pass

        conn.commit()

    # ========== Page Version 操作 ==========

    def get_page_versions(self, page_id: str) -> List[dict]:
        """获取页面版本历史"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM page_versions
            WHERE page_id = ?
            ORDER BY version DESC
        """, (page_id,))
        rows = cursor.fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_page_version(self, page_id: str, version: int) -> Optional[dict]:
        """获取指定版本"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM page_versions
            WHERE page_id = ? AND version = ?
        """, (page_id, version))
        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def revert_to_version(self, page_id: str, version: int) -> bool:
        """恢复到指定版本"""
        old_version = self.get_page_version(page_id, version)
        if not old_version:
            return False

        return self.update_page(
            page_id,
            title=old_version["title"],
            content=old_version["content"],
            change_summary=f"Reverted to version {version}"
        )

    # ========== 搜索操作 ==========

    def search_pages(self, query: str, category_id: Optional[str] = None, limit: int = 10) -> List[dict]:
        """全文搜索页面"""
        conn = self._get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{query}%"
        conditions = ["is_deleted = 0", "is_published = 1", "(title LIKE ? OR content LIKE ?)"]
        params: List[Any] = [search_pattern, search_pattern]

        if category_id:
            conditions.append("category_id = ?")
            params.append(category_id)

        where_clause = " AND ".join(conditions)

        cursor.execute(f"""
            SELECT id, title, slug, summary, category_id, updated_at
            FROM wiki_pages
            WHERE {where_clause}
            ORDER BY updated_at DESC
            LIMIT ?
        """, (*params, limit))

        rows = cursor.fetchall()
        results = []
        for row in rows:
            p = self._row_to_dict(row)
            # 生成 snippet
            p["snippet"] = self._generate_snippet(p.get("summary") or "", query)
            results.append(p)

        return results

    # ========== Wiki Entity 操作 ==========

    def save_entity(
        self,
        page_id: str,
        name: str,
        entity_type: str,
        description: Optional[str] = None,
        properties: Optional[dict] = None,
        confidence: float = 1.0
    ) -> str:
        """保存实体到页面"""
        entity_id = f"ent_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO wiki_entities (id, page_id, name, entity_type, description, properties, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entity_id, page_id, name, entity_type, description, json.dumps(properties) if properties else None, confidence, now))

        conn.commit()
        logger.info(f"[WikiDB] Saved entity: {entity_id} - {name}")
        return entity_id

    def get_page_entities(self, page_id: str) -> List[dict]:
        """获取页面的所有实体"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM wiki_entities
            WHERE page_id = ?
            ORDER BY entity_type, name
        """, (page_id,))
        rows = cursor.fetchall()
        entities = []
        for row in rows:
            e = self._row_to_dict(row)
            if e.get("properties"):
                e["properties"] = json.loads(e["properties"])
            entities.append(e)
        return entities

    def delete_page_entities(self, page_id: str) -> None:
        """删除页面的所有实体"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wiki_entities WHERE page_id = ?", (page_id,))
        conn.commit()

    # ========== Entity Relationship 操作 ==========

    def save_entity_relationship(
        self,
        page_id: str,
        source_entity_id: str,
        target_entity_id: str,
        relationship_type: str,
        description: Optional[str] = None,
        properties: Optional[dict] = None
    ) -> str:
        """保存实体关系"""
        rel_id = f"rel_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO wiki_entity_relationships (id, page_id, source_entity_id, target_entity_id, relationship_type, description, properties, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (rel_id, page_id, source_entity_id, target_entity_id, relationship_type, description, json.dumps(properties) if properties else None, now))

        conn.commit()
        logger.info(f"[WikiDB] Saved relationship: {rel_id}")
        return rel_id

    def get_page_relationships(self, page_id: str) -> List[dict]:
        """获取页面的所有实体关系"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM wiki_entity_relationships
            WHERE page_id = ?
            ORDER BY relationship_type
        """, (page_id,))
        rows = cursor.fetchall()
        rels = []
        for row in rows:
            r = self._row_to_dict(row)
            if r.get("properties"):
                r["properties"] = json.loads(r["properties"])
            rels.append(r)
        return rels

    def delete_page_relationships(self, page_id: str) -> None:
        """删除页面的所有实体关系"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM wiki_entity_relationships WHERE page_id = ?", (page_id,))
        conn.commit()

    # ========== Tracked Task 操作 ==========

    def save_tracked_task(
        self,
        page_id: Optional[str],
        title: str,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        due_date: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        related_meeting_ids: Optional[List[str]] = None,
        source_text: Optional[str] = None
    ) -> str:
        """保存跟踪任务"""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tracked_tasks (id, page_id, title, description, assignee, due_date, status, priority, related_meeting_ids, source_text, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id, page_id, title, description, assignee, due_date,
            status, priority,
            json.dumps(related_meeting_ids) if related_meeting_ids else None,
            source_text, now, now
        ))

        conn.commit()
        logger.info(f"[WikiDB] Saved tracked task: {task_id} - {title}")
        return task_id

    def get_tracked_tasks(
        self,
        page_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[dict]:
        """获取跟踪任务"""
        conn = self._get_connection()
        cursor = conn.cursor()

        conditions = []
        params = []
        if page_id:
            conditions.append("page_id = ?")
            params.append(page_id)
        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        cursor.execute(f"""
            SELECT * FROM tracked_tasks
            WHERE {where_clause}
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                due_date ASC,
                created_at DESC
        """, params)
        rows = cursor.fetchall()
        tasks = []
        for row in rows:
            t = self._row_to_dict(row)
            if t.get("related_meeting_ids"):
                t["related_meeting_ids"] = json.loads(t["related_meeting_ids"])
            tasks.append(t)
        return tasks

    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        now = datetime.utcnow().isoformat()
        completed_at = now if status == "completed" else None

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE tracked_tasks
            SET status = ?, updated_at = ?, completed_at = ?
            WHERE id = ?
        """, (status, now, completed_at, task_id))
        conn.commit()
        return cursor.rowcount > 0

    def delete_tracked_task(self, task_id: str) -> bool:
        """删除跟踪任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tracked_tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0

    # ========== Workflow Pattern 操作 ==========

    def save_workflow_pattern(
        self,
        page_id: str,
        workflow_type: str,
        name: str,
        steps: List[dict],
        description: Optional[str] = None,
        entities: Optional[List[str]] = None
    ) -> str:
        """保存工作流模式"""
        pattern_id = f"wf_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO workflow_patterns (id, page_id, workflow_type, name, description, steps, entities, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pattern_id, page_id, workflow_type, name, description,
            json.dumps(steps), json.dumps(entities) if entities else None, now
        ))

        conn.commit()
        logger.info(f"[WikiDB] Saved workflow pattern: {pattern_id} - {name}")
        return pattern_id

    def get_page_workflows(self, page_id: str) -> List[dict]:
        """获取页面的工作流模式"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM workflow_patterns
            WHERE page_id = ?
            ORDER BY workflow_type, name
        """, (page_id,))
        rows = cursor.fetchall()
        patterns = []
        for row in rows:
            p = self._row_to_dict(row)
            if p.get("steps"):
                p["steps"] = json.loads(p["steps"])
            if p.get("entities"):
                p["entities"] = json.loads(p["entities"])
            patterns.append(p)
        return patterns

    def delete_page_workflows(self, page_id: str) -> None:
        """删除页面的工作流模式"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workflow_patterns WHERE page_id = ?", (page_id,))
        conn.commit()

    # ========== 工具方法 ==========

    def _generate_slug(self, text: str) -> str:
        """生成 URL 友好的 slug"""
        import re
        # 转小写
        slug = text.lower()
        # 替换空格为 -
        slug = re.sub(r'\s+', '-', slug)
        # 移除非字母数字字符
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        # 移除连续横线
        slug = re.sub(r'-+', '-', slug)
        # 去除首尾横线
        slug = slug.strip('-')
        return slug

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

    def generate_unique_slug(self, base_slug: str) -> str:
        """生成唯一的 slug"""
        slug = base_slug
        counter = 1

        while True:
            cursor = self._get_connection().cursor()
            cursor.execute("SELECT id FROM wiki_pages WHERE slug = ?", (slug,))
            if not cursor.fetchone():
                break
            slug = f"{base_slug}-{counter}"
            counter += 1

        return slug

    def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            self._conn.close()
            self._conn = None


# 全局实例
_wiki_db: Optional[WikiDatabase] = None


def get_wiki_db() -> WikiDatabase:
    """获取 Wiki 数据库实例"""
    global _wiki_db
    if _wiki_db is None:
        _wiki_db = WikiDatabase()
    return _wiki_db