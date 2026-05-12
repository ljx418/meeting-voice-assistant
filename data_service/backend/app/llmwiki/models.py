"""LLMWiki 数据模型"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


def generate_id() -> str:
    """生成 UUID"""
    return str(uuid.uuid4())


class SourceType(str, Enum):
    """来源类型"""
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    PDF = "pdf"
    PPTX = "pptx"
    PPT = "ppt"
    DOCX = "docx"
    YAML = "yaml"
    CHAT_JSON = "chat_json"


class SectionKind(str, Enum):
    """章节类型"""
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    SLIDE = "slide"
    TURN = "turn"
    CODE = "code"


class PageKind(str, Enum):
    """页面类型"""
    SOURCE_NOTE = "source_note"
    TOPIC = "topic"
    CONVERSATION_NOTE = "conversation_note"
    INDEX = "index"


class IngestStatus(str, Enum):
    """摄取状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


class Authority(str, Enum):
    """权威级别"""
    PRIMARY_DOC = "PRIMARY_DOC"
    SECONDARY_CHAT = "SECONDARY_CHAT"
    DERIVED_WIKI = "DERIVED_WIKI"


@dataclass
class SourceRecord:
    """源记录"""
    source_id: str = field(default_factory=generate_id)
    source_type: str = SourceType.TEXT.value
    authority: str = Authority.PRIMARY_DOC.value
    original_path: Optional[str] = None
    stored_path: Optional[str] = None
    sha256: Optional[str] = None
    title: Optional[str] = None
    mime: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    extractor_name: Optional[str] = None
    extractor_version: Optional[str] = None
    status: str = IngestStatus.PENDING.value
    error: Optional[str] = None
    content_hash: Optional[str] = None
    compiled_at: Optional[datetime] = None
    compile_status: str = "pending"
    compile_error: Optional[str] = None
    compiled_by_model: Optional[str] = None
    stale_reason: Optional[str] = None
    meta_json: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NormalizedSection:
    """规范化章节"""
    section_id: str = field(default_factory=generate_id)
    source_id: str = ""
    kind: str = SectionKind.PARAGRAPH.value
    title: Optional[str] = None
    text: str = ""
    locator: Dict[str, Any] = field(default_factory=dict)  # {"kind": "lines", "start": int, "end": int, ...}
    order_index: int = 0
    meta_json: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Passage:
    """段落（用于检索）"""
    passage_id: str = field(default_factory=generate_id)
    source_id: str = ""
    section_id: str = ""
    text: str = ""
    cjk_terms: str = ""  # Space-separated CJK n-grams
    token_count_est: int = 0
    locator: Dict[str, Any] = field(default_factory=dict)
    order_index: int = 0


@dataclass
class WikiPage:
    """Wiki 页面"""
    slug: str = ""
    title: str = ""
    kind: str = PageKind.SOURCE_NOTE.value
    summary: str = ""
    body_md: str = ""
    source_ids: List[str] = field(default_factory=list)
    link_slugs: List[str] = field(default_factory=list)
    version: int = 1
    updated_at: Optional[datetime] = None
    markdown_path: Optional[str] = None
    content_hash: Optional[str] = None
    compiled_at: Optional[datetime] = None
    compile_status: str = "pending"
    compile_error: Optional[str] = None
    compiled_by_model: Optional[str] = None
    stale_reason: Optional[str] = None
    meta_json: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Citation:
    """引用"""
    source_id: str = ""
    locator: Dict[str, Any] = field(default_factory=dict)
    label: str = ""
    excerpt: Optional[str] = None


@dataclass
class Conversation:
    """对话"""
    conversation_id: str = field(default_factory=generate_id)
    source_id: Optional[str] = None
    title: Optional[str] = None
    participants: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    meta_json: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Turn:
    """对话回合"""
    turn_id: str = field(default_factory=generate_id)
    conversation_id: str = ""
    role: str = ""  # user / assistant / system
    content_text: str = ""
    timestamp: Optional[datetime] = None
    order_index: int = 0
    meta_json: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PageLink:
    """页面链接"""
    from_slug: str = ""
    to_slug: str = ""
    link_text: Optional[str] = None


@dataclass
class IngestRun:
    """摄取运行记录"""
    run_id: str = field(default_factory=generate_id)
    source_ids: List[str] = field(default_factory=list)
    status: str = IngestStatus.PENDING.value
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_files: int = 0
    success_files: int = 0
    failed_files: int = 0
    new_pages: int = 0
    updated_pages: int = 0
    skipped_files: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
