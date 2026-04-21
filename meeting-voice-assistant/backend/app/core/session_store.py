"""
会话状态持久化模块

使用 SQLite 存储 WebSocket 会话状态，支持断线重连后恢复会话。
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from app.config import config
from app.utils.logger import setup_logger

logger = setup_logger("session_store")


class SessionStatus(str, Enum):
    """会话状态"""
    IDLE = "idle"
    RECORDING = "recording"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class TranscriptRecord:
    """转写记录"""
    text: str
    start_time: float
    end_time: float
    speaker: str
    confidence: float
    is_final: bool


@dataclass
class SessionState:
    """会话状态"""
    session_id: str
    status: SessionStatus
    transcripts_json: str  # JSON 序列化的转写列表
    audio_chunks_count: int
    audio_file_path: Optional[str]  # 音频数据文件路径
    seq: int  # 当前序列号
    created_at: str
    updated_at: str

    def get_transcripts(self) -> list[TranscriptRecord]:
        """反序列化转写记录"""
        if not self.transcripts_json:
            return []
        try:
            data = json.loads(self.transcripts_json)
            return [TranscriptRecord(**t) for t in data]
        except (json.JSONDecodeError, TypeError):
            return []


class SessionStore:
    """
    SQLite 会话存储

    会话状态持久化，支持:
    - 创建/更新会话
    - 根据 session_id 查询会话
    - 会话过期清理
    """

    _instance: Optional["SessionStore"] = None

    def __init__(self):
        self.db_path = Path(config.cache.cache_dir) / "sessions.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    @classmethod
    def get_instance(cls) -> "SessionStore":
        """获取单例实例（同步版本）"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _init_db(self) -> None:
        """初始化数据库表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'idle',
                transcripts_json TEXT DEFAULT '[]',
                audio_chunks_count INTEGER DEFAULT 0,
                audio_file_path TEXT,
                seq INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_updated_at
            ON sessions(updated_at)
        """)
        conn.commit()
        logger.info(f"Session store initialized at {self.db_path}")

    def _get_conn(self) -> sqlite3.Connection:
        """获取数据库连接"""
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def create_session(self, session_id: str) -> SessionState:
        """创建新会话"""
        now = datetime.now().isoformat()
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (session_id, status, transcripts_json, audio_chunks_count, seq, created_at, updated_at)
            VALUES (?, ?, '[]', 0, 0, ?, ?)
        """, (session_id, SessionStatus.IDLE.value, now, now))
        conn.commit()
        logger.info(f"Created session: {session_id}")
        return SessionState(
            session_id=session_id,
            status=SessionStatus.IDLE,
            transcripts_json="[]",
            audio_chunks_count=0,
            audio_file_path=None,
            seq=0,
            created_at=now,
            updated_at=now
        )

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """获取会话状态"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return SessionState(
                session_id=row["session_id"],
                status=SessionStatus(row["status"]),
                transcripts_json=row["transcripts_json"] or "[]",
                audio_chunks_count=row["audio_chunks_count"] or 0,
                audio_file_path=row["audio_file_path"],
                seq=row["seq"] or 0,
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
        return None

    def update_session(
        self,
        session_id: str,
        status: Optional[SessionStatus] = None,
        transcripts: Optional[list[TranscriptRecord]] = None,
        audio_chunks_count: Optional[int] = None,
        audio_file_path: Optional[str] = None,
        seq: Optional[int] = None
    ) -> Optional[SessionState]:
        """更新会话状态"""
        conn = self._get_conn()
        cursor = conn.cursor()

        updates = []
        params = []

        if status is not None:
            updates.append("status = ?")
            params.append(status.value)
        if transcripts is not None:
            updates.append("transcripts_json = ?")
            params.append(json.dumps([asdict(t) for t in transcripts]))
        if audio_chunks_count is not None:
            updates.append("audio_chunks_count = ?")
            params.append(audio_chunks_count)
        if audio_file_path is not None:
            updates.append("audio_file_path = ?")
            params.append(audio_file_path)
        if seq is not None:
            updates.append("seq = ?")
            params.append(seq)

        if not updates:
            return self.get_session(session_id)

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(session_id)

        cursor.execute(f"""
            UPDATE sessions SET {', '.join(updates)}
            WHERE session_id = ?
        """, params)
        conn.commit()

        logger.debug(f"Updated session {session_id}: {updates}")
        return self.get_session(session_id)

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Deleted session: {session_id}")
        return deleted

    def cleanup_expired_sessions(self, max_age_seconds: int = 3600) -> int:
        """
        清理过期会话

        Args:
            max_age_seconds: 会话最大存活时间（秒），默认 1 小时

        Returns:
            删除的会话数量
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        cutoff = datetime.now().isoformat()

        # 计算过期时间（使用 Python 而不是 SQL，因为 SQLite 不支持 interval）
        from datetime import timedelta
        cutoff_time = datetime.now() - timedelta(seconds=max_age_seconds)
        cutoff_str = cutoff_time.isoformat()

        cursor.execute("""
            DELETE FROM sessions
            WHERE updated_at < ?
        """, (cutoff_str,))

        deleted_count = cursor.rowcount
        conn.commit()

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired sessions (older than {max_age_seconds}s)")
        return deleted_count

    def get_active_sessions(self, limit: int = 100) -> list[SessionState]:
        """获取活跃会话列表"""
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM sessions
            WHERE status IN ('idle', 'recording', 'processing')
            ORDER BY updated_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [
            SessionState(
                session_id=row["session_id"],
                status=SessionStatus(row["status"]),
                transcripts_json=row["transcripts_json"] or "[]",
                audio_chunks_count=row["audio_chunks_count"] or 0,
                audio_file_path=row["audio_file_path"],
                seq=row["seq"] or 0,
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            )
            for row in rows
        ]


# 同步全局实例（用于不需要异步的场景）
_session_store_sync: Optional[SessionStore] = None


def get_session_store_sync() -> SessionStore:
    """获取同步全局会话存储实例"""
    global _session_store_sync
    if _session_store_sync is None:
        _session_store_sync = SessionStore()
    return _session_store_sync
