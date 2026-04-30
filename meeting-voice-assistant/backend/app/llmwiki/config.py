"""LLMWiki 配置管理"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Union


@dataclass
class LLMWikiConfig:
    """LLMWiki 配置"""

    CONFIG_DIRNAME = ".llmwiki"
    CONFIG_FILENAME = "config.json"

    # 工作空间目录。默认取命令执行时的当前终端路径，
    # 也可以通过 llmwiki workspace <path> 持久修改。
    workspace_path: Path = field(default_factory=lambda: Path.cwd())

    # 数据存储目录
    vault_path: Path = field(default_factory=lambda: Path("./llmwiki_vault"))

    # 是否复制原始文件到 vault
    copy_raw_files: bool = True

    # 是否启用 PDF 支持
    enable_pdf: bool = False

    # LLM 提供商: null (本地) / http (远程 API)
    llm_provider: str = "null"

    # HTTP API 端点
    llm_api_base: Optional[str] = None

    # API Key 环境变量名
    llm_api_key_env: Optional[str] = None

    # 模型名
    llm_model: str = "gpt-4.1-mini"

    # 超时和重试
    llm_timeout: float = 30.0
    llm_max_retries: int = 2

    # 摄取后是否自动编译 wiki 页面
    compile_on_ingest: bool = True

    # 最大 passage 字符数
    max_passage_chars: int = 1200

    # 重叠字符数
    overlap_chars: int = 150

    # 数据库路径
    db_path: Path = field(default_factory=lambda: Path("./llmwiki.db"))

    # Markdown 页面输出目录
    markdown_output_dir: Path = field(default_factory=lambda: Path("./llmwiki_markdown"))

    # 标准化抽取结果输出目录
    normalized_output_dir: Path = field(default_factory=lambda: Path("./llmwiki_normalized"))

    # 预处理后的可读文档目录
    readable_docs_dir: Path = field(default_factory=lambda: Path("./llmwiki_readable"))

    # summary 状态文件
    summary_path: Path = field(default_factory=lambda: Path("./llmwiki_summary.md"))

    @classmethod
    def from_env(cls) -> "LLMWikiConfig":
        """从环境变量加载配置"""
        workspace_path = cls.resolve_workspace_path()
        llmwiki_root = cls._resolve_optional_path(
            os.getenv("LLMWIKI_ARTIFACT_ROOT"),
            workspace_path / "llmwiki",
            base_dir=workspace_path,
        )
        return cls(
            workspace_path=workspace_path,
            vault_path=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_VAULT_PATH",
                default=llmwiki_root / "raw",
                legacy=workspace_path / "llmwiki_vault",
                base_dir=workspace_path,
            ),
            copy_raw_files=os.getenv("LLMWIKI_COPY_RAW_FILES", "true").lower() == "true",
            enable_pdf=os.getenv("LLMWIKI_ENABLE_PDF", "false").lower() == "true",
            llm_provider=os.getenv("LLMWIKI_LLM_PROVIDER", "null"),
            llm_api_base=os.getenv("LLMWIKI_LLM_API_BASE"),
            llm_api_key_env=os.getenv("LLMWIKI_LLM_API_KEY_ENV"),
            llm_model=os.getenv("LLMWIKI_LLM_MODEL", "gpt-4.1-mini"),
            llm_timeout=float(os.getenv("LLMWIKI_LLM_TIMEOUT", "30")),
            llm_max_retries=int(os.getenv("LLMWIKI_LLM_MAX_RETRIES", "2")),
            compile_on_ingest=os.getenv("LLMWIKI_COMPILE_ON_INGEST", "true").lower() == "true",
            max_passage_chars=int(os.getenv("LLMWIKI_MAX_PASSAGE_CHARS", "1200")),
            overlap_chars=int(os.getenv("LLMWIKI_OVERLAP_CHARS", "150")),
            db_path=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_DB_PATH",
                default=llmwiki_root / "state" / "llmwiki.db",
                legacy=workspace_path / "llmwiki.db",
                base_dir=workspace_path,
            ),
            markdown_output_dir=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_MARKDOWN_OUTPUT_DIR",
                default=llmwiki_root / "pages",
                legacy=workspace_path / "llmwiki_markdown",
                base_dir=workspace_path,
            ),
            normalized_output_dir=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_NORMALIZED_OUTPUT_DIR",
                default=llmwiki_root / "normalized",
                legacy=workspace_path / "llmwiki_normalized",
                base_dir=workspace_path,
            ),
            readable_docs_dir=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_READABLE_DOCS_DIR",
                default=llmwiki_root / "readable",
                legacy=workspace_path / "llmwiki_readable",
                base_dir=workspace_path,
            ),
            summary_path=cls._resolve_legacy_or_default_path(
                env_var="LLMWIKI_SUMMARY_PATH",
                default=workspace_path / "summary.md",
                legacy=workspace_path / "llmwiki_summary.md",
                base_dir=workspace_path,
            ),
        )

    @classmethod
    def resolve_workspace_path(cls, start_dir: Optional[Path] = None) -> Path:
        """解析当前生效的工作空间目录。"""
        start_dir = (start_dir or Path.cwd()).resolve()

        workspace_env = os.getenv("LLMWIKI_WORKSPACE")
        if workspace_env:
            return cls._resolve_path(Path(workspace_env).expanduser(), base_dir=start_dir)

        config_file = cls.find_workspace_config(start_dir)
        if config_file:
            try:
                data = json.loads(config_file.read_text(encoding="utf-8"))
                raw_path = data.get("workspace_path")
                if raw_path:
                    return cls._resolve_path(Path(raw_path).expanduser(), base_dir=config_file.parent)
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                pass

        return start_dir

    @classmethod
    def find_workspace_config(cls, start_dir: Optional[Path] = None) -> Optional[Path]:
        """从当前目录向上查找 workspace 配置文件。"""
        current = (start_dir or Path.cwd()).resolve()
        for directory in (current, *current.parents):
            candidate = directory / cls.CONFIG_DIRNAME / cls.CONFIG_FILENAME
            if candidate.exists():
                return candidate
        return None

    @classmethod
    def get_workspace_config_path(cls, start_dir: Optional[Path] = None) -> Path:
        """获取用于写入 workspace 配置的文件路径。"""
        existing = cls.find_workspace_config(start_dir)
        if existing:
            return existing
        anchor = (start_dir or Path.cwd()).resolve()
        return anchor / cls.CONFIG_DIRNAME / cls.CONFIG_FILENAME

    @classmethod
    def set_workspace(cls, workspace_path: Union[Path, str], start_dir: Optional[Path] = None) -> Path:
        """持久设置工作空间目录。"""
        anchor = (start_dir or Path.cwd()).resolve()
        workspace = cls._resolve_path(Path(workspace_path).expanduser(), base_dir=anchor)
        config_path = cls.get_workspace_config_path(anchor)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(
            json.dumps({"workspace_path": str(workspace)}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return config_path

    @classmethod
    def clear_workspace(cls, start_dir: Optional[Path] = None) -> Optional[Path]:
        """清除持久 workspace 配置。"""
        config_path = cls.find_workspace_config(start_dir)
        if config_path is None:
            return None
        config_path.unlink()
        try:
            config_path.parent.rmdir()
        except OSError:
            pass
        return config_path

    @staticmethod
    def _resolve_path(path: Path, base_dir: Path) -> Path:
        """将相对路径解析为绝对路径。"""
        if path.is_absolute():
            return path.resolve()
        return (base_dir / path).resolve()

    @classmethod
    def _resolve_optional_path(cls, raw_value: Optional[str], default: Path, base_dir: Path) -> Path:
        """解析可选路径配置，未提供时返回默认值。"""
        if not raw_value:
            return default.resolve()
        return cls._resolve_path(Path(raw_value).expanduser(), base_dir=base_dir)

    @classmethod
    def _resolve_legacy_or_default_path(
        cls,
        env_var: str,
        default: Path,
        legacy: Path,
        base_dir: Path,
    ) -> Path:
        raw_value = os.getenv(env_var)
        if raw_value:
            return cls._resolve_path(Path(raw_value).expanduser(), base_dir=base_dir)
        legacy = legacy.resolve()
        default = default.resolve()
        if legacy.exists() and not default.exists():
            return legacy
        return default

    def ensure_directories(self) -> None:
        """确保必要目录存在"""
        if isinstance(self.workspace_path, str):
            self.workspace_path = Path(self.workspace_path)
        if isinstance(self.vault_path, str):
            self.vault_path = Path(self.vault_path)
        if isinstance(self.db_path, str):
            self.db_path = Path(self.db_path)
        if isinstance(self.markdown_output_dir, str):
            self.markdown_output_dir = Path(self.markdown_output_dir)
        if isinstance(self.normalized_output_dir, str):
            self.normalized_output_dir = Path(self.normalized_output_dir)
        if isinstance(self.readable_docs_dir, str):
            self.readable_docs_dir = Path(self.readable_docs_dir)
        if isinstance(self.summary_path, str):
            self.summary_path = Path(self.summary_path)
        self.workspace_path = self.workspace_path.resolve()
        self.vault_path = self.vault_path.resolve()
        self.db_path = self.db_path.resolve()
        self.markdown_output_dir = self.markdown_output_dir.resolve()
        self.normalized_output_dir = self.normalized_output_dir.resolve()
        self.readable_docs_dir = self.readable_docs_dir.resolve()
        self.summary_path = self.summary_path.resolve()
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.markdown_output_dir.mkdir(parents=True, exist_ok=True)
        self.normalized_output_dir.mkdir(parents=True, exist_ok=True)
        self.readable_docs_dir.mkdir(parents=True, exist_ok=True)
        self.summary_path.parent.mkdir(parents=True, exist_ok=True)
