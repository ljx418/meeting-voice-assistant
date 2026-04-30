"""
用户数据仓库

使用 SQLite 实现用户数据的持久化存储
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
import logging
import uuid

from app.core.auth import hash_password, verify_password

logger = logging.getLogger("app.db.user_repository")


class UserRepository:
    """用户数据仓库 - SQLite 实现"""

    def __init__(self, db_path: Optional[Path] = None):
        """初始化用户仓库"""
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "audio_cache" / "users.db"
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

            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL UNIQUE,
                    email TEXT NOT NULL UNIQUE,
                    hashed_password TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    is_superuser INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

            conn.commit()
            logger.info(f"[UserRepository] Database initialized at {self.db_path}")

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        """将 Row 转换为 dict"""
        d = dict(row)
        if 'is_active' in d:
            d['is_active'] = bool(d['is_active'])
        if 'is_superuser' in d:
            d['is_superuser'] = bool(d['is_superuser'])
        return d

    async def create_user(self, username: str, email: str, password: str) -> Optional[dict]:
        """创建用户"""
        # 检查用户名是否存在
        existing = self.get_user_by_username(username)
        if existing:
            logger.warning(f"[UserRepository] Username already exists: {username}")
            return None

        # 检查邮箱是否存在
        existing_email = self.get_user_by_email(email)
        if existing_email:
            logger.warning(f"[UserRepository] Email already exists: {email}")
            return None

        user_id = str(uuid.uuid4())
        hashed = hash_password(password)
        now = datetime.utcnow().isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (id, username, email, hashed_password, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, email, hashed, now, now))
            conn.commit()

        logger.info(f"[UserRepository] User created: {username} (id={user_id})")
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "is_active": True,
        }

    def get_user_by_username(self, username: str) -> Optional[dict]:
        """根据用户名获取用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """根据邮箱获取用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """根据 ID 获取用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    async def authenticate(self, username: str, password: str) -> Optional[dict]:
        """验证用户"""
        user = self.get_user_by_username(username)
        if not user:
            logger.warning(f"[UserRepository] Login failed: user not found - {username}")
            return None

        if not verify_password(password, user.get("hashed_password", "")):
            logger.warning(f"[UserRepository] Login failed: invalid password - {username}")
            return None

        if not user.get("is_active", True):
            logger.warning(f"[UserRepository] Login failed: user inactive - {username}")
            return None

        logger.info(f"[UserRepository] User authenticated: {username}")
        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "is_active": user.get("is_active", True),
        }


# 全局实例
_user_repo: Optional[UserRepository] = None


def get_user_repository() -> UserRepository:
    """获取用户仓库实例"""
    global _user_repo
    if _user_repo is None:
        _user_repo = UserRepository()
    return _user_repo