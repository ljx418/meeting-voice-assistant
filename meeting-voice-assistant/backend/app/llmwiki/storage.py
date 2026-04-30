"""LLMWiki 存储层 - SQLite + FTS5"""
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

from .config import LLMWikiConfig
from .models import (
    Citation,
    Conversation,
    IngestRun,
    IngestStatus,
    NormalizedSection,
    PageKind,
    PageLink,
    Passage,
    SectionKind,
    SourceRecord,
    SourceType,
    Turn,
    WikiPage,
)


class JSONEncoder(json.JSONEncoder):
    """支持 datetime 的 JSON 编码器"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def json_dumps(data: Any) -> str:
    return json.dumps(data, cls=JSONEncoder)


def json_loads(data: str) -> Any:
    if not data:
        return {}
    return json.loads(data)


class Storage:
    """LLMWiki 存储引擎"""

    SCHEMA_VERSION = 2

    def __init__(self, config: Optional[LLMWikiConfig] = None):
        self.config = config or LLMWikiConfig()
        self.conn: Optional[sqlite3.Connection] = None

    @contextmanager
    def get_conn(self) -> Generator[sqlite3.Connection, None, None]:
        """获取数据库连接的上下文管理器"""
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.config.db_path))
            self.conn.row_factory = sqlite3.Row
        try:
            yield self.conn
        finally:
            pass  # 不关闭连接，保持复用

    def init_db(self) -> None:
        """初始化数据库 schema"""
        with self.get_conn() as conn:
            cursor = conn.cursor()

            # Schema 版本表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            """)

            # 检查是否需要初始化
            cursor.execute("SELECT version FROM schema_version LIMIT 1")
            row = cursor.fetchone()
            if row is None:
                self._create_tables(cursor)
                cursor.execute(
                    "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                    (self.SCHEMA_VERSION, datetime.utcnow().isoformat())
                )
            current_version = row["version"] if row is not None else self.SCHEMA_VERSION
            self._migrate_tables(cursor)
            if current_version != self.SCHEMA_VERSION:
                cursor.execute("UPDATE schema_version SET version = ?, applied_at = ?", (
                    self.SCHEMA_VERSION,
                    datetime.utcnow().isoformat(),
                ))
            conn.commit()

    def _create_tables(self, cursor: sqlite3.Cursor) -> None:
        """创建所有表"""
        # Sources 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sources (
                source_id TEXT PRIMARY KEY,
                source_type TEXT NOT NULL,
                authority TEXT,
                original_path TEXT,
                stored_path TEXT,
                sha256 TEXT,
                title TEXT,
                mime TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                extractor_name TEXT,
                extractor_version TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                error TEXT,
                content_hash TEXT,
                compiled_at TEXT,
                compile_status TEXT NOT NULL DEFAULT 'pending',
                compile_error TEXT,
                compiled_by_model TEXT,
                stale_reason TEXT,
                meta_json TEXT NOT NULL DEFAULT '{}'
            )
        """)

        # Normalized sections 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS normalized_sections (
                section_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                title TEXT,
                text TEXT NOT NULL,
                locator TEXT,
                order_index INTEGER NOT NULL DEFAULT 0,
                meta_json TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (source_id) REFERENCES sources(source_id)
            )
        """)

        # Passages 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passages (
                passage_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                section_id TEXT,
                text TEXT NOT NULL,
                cjk_terms TEXT NOT NULL DEFAULT '[]',
                token_count_est INTEGER NOT NULL DEFAULT 0,
                locator TEXT,
                order_index INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (source_id) REFERENCES sources(source_id),
                FOREIGN KEY (section_id) REFERENCES normalized_sections(section_id)
            )
        """)

        # Pages 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pages (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'article',
                summary TEXT,
                body_md TEXT NOT NULL DEFAULT '',
                version INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL,
                markdown_path TEXT,
                content_hash TEXT,
                compiled_at TEXT,
                compile_status TEXT NOT NULL DEFAULT 'pending',
                compile_error TEXT,
                compiled_by_model TEXT,
                stale_reason TEXT,
                meta_json TEXT NOT NULL DEFAULT '{}'
            )
        """)

        # Page-Sources 多对多关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS page_sources (
                slug TEXT NOT NULL,
                source_id TEXT NOT NULL,
                PRIMARY KEY (slug, source_id),
                FOREIGN KEY (slug) REFERENCES pages(slug),
                FOREIGN KEY (source_id) REFERENCES sources(source_id)
            )
        """)

        # Links 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                from_slug TEXT NOT NULL,
                to_slug TEXT NOT NULL,
                link_text TEXT,
                PRIMARY KEY (from_slug, to_slug),
                FOREIGN KEY (from_slug) REFERENCES pages(slug),
                FOREIGN KEY (to_slug) REFERENCES pages(slug)
            )
        """)

        # Conversations 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                source_id TEXT,
                title TEXT,
                participants TEXT NOT NULL DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                meta_json TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (source_id) REFERENCES sources(source_id)
            )
        """)

        # Turns 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS turns (
                turn_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content_text TEXT NOT NULL,
                timestamp TEXT,
                order_index INTEGER NOT NULL DEFAULT 0,
                meta_json TEXT NOT NULL DEFAULT '{}',
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
            )
        """)

        # Ingest runs 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingest_runs (
                run_id TEXT PRIMARY KEY,
                source_ids TEXT NOT NULL DEFAULT '[]',
                status TEXT NOT NULL DEFAULT 'pending',
                started_at TEXT NOT NULL,
                completed_at TEXT,
                pages_created INTEGER NOT NULL DEFAULT 0,
                passages_created INTEGER NOT NULL DEFAULT 0,
                error_message TEXT
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_type ON sources(source_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_status ON sources(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sections_source ON normalized_sections(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_passages_source ON passages(source_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_passages_section ON passages(section_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_turns_conversation ON turns(conversation_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_links_to_slug ON links(to_slug)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sources_content_hash ON sources(content_hash)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_compile_status ON pages(compile_status)")

        # FTS5 索引 - Pages (standalone, not contentless)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS pages_fts USING fts5(
                slug,
                title,
                body_md
            )
        """)

        # FTS5 索引 - Passages (standalone, includes passage_id for correlation)
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS passages_fts USING fts5(
                passage_id,
                text,
                cjk_terms
            )
        """)

    def _migrate_tables(self, cursor: sqlite3.Cursor) -> None:
        """Best-effort schema migrations for existing workspaces."""
        self._ensure_column(cursor, "sources", "error", "TEXT")
        self._ensure_column(cursor, "sources", "content_hash", "TEXT")
        self._ensure_column(cursor, "sources", "compiled_at", "TEXT")
        self._ensure_column(cursor, "sources", "compile_status", "TEXT NOT NULL DEFAULT 'pending'")
        self._ensure_column(cursor, "sources", "compile_error", "TEXT")
        self._ensure_column(cursor, "sources", "compiled_by_model", "TEXT")
        self._ensure_column(cursor, "sources", "stale_reason", "TEXT")

        self._ensure_column(cursor, "pages", "markdown_path", "TEXT")
        self._ensure_column(cursor, "pages", "content_hash", "TEXT")
        self._ensure_column(cursor, "pages", "compiled_at", "TEXT")
        self._ensure_column(cursor, "pages", "compile_status", "TEXT NOT NULL DEFAULT 'pending'")
        self._ensure_column(cursor, "pages", "compile_error", "TEXT")
        self._ensure_column(cursor, "pages", "compiled_by_model", "TEXT")
        self._ensure_column(cursor, "pages", "stale_reason", "TEXT")

    def _ensure_column(self, cursor: sqlite3.Cursor, table: str, column: str, ddl: str) -> None:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row["name"] for row in cursor.fetchall()}
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

    # ========== Source CRUD ==========

    def insert_source(self, source: SourceRecord) -> None:
        """插入源记录"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sources (
                    source_id, source_type, authority, original_path, stored_path,
                    sha256, title, mime, created_at, updated_at,
                    extractor_name, extractor_version, status, error, content_hash,
                    compiled_at, compile_status, compile_error, compiled_by_model,
                    stale_reason, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                source.source_id,
                source.source_type.value if isinstance(source.source_type, SourceType) else source.source_type,
                source.authority,
                source.original_path,
                source.stored_path,
                source.sha256,
                source.title,
                source.mime,
                (source.created_at or datetime.utcnow()).isoformat(),
                (source.updated_at or datetime.utcnow()).isoformat(),
                source.extractor_name,
                source.extractor_version,
                source.status.value if isinstance(source.status, IngestStatus) else source.status,
                source.error,
                source.content_hash,
                source.compiled_at.isoformat() if source.compiled_at else None,
                source.compile_status,
                source.compile_error,
                source.compiled_by_model,
                source.stale_reason,
                json_dumps(source.meta_json),
            ))
            conn.commit()

    def get_source(self, source_id: str) -> Optional[SourceRecord]:
        """获取源记录"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sources WHERE source_id = ?", (source_id,))
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_source(row)

    def list_sources(
        self,
        source_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[SourceRecord]:
        """列出源记录"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM sources WHERE 1=1"
            params: List[Any] = []

            if source_type:
                query += " AND source_type = ?"
                params.append(source_type)
            if status:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            return [self._row_to_source(row) for row in cursor.fetchall()]

    def _row_to_source(self, row: sqlite3.Row) -> SourceRecord:
        """将 Row 转换为 SourceRecord"""
        return SourceRecord(
            source_id=row["source_id"],
            source_type=SourceType(row["source_type"]),
            authority=row["authority"],
            original_path=row["original_path"],
            stored_path=row["stored_path"],
            sha256=row["sha256"],
            title=row["title"],
            mime=row["mime"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            extractor_name=row["extractor_name"],
            extractor_version=row["extractor_version"],
            status=IngestStatus(row["status"]),
            error=row["error"] if "error" in row.keys() else None,
            content_hash=row["content_hash"] if "content_hash" in row.keys() else None,
            compiled_at=datetime.fromisoformat(row["compiled_at"]) if row["compiled_at"] else None,
            compile_status=row["compile_status"] if "compile_status" in row.keys() else "pending",
            compile_error=row["compile_error"] if "compile_error" in row.keys() else None,
            compiled_by_model=row["compiled_by_model"] if "compiled_by_model" in row.keys() else None,
            stale_reason=row["stale_reason"] if "stale_reason" in row.keys() else None,
            meta_json=json_loads(row["meta_json"]),
        )

    def update_source_compile_state(
        self,
        source_id: str,
        *,
        compile_status: str,
        compiled_at: Optional[datetime],
        compiled_by_model: Optional[str],
        compile_error: Optional[str],
        content_hash: Optional[str] = None,
        stale_reason: Optional[str] = None,
    ) -> None:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE sources
                SET compile_status = ?, compiled_at = ?, compiled_by_model = ?,
                    compile_error = ?, content_hash = COALESCE(?, content_hash),
                    stale_reason = ?, updated_at = ?
                WHERE source_id = ?
                """,
                (
                    compile_status,
                    compiled_at.isoformat() if compiled_at else None,
                    compiled_by_model,
                    compile_error,
                    content_hash,
                    stale_reason,
                    datetime.utcnow().isoformat(),
                    source_id,
                ),
            )
            conn.commit()

    # ========== Passage CRUD ==========

    def insert_passage(self, passage: Passage) -> None:
        """插入段落"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO passages (
                    passage_id, source_id, section_id, text, cjk_terms,
                    token_count_est, locator, order_index
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                passage.passage_id,
                passage.source_id,
                passage.section_id,
                passage.text,
                passage.cjk_terms if isinstance(passage.cjk_terms, str) else json_dumps(passage.cjk_terms),
                passage.token_count_est,
                json_dumps(passage.locator) if isinstance(passage.locator, dict) else passage.locator,
                passage.order_index,
            ))
            conn.commit()

            # 更新 FTS 索引 (直接插入，使用 passage_id 关联)
            cursor.execute(
                "INSERT INTO passages_fts (passage_id, text, cjk_terms) VALUES (?, ?, ?)",
                (passage.passage_id, passage.text, passage.cjk_terms if isinstance(passage.cjk_terms, str) else json_dumps(passage.cjk_terms))
            )
            conn.commit()

    def search_passages(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Passage]:
        """搜索段落"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            # 使用 FTS5 搜索 (通过 passage_id 关联)
            cursor.execute("""
                SELECT p.* FROM passages p
                JOIN passages_fts fts ON p.passage_id = fts.passage_id
                WHERE passages_fts MATCH ?
                ORDER BY rank
                LIMIT ? OFFSET ?
            """, (query, limit, offset))

            return [self._row_to_passage(row) for row in cursor.fetchall()]

    def _row_to_passage(self, row: sqlite3.Row) -> Passage:
        """将 Row 转换为 Passage"""
        return Passage(
            passage_id=row["passage_id"],
            source_id=row["source_id"],
            section_id=row["section_id"],
            text=row["text"],
            cjk_terms=row["cjk_terms"],  # Already a string (space-separated)
            token_count_est=row["token_count_est"],
            locator=json_loads(row["locator"]) if row["locator"] else {},
            order_index=row["order_index"],
        )

    # ========== Page CRUD ==========

    def insert_page(self, page: WikiPage) -> None:
        """插入或更新 Wiki 页面"""
        with self.get_conn() as conn:
            cursor = conn.cursor()

            # Upsert page
            cursor.execute("""
                INSERT INTO pages (
                    slug, title, kind, summary, body_md, version, updated_at,
                    markdown_path, content_hash, compiled_at, compile_status,
                    compile_error, compiled_by_model, stale_reason, meta_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    kind = excluded.kind,
                    summary = excluded.summary,
                    body_md = excluded.body_md,
                    version = version + 1,
                    updated_at = excluded.updated_at,
                    markdown_path = excluded.markdown_path,
                    content_hash = excluded.content_hash,
                    compiled_at = excluded.compiled_at,
                    compile_status = excluded.compile_status,
                    compile_error = excluded.compile_error,
                    compiled_by_model = excluded.compiled_by_model,
                    stale_reason = excluded.stale_reason,
                    meta_json = excluded.meta_json
            """, (
                page.slug,
                page.title,
                page.kind.value if isinstance(page.kind, PageKind) else page.kind,
                page.summary,
                page.body_md,
                page.version,
                (page.updated_at or datetime.utcnow()).isoformat(),
                page.markdown_path,
                page.content_hash,
                page.compiled_at.isoformat() if page.compiled_at else None,
                page.compile_status,
                page.compile_error,
                page.compiled_by_model,
                page.stale_reason,
                json_dumps(page.meta_json),
            ))

            # 更新 page_sources 关系
            cursor.execute("DELETE FROM page_sources WHERE slug = ?", (page.slug,))
            for source_id in page.source_ids:
                cursor.execute(
                    "INSERT INTO page_sources (slug, source_id) VALUES (?, ?)",
                    (page.slug, source_id)
                )

            # 更新 links
            cursor.execute("DELETE FROM links WHERE from_slug = ?", (page.slug,))
            for link_slug in page.link_slugs:
                cursor.execute(
                    "INSERT INTO links (from_slug, to_slug) VALUES (?, ?)",
                    (page.slug, link_slug)
                )

            conn.commit()

            # 更新 FTS 索引 (先删除再插入)
            cursor.execute("DELETE FROM pages_fts WHERE slug = ?", (page.slug,))
            cursor.execute(
                "INSERT INTO pages_fts (slug, title, body_md) VALUES (?, ?, ?)",
                (page.slug, page.title, page.body_md)
            )
            conn.commit()

    def get_page(self, slug: str) -> Optional[WikiPage]:
        """获取 Wiki 页面"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pages WHERE slug = ?", (slug,))
            row = cursor.fetchone()
            if row is None:
                return None

            # 获取关联的 source_ids
            cursor.execute(
                "SELECT source_id FROM page_sources WHERE slug = ?",
                (slug,)
            )
            source_ids = [r["source_id"] for r in cursor.fetchall()]

            # 获取 link_slugs
            cursor.execute(
                "SELECT to_slug FROM links WHERE from_slug = ?",
                (slug,)
            )
            link_slugs = [r["to_slug"] for r in cursor.fetchall()]

            return self._row_to_page(row, source_ids, link_slugs)

    def get_backlinks(self, slug: str) -> List[dict]:
        """获取反向链接（哪些页面链接到了此页面）

        Args:
            slug: 目标页面 slug

        Returns:
            [{"slug": str, "title": str}, ...]
        """
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.slug, p.title FROM links l
                JOIN pages p ON l.from_slug = p.slug
                WHERE l.to_slug = ?
                ORDER BY p.title
            """, (slug,))
            return [{"slug": row["slug"], "title": row["title"]} for row in cursor.fetchall()]

    def list_pages(
        self,
        kind: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[WikiPage]:
        """列出 Wiki 页面"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM pages WHERE 1=1"
            params: List[Any] = []

            if kind:
                query += " AND kind = ?"
                params.append(kind)

            query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            pages = []
            for row in cursor.fetchall():
                slug = row["slug"]
                cursor.execute(
                    "SELECT source_id FROM page_sources WHERE slug = ?",
                    (slug,)
                )
                source_ids = [r["source_id"] for r in cursor.fetchall()]

                cursor.execute(
                    "SELECT to_slug FROM links WHERE from_slug = ?",
                    (slug,)
                )
                link_slugs = [r["to_slug"] for r in cursor.fetchall()]

                pages.append(self._row_to_page(row, source_ids, link_slugs))

            return pages

    def _row_to_page(
        self,
        row: sqlite3.Row,
        source_ids: List[str],
        link_slugs: List[str],
    ) -> WikiPage:
        """将 Row 转换为 WikiPage"""
        return WikiPage(
            slug=row["slug"],
            title=row["title"],
            kind=PageKind(row["kind"]),
            summary=row["summary"],
            body_md=row["body_md"],
            source_ids=source_ids,
            link_slugs=link_slugs,
            version=row["version"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
            markdown_path=row["markdown_path"] if "markdown_path" in row.keys() else None,
            content_hash=row["content_hash"] if "content_hash" in row.keys() else None,
            compiled_at=datetime.fromisoformat(row["compiled_at"]) if row["compiled_at"] else None,
            compile_status=row["compile_status"] if "compile_status" in row.keys() else "pending",
            compile_error=row["compile_error"] if "compile_error" in row.keys() else None,
            compiled_by_model=row["compiled_by_model"] if "compiled_by_model" in row.keys() else None,
            stale_reason=row["stale_reason"] if "stale_reason" in row.keys() else None,
            meta_json=json_loads(row["meta_json"]),
        )

    def get_passages_by_source(self, source_id: str) -> List[Passage]:
        """Return passages ordered by source order."""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM passages WHERE source_id = ? ORDER BY order_index ASC",
                (source_id,),
            )
            return [self._row_to_passage(row) for row in cursor.fetchall()]

    def get_pages_by_source(self, source_id: str) -> List[WikiPage]:
        """Return pages associated with one source."""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.* FROM pages p
                JOIN page_sources ps ON ps.slug = p.slug
                WHERE ps.source_id = ?
                ORDER BY p.updated_at DESC
                """,
                (source_id,),
            )
            pages: List[WikiPage] = []
            for row in cursor.fetchall():
                slug = row["slug"]
                cursor.execute("SELECT source_id FROM page_sources WHERE slug = ?", (slug,))
                source_ids = [r["source_id"] for r in cursor.fetchall()]
                cursor.execute("SELECT to_slug FROM links WHERE from_slug = ?", (slug,))
                link_slugs = [r["to_slug"] for r in cursor.fetchall()]
                pages.append(self._row_to_page(row, source_ids, link_slugs))
            return pages

    # ========== Conversation CRUD ==========

    def insert_conversation(self, conversation: Conversation) -> None:
        """插入或更新会话记录"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO conversations (
                    conversation_id, source_id, title, participants,
                    created_at, updated_at, meta_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    conversation.conversation_id,
                    conversation.source_id,
                    conversation.title,
                    json_dumps(conversation.participants),
                    (conversation.created_at or datetime.utcnow()).isoformat(),
                    (conversation.updated_at or datetime.utcnow()).isoformat(),
                    json_dumps(conversation.meta_json),
                ),
            )
            conn.commit()

    def insert_turns(self, turns: List[Turn]) -> None:
        """批量插入会话回合"""
        if not turns:
            return
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM turns WHERE conversation_id = ?", (turns[0].conversation_id,))
            for turn in turns:
                cursor.execute(
                    """
                    INSERT INTO turns (
                        turn_id, conversation_id, role, content_text,
                        timestamp, order_index, meta_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        turn.turn_id,
                        turn.conversation_id,
                        turn.role,
                        turn.content_text,
                        turn.timestamp.isoformat() if turn.timestamp else None,
                        turn.order_index,
                        json_dumps(turn.meta_json),
                    ),
                )
            conn.commit()

    def get_conversation_by_source(self, source_id: str) -> Optional[Conversation]:
        """根据 source 获取会话"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations WHERE source_id = ? ORDER BY created_at DESC LIMIT 1",
                (source_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_conversation(row)

    def get_turns(self, conversation_id: str) -> List[Turn]:
        """获取会话全部 turn"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM turns WHERE conversation_id = ? ORDER BY order_index ASC",
                (conversation_id,),
            )
            return [self._row_to_turn(row) for row in cursor.fetchall()]

    def _row_to_conversation(self, row: sqlite3.Row) -> Conversation:
        return Conversation(
            conversation_id=row["conversation_id"],
            source_id=row["source_id"],
            title=row["title"],
            participants=json_loads(row["participants"]) if row["participants"] else [],
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
            meta_json=json_loads(row["meta_json"]),
        )

    def _row_to_turn(self, row: sqlite3.Row) -> Turn:
        return Turn(
            turn_id=row["turn_id"],
            conversation_id=row["conversation_id"],
            role=row["role"],
            content_text=row["content_text"],
            timestamp=datetime.fromisoformat(row["timestamp"]) if row["timestamp"] else None,
            order_index=row["order_index"],
            meta_json=json_loads(row["meta_json"]),
        )

    # ========== Ingest Run CRUD ==========

    def insert_ingest_run(self, run: IngestRun) -> None:
        """插入摄取运行记录"""
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ingest_runs (
                    run_id, source_ids, status, started_at, completed_at,
                    pages_created, passages_created, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run.run_id,
                json_dumps(run.source_ids),
                run.status.value if isinstance(run.status, IngestStatus) else run.status,
                (run.started_at or datetime.utcnow()).isoformat(),
                run.completed_at.isoformat() if run.completed_at else None,
                getattr(run, "pages_created", getattr(run, "new_pages", 0)),
                getattr(run, "passages_created", 0),
                getattr(run, "error_message", None) or (json_dumps(run.errors) if getattr(run, "errors", None) else None),
            ))
            conn.commit()

    def close(self) -> None:
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
