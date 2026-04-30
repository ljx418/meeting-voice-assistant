"""
版本管理模块 - 文件变更历史记录与回滚

功能：
- 记录文件变更历史
- 支持版本回滚
- 文件差异计算

使用方式:
    from app.core.version_control import VersionControl, get_version_control

    vc = VersionControl()
    versions = vc.get_versions("/path/to/file")
    vc.rollback("/path/to/file", version_id)
"""

import hashlib
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger("version_control")


# ============================================================================
# 常量配置
# ============================================================================

VERSION_DIR_NAME = ".versions"
METADATA_FILE = "metadata.json"
MAX_VERSIONS_PER_FILE = 50  # 单文件最大版本数


# ============================================================================
# 数据结构
# ============================================================================

@dataclass
class FileVersion:
    """文件版本信息"""
    version_id: str
    file_path: str
    content_hash: str
    file_size: int
    created_at: datetime
    comment: str = ""
    is_current: bool = True

    def to_dict(self) -> dict:
        return {
            "version_id": self.version_id,
            "file_path": self.file_path,
            "content_hash": self.content_hash,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
            "comment": self.comment,
            "is_current": self.is_current,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FileVersion":
        return cls(
            version_id=data["version_id"],
            file_path=data["file_path"],
            content_hash=data["content_hash"],
            file_size=data["file_size"],
            created_at=datetime.fromisoformat(data["created_at"]),
            comment=data.get("comment", ""),
            is_current=data.get("is_current", True),
        )


@dataclass
class DiffResult:
    """文件差异结果"""
    has_diff: bool
    added_lines: List[str] = field(default_factory=list)
    removed_lines: List[str] = field(default_factory=list)
    unchanged_lines: List[str] = field(default_factory=list)


# ============================================================================
# 版本管理器
# ============================================================================

class VersionControl:
    """
    文件版本管理器

    功能：
    - 自动记录文件变更历史
    - 支持版本回滚
    - 文件差异计算

    版本存储结构:
        .versions/
        └── /path/to/file.txt/
            ├── metadata.json        # 版本元数据
            ├── v1_hash1234.txt     # 版本文件副本
            ├── v2_hash5678.txt
            └── ...
    """

    def __init__(self, version_root: Optional[Path] = None):
        """
        初始化版本管理器

        Args:
            version_root: 版本存储根目录（默认为文件同级目录的 .versions）
        """
        self._version_root = version_root
        self._metadata_cache: Dict[str, dict] = {}

    def _get_version_root(self, file_path: Optional[str] = None) -> Path:
        """获取版本根目录"""
        if self._version_root:
            return self._version_root

        if file_path:
            return Path(file_path).parent / VERSION_DIR_NAME

        return Path.cwd() / VERSION_DIR_NAME

    def _get_file_version_dir(self, file_path: str) -> Path:
        """获取文件的版本目录"""
        # 使用文件路径的 hash 作为目录名，避免路径中的特殊字符问题
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:12]
        safe_name = Path(file_path).name.replace("/", "_").replace("\\", "_")
        return self._get_version_root(file_path) / f"{safe_name}_{path_hash}"

    def _get_metadata_path(self, version_dir: Path) -> Path:
        """获取元数据文件路径"""
        return version_dir / METADATA_FILE

    def _load_metadata(self, version_dir: Path) -> dict:
        """加载元数据"""
        metadata_path = self._get_metadata_path(version_dir)

        if version_dir in self._metadata_cache:
            return self._metadata_cache[version_dir]

        if metadata_path.exists():
            try:
                data = json.loads(metadata_path.read_text())
                self._metadata_cache[version_dir] = data
                return data
            except Exception as e:
                logger.error(f"[VersionControl] Failed to load metadata: {e}")

        return {"versions": [], "current_version": None}

    def _save_metadata(self, version_dir: Path, metadata: dict):
        """保存元数据"""
        metadata_path = self._get_metadata_path(version_dir)
        version_dir.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
        self._metadata_cache[version_dir] = metadata

    def _compute_hash(self, file_path: str) -> str:
        """计算文件内容 hash"""
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _generate_version_id(self) -> str:
        """生成版本 ID"""
        import uuid
        return uuid.uuid4().hex[:12]

    def _get_version_file_name(self, version: FileVersion) -> str:
        """获取版本文件名"""
        return f"v{version.version_id}_{version.content_hash[:8]}.{Path(version.file_path).suffix}"

    # ------------------------------------------------------------------------
    # 公共 API
    # ------------------------------------------------------------------------

    def record_version(
        self,
        file_path: str,
        comment: str = "",
        force: bool = False,
    ) -> Optional[FileVersion]:
        """
        记录文件新版本

        Args:
            file_path: 文件路径
            comment: 版本注释
            force: 是否强制记录（即使内容没变）

        Returns:
            FileVersion: 新版本信息，失败返回 None
        """
        if not os.path.exists(file_path):
            logger.error(f"[VersionControl] File not found: {file_path}")
            return None

        try:
            # 计算当前内容 hash
            content_hash = self._compute_hash(file_path)
            file_size = os.path.getsize(file_path)

            # 获取版本目录
            version_dir = self._get_file_version_dir(file_path)
            version_dir.mkdir(parents=True, exist_ok=True)

            # 加载当前元数据
            metadata = self._load_metadata(version_dir)

            # 检查是否内容已存在（忽略小改动）
            existing = [
                v for v in metadata.get("versions", [])
                if v["content_hash"] == content_hash
            ]
            if existing and not force:
                logger.debug(f"[VersionControl] Content unchanged, skipping: {file_path}")
                return None

            # 创建新版本
            version_id = self._generate_version_id()
            version = FileVersion(
                version_id=version_id,
                file_path=file_path,
                content_hash=content_hash,
                file_size=file_size,
                created_at=datetime.now(),
                comment=comment,
                is_current=True,
            )

            # 保存版本文件副本
            version_file_name = self._get_version_file_name(version)
            version_file_path = version_dir / version_file_name
            shutil.copy2(file_path, version_file_path)

            # 更新元数据
            # 先将旧版本标记为非当前
            for v in metadata.get("versions", []):
                v["is_current"] = False

            # 添加新版本
            metadata["versions"].append(version.to_dict())
            metadata["current_version"] = version_id

            # 限制版本数量
            if len(metadata["versions"]) > MAX_VERSIONS_PER_FILE:
                # 删除最老的版本
                oldest = metadata["versions"].pop(0)
                oldest_file = version_dir / self._get_version_file_name(
                    FileVersion.from_dict(oldest)
                )
                if oldest_file.exists():
                    oldest_file.unlink()

            # 保存元数据
            self._save_metadata(version_dir, metadata)

            logger.info(
                f"[VersionControl] Recorded version {version_id} for {file_path}"
            )
            return version

        except Exception as e:
            logger.error(f"[VersionControl] Failed to record version: {e}")
            return None

    def get_versions(self, file_path: str) -> List[FileVersion]:
        """
        获取文件的所有版本

        Args:
            file_path: 文件路径

        Returns:
            List[FileVersion]: 版本列表（按时间倒序）
        """
        version_dir = self._get_file_version_dir(file_path)

        if not version_dir.exists():
            return []

        metadata = self._load_metadata(version_dir)
        versions = [
            FileVersion.from_dict(v)
            for v in metadata.get("versions", [])
        ]

        # 按时间倒序
        versions.sort(key=lambda v: v.created_at, reverse=True)
        return versions

    def get_current_version(self, file_path: str) -> Optional[FileVersion]:
        """
        获取文件当前版本信息

        Args:
            file_path: 文件路径

        Returns:
            FileVersion: 当前版本，失败返回 None
        """
        versions = self.get_versions(file_path)
        for v in versions:
            if v.is_current:
                return v
        return versions[0] if versions else None

    def get_version(self, file_path: str, version_id: str) -> Optional[FileVersion]:
        """
        获取指定版本信息

        Args:
            file_path: 文件路径
            version_id: 版本 ID

        Returns:
            FileVersion: 版本信息，失败返回 None
        """
        versions = self.get_versions(file_path)
        for v in versions:
            if v.version_id == version_id:
                return v
        return None

    def get_version_file_path(self, file_path: str, version_id: str) -> Optional[str]:
        """
        获取版本文件路径

        Args:
            file_path: 文件路径
            version_id: 版本 ID

        Returns:
            str: 版本文件路径，失败返回 None
        """
        version = self.get_version(file_path, version_id)
        if not version:
            return None

        version_dir = self._get_file_version_dir(file_path)
        version_file_name = self._get_version_file_name(version)
        version_file_path = version_dir / version_file_name

        if version_file_path.exists():
            return str(version_file_path)

        return None

    def rollback(
        self,
        file_path: str,
        version_id: str,
        create_backup: bool = True,
    ) -> bool:
        """
        回滚文件到指定版本

        Args:
            file_path: 文件路径
            version_id: 版本 ID
            create_backup: 是否先创建当前版本的备份

        Returns:
            bool: 是否成功
        """
        if not os.path.exists(file_path):
            logger.error(f"[VersionControl] File not found: {file_path}")
            return False

        try:
            version_file = self.get_version_file_path(file_path, version_id)
            if not version_file:
                logger.error(f"[VersionControl] Version not found: {version_id}")
                return False

            # 创建当前版本备份
            if create_backup:
                self.record_version(file_path, comment="Backup before rollback")

            # 复制版本文件覆盖当前文件
            shutil.copy2(version_file, file_path)

            # 更新元数据：当前版本标记
            version_dir = self._get_file_version_dir(file_path)
            metadata = self._load_metadata(version_dir)

            for v in metadata.get("versions", []):
                v["is_current"] = (v["version_id"] == version_id)

            metadata["current_version"] = version_id
            self._save_metadata(version_dir, metadata)

            logger.info(f"[VersionControl] Rolled back {file_path} to version {version_id}")
            return True

        except Exception as e:
            logger.error(f"[VersionControl] Rollback failed: {e}")
            return False

    def compute_diff(
        self,
        file_path: str,
        version_id1: str,
        version_id2: Optional[str] = None,
    ) -> DiffResult:
        """
        计算文件差异

        Args:
            file_path: 文件路径
            version_id1: 版本1 ID
            version_id2: 版本2 ID（None 表示当前版本）

        Returns:
            DiffResult: 差异结果
        """
        # 获取两个版本的文件路径
        version1_path = self.get_version_file_path(file_path, version_id1)

        if version_id2:
            version2_path = self.get_version_file_path(file_path, version_id2)
        else:
            # 与当前文件比较
            version2_path = file_path

        if not version1_path:
            logger.error(f"[VersionControl] Version not found: {version_id1}")
            return DiffResult(has_diff=False)

        if not os.path.exists(version2_path):
            logger.error(f"[VersionControl] File not found: {version2_path}")
            return DiffResult(has_diff=False)

        try:
            with open(version1_path, "r", encoding="utf-8", errors="replace") as f:
                lines1 = f.readlines()

            with open(version2_path, "r", encoding="utf-8", errors="replace") as f:
                lines2 = f.readlines()

            # 简单行比较
            set1 = set(lines1)
            set2 = set(lines2)

            added = list(set2 - set1)
            removed = list(set1 - set2)
            unchanged = list(set1 & set2)

            return DiffResult(
                has_diff=bool(added or removed),
                added_lines=added,
                removed_lines=removed,
                unchanged_lines=unchanged,
            )

        except Exception as e:
            logger.error(f"[VersionControl] Diff computation failed: {e}")
            return DiffResult(has_diff=False)

    def delete_versions(self, file_path: str, keep_current: bool = True) -> int:
        """
        删除文件的所有版本

        Args:
            file_path: 文件路径
            keep_current: 是否保留当前版本

        Returns:
            int: 删除的版本数
        """
        version_dir = self._get_file_version_dir(file_path)

        if not version_dir.exists():
            return 0

        try:
            metadata = self._load_metadata(version_dir)
            versions = metadata.get("versions", [])

            deleted_count = 0
            if keep_current:
                # 保留当前版本，删除其他
                current_id = metadata.get("current_version")
                for v in versions:
                    if v["version_id"] != current_id:
                        v_obj = FileVersion.from_dict(v)
                        version_file = version_dir / self._get_version_file_name(v_obj)
                        if version_file.exists():
                            version_file.unlink()
                        deleted_count += 1
            else:
                # 删除所有版本
                for v in versions:
                    v_obj = FileVersion.from_dict(v)
                    version_file = version_dir / self._get_version_file_name(v_obj)
                    if version_file.exists():
                        version_file.unlink()
                    deleted_count += 1

            # 删除元数据文件
            if keep_current and deleted_count > 0:
                # 更新元数据，只保留当前版本
                current_versions = [v for v in versions if v.get("is_current")]
                metadata["versions"] = current_versions
                self._save_metadata(version_dir, metadata)
            elif not keep_current:
                metadata_path = self._get_metadata_path(version_dir)
                if metadata_path.exists():
                    metadata_path.unlink()

            logger.info(f"[VersionControl] Deleted {deleted_count} versions for {file_path}")
            return deleted_count

        except Exception as e:
            logger.error(f"[VersionControl] Failed to delete versions: {e}")
            return 0

    def get_all_tracked_files(self) -> List[str]:
        """
        获取所有被跟踪的文件

        Returns:
            List[str]: 文件路径列表
        """
        tracked = []
        version_root = self._get_version_root()

        if not version_root.exists():
            return []

        for item in version_root.iterdir():
            if item.is_dir() and item.name != METADATA_FILE:
                metadata = self._load_metadata(item)
                for v in metadata.get("versions", []):
                    if v.get("is_current"):
                        tracked.append(v["file_path"])
                        break

        return tracked


# ============================================================================
# 全局实例管理
# ============================================================================

_global_vc: Optional[VersionControl] = None


def get_version_control(version_root: Optional[Path] = None) -> VersionControl:
    """
    获取全局版本控制器实例

    Args:
        version_root: 版本存储根目录

    Returns:
        VersionControl: 版本控制器实例
    """
    global _global_vc

    if _global_vc is None:
        _global_vc = VersionControl(version_root=version_root)

    return _global_vc


def record_file_version(
    file_path: str,
    comment: str = "",
    force: bool = False,
) -> Optional[FileVersion]:
    """
    快速记录文件版本

    Args:
        file_path: 文件路径
        comment: 版本注释
        force: 是否强制记录

    Returns:
        FileVersion: 版本信息
    """
    vc = get_version_control()
    return vc.record_version(file_path, comment, force)


def rollback_file(
    file_path: str,
    version_id: str,
    create_backup: bool = True,
) -> bool:
    """
    快速回滚文件

    Args:
        file_path: 文件路径
        version_id: 版本 ID
        create_backup: 是否创建备份

    Returns:
        bool: 是否成功
    """
    vc = get_version_control()
    return vc.rollback(file_path, version_id, create_backup)