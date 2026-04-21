"""
Wiki 文档数据模型

基于 ADR-002 设计文档实现
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocType(str, Enum):
    """文档类型"""
    MEETING_SUMMARY = "meeting_summary"  # 会议摘要
    MEETING_NOTES = "meeting_notes"      # 会议记录
    CHAPTER = "chapter"                  # 章节/段落
    PAGE = "page"                         # 普通页面
    TEMPLATE = "template"                 # 模板


class WikiDocumentBase(BaseModel):
    """Wiki 文档基础模型"""
    title: str = Field(description="文档标题")
    content: str = Field(description="文档内容 (Markdown)")
    doc_type: DocType = Field(description="文档类型")
    parent_id: Optional[str] = Field(default=None, description="父文档 ID")
    meeting_id: Optional[str] = Field(default=None, description="关联的会议 ID")
    tags: List[str] = Field(default_factory=list, description="标签列表")


class WikiDocumentCreate(WikiDocumentBase):
    """创建 Wiki 文档请求"""
    pass


class WikiDocumentUpdate(BaseModel):
    """更新 Wiki 文档请求"""
    title: Optional[str] = Field(default=None, description="文档标题")
    content: Optional[str] = Field(default=None, description="文档内容")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")
    parent_id: Optional[str] = Field(default=None, description="父文档 ID")
    change_summary: Optional[str] = Field(default=None, description="变更说明")


class WikiDocument(WikiDocumentBase):
    """Wiki 文档完整模型"""
    id: str = Field(description="文档唯一 ID")
    version: int = Field(default=1, description="版本号")
    is_deleted: bool = Field(default=False, description="软删除标记")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, description="创建者")


class WikiDocumentVersion(BaseModel):
    """文档版本历史"""
    id: str = Field(description="版本记录 ID")
    document_id: str = Field(description="文档 ID")
    version: int = Field(description="版本号")
    title: str = Field(description="文档标题（快照）")
    content: str = Field(description="文档内容（快照）")
    change_summary: Optional[str] = Field(default=None, description="变更说明")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(default=None, description="修改者")


class WikiDocumentRelationship(BaseModel):
    """文档关联关系"""
    id: str = Field(description="关系 ID")
    source_doc_id: str = Field(description="源文档 ID")
    target_doc_id: str = Field(description="目标文档 ID")
    relationship_type: str = Field(description="关系类型: related/child/reference/source")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WikiSearchResult(BaseModel):
    """搜索结果项"""
    id: str
    title: str
    snippet: str = Field(description="搜索结果片段，高亮关键词")
    doc_type: DocType
    tags: List[str]
    updated_at: datetime


class WikiSearchResponse(BaseModel):
    """搜索响应"""
    items: List[WikiSearchResult]
    total: int
    page: int
    size: int


class WikiIndexRequest(BaseModel):
    """索引请求"""
    include_sections: bool = Field(default=True, description="是否包含章节")
    tags: Optional[List[str]] = Field(default=None, description="额外标签")


class WikiIndexResponse(BaseModel):
    """索引响应"""
    success: bool
    document_id: str
    entities_count: int = 0
    relationships_count: int = 0
    message: str = ""


class WikiFromMeetingRequest(BaseModel):
    """从会议生成 Wiki 请求"""
    doc_type: DocType = Field(default=DocType.MEETING_SUMMARY)
    include_sections: bool = Field(default=True)
    tags: Optional[List[str]] = Field(default=None)


class APIResponse(BaseModel):
    """通用 API 响应"""
    success: bool = True
    data: Optional[dict] = None
    message: Optional[str] = None


class APIError(BaseModel):
    """API 错误响应"""
    success: bool = False
    error: dict = Field(description="错误详情")


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[dict]
    total: int
    page: int
    size: int