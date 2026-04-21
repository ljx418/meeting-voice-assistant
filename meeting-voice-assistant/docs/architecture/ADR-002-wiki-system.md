# ADR-002: Wiki 生成系统架构

## Status

Proposed

## Context

### 项目背景

会议语音助手项目在完成语音识别和会议分析后，需要一个知识管理模块来组织和存储生成的会议内容。当前 GraphRAG 系统负责知识图谱索引，但缺少一个结构化的文档/wiki 系统来：

1. 存储会议摘要、章节、关键点等结构化内容
2. 支持用户创建和编辑 wiki 页面
3. 与 GraphRAG 集成，实现文档的自动索引
4. 提供全文搜索和版本管理

### 需求分析

**功能需求：**
- 文档 CRUD（创建、读取、更新、删除）
- 文档版本历史
- 文档分类和标签
- 文档搜索（全文搜索）
- 与 GraphRAG 集成（自动索引入知识图谱）
- 与会议记录关联

**非功能需求：**
- 使用现有认证机制（API Key）
- 复用现有数据库（SQLite）
- 保持与现有架构的一致性
- 支持未来多用户扩展

**约束条件：**
- 使用 FastAPI 框架
- 使用 SQLite 作为主数据库（与现有系统一致）
- 复用现有 API Key 认证
- 不引入额外的外部依赖（如 Elasticsearch）

---

## Decision

### 1. 数据模型设计

#### 1.1 Wiki 文档模型

```python
# backend/app/models/wiki.py

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


class WikiDocument(BaseModel):
    """Wiki 文档模型"""
    id: str = Field(description="文档唯一 ID，格式: wiki_{uuid}")
    title: str = Field(description="文档标题")
    content: str = Field(description="文档内容 (Markdown)")
    doc_type: DocType = Field(description="文档类型")

    # 关联关系
    parent_id: Optional[str] = Field(default=None, description="父文档 ID，用于层级结构")
    meeting_id: Optional[str] = Field(default=None, description="关联的会议 ID")

    # 元数据
    tags: List[str] = Field(default_factory=list, description="标签列表")
    version: int = Field(default=1, description="版本号")
    is_deleted: bool = Field(default=False, description="软删除标记")

    # 审计字段
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
```

#### 1.2 文档关系模型

```python
class WikiDocumentRelationship(BaseModel):
    """文档关联关系"""
    id: str
    source_doc_id: str = Field(description="源文档 ID")
    target_doc_id: str = Field(description="目标文档 ID")
    relationship_type: str = Field(description="关系类型: 'related' | 'child' | '引用' | '来源'")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. API 端点设计

#### 2.1 文档管理

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/wiki/docs` | 创建文档 |
| GET | `/api/v1/wiki/docs` | 列出文档（支持分页、过滤） |
| GET | `/api/v1/wiki/docs/{doc_id}` | 获取文档详情 |
| PUT | `/api/v1/wiki/docs/{doc_id}` | 更新文档 |
| DELETE | `/api/v1/wiki/docs/{doc_id}` | 删除文档（软删除） |
| GET | `/api/v1/wiki/docs/{doc_id}/versions` | 获取版本历史 |
| POST | `/api/v1/wiki/docs/{doc_id}/restore/{version}` | 恢复到指定版本 |

#### 2.2 搜索与查询

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/api/v1/wiki/search` | 全文搜索 |
| GET | `/api/v1/wiki/docs/{doc_id}/children` | 获取子文档 |
| GET | `/api/v1/wiki/tags` | 获取所有标签 |

#### 2.3 会议集成

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/wiki/from-meeting/{meeting_id}` | 从会议生成 Wiki 文档 |
| GET | `/api/v1/wiki/by-meeting/{meeting_id}` | 获取会议关联的文档 |

#### 2.4 GraphRAG 集成

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/api/v1/wiki/docs/{doc_id}/index` | 手动触发索引 |
| POST | `/api/v1/wiki/index-all` | 批量索引所有文档 |

### 3. API 详细规范

#### 3.1 创建文档

**POST /api/v1/wiki/docs**

```json
// Request
{
  "title": "2024 Q1 战略会议",
  "content": "# 会议摘要\n\n## 关键决策\n\n1. ...",
  "doc_type": "meeting_summary",
  "parent_id": null,
  "meeting_id": "mtg_abc123",
  "tags": ["战略", "Q1", "2024"]
}

// Response 201
{
  "success": true,
  "data": {
    "id": "wiki_xyz789",
    "title": "2024 Q1 战略会议",
    "content": "...",
    "doc_type": "meeting_summary",
    "version": 1,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

#### 3.2 更新文档

**PUT /api/v1/wiki/docs/{doc_id}**

```json
// Request
{
  "title": "2024 Q1 战略会议（修订版）",
  "content": "# 会议摘要\n\n## 关键决策\n\n1. ...\n\n## 补充",
  "tags": ["战略", "Q1", "2024", "已修订"],
  "change_summary": "补充了讨论细节"
}

// Response 200
{
  "success": true,
  "data": {
    "id": "wiki_xyz789",
    "title": "2024 Q1 战略会议（修订版）",
    "version": 2,
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "message": "Document updated. Version 2 created."
}
```

#### 3.3 搜索文档

**GET /api/v1/wiki/search?q={query}&tags={tag1,tag2}&doc_type={type}&page={page}&size={size}**

```json
// Response 200
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "wiki_xyz789",
        "title": "2024 Q1 战略会议",
        "snippet": "...在<mark>Q1</mark>季度，我们讨论了...",
        "doc_type": "meeting_summary",
        "tags": ["战略", "Q1"],
        "updated_at": "2024-01-15T11:00:00Z"
      }
    ],
    "total": 42,
    "page": 1,
    "size": 20
  }
}
```

#### 3.4 从会议生成 Wiki

**POST /api/v1/wiki/from-meeting/{meeting_id}**

```json
// Request
{
  "doc_type": "meeting_summary",
  "include_sections": true,
  "tags": ["自动生成"]
}

// Response 202
{
  "success": true,
  "message": "Wiki document generation started",
  "data": {
    "job_id": "job_abc123",
    "document_id": "wiki_xyz789"
  }
}
```

### 4. 目录结构

```
backend/app/
├── api/v1/
│   └── wiki.py              # Wiki API 路由
├── core/
│   └── wiki/
│       ├── __init__.py
│       ├── service.py       # Wiki 业务逻辑
│       ├── search.py        # 搜索实现
│       ├── indexer.py       # GraphRAG 索引集成
│       └── templates.py     # 文档模板
├── models/
│   └── wiki.py              # Wiki Pydantic 模型
└── db/
    └── wiki_repository.py    # 数据库操作
```

### 5. 核心技术决策

#### 5.1 搜索方案

**方案 A: SQLite FTS5（推荐）**

```sql
-- 创建 FTS5 虚拟表
CREATE VIRTUAL TABLE wiki_fts USING fts5(
    title,
    content,
    tags,
    content='wiki_documents',
    content_rowid='rowid'
);
```

**优点：**
- SQLite 内置，无需额外依赖
- 性能良好，支持中文分词
- 与现有数据库一致

**缺点：**
- 不如 Elasticsearch 强大
- 无法分布式部署

**方案 B: PostgreSQL + pg_trgm**

不适合（现有系统使用 SQLite）。

**方案 C: 外部搜索服务（Elasticsearch/Meilisearch）**

增加部署复杂度，未来可扩展。

#### 5.2 版本控制策略

**方案 A: 全量存储每个版本**

每次更新存储完整的文档快照。

**优点：**
- 恢复简单
- 查询历史版本快

**缺点：**
- 存储成本高

**方案 B: 增量存储（git-like）**

只存储变更的增量。

**优点：**
- 存储成本低

**缺点：**
- 恢复需要重放
- 实现复杂

**决策：采用方案 A（全量存储）**

对于 Wiki 文档，存储成本不是主要瓶颈，实现简单更重要。

#### 5.3 GraphRAG 集成策略

**方案 A: 同步索引（创建/更新时自动索引）**

```python
async def create_document(doc: WikiDocument):
    # 1. 保存到数据库
    # 2. 同步调用 GraphRAG 索引
    await graphrag_service.index_document(doc)
```

**优点：**
- 简单直接

**缺点：**
- API 响应延迟增加
- 索引失败难以处理

**方案 B: 异步索引（事件驱动）**

```python
async def create_document(doc: WikiDocument):
    # 1. 保存到数据库
    # 2. 发布索引事件
    await event_bus.publish("wiki.document.created", {"doc_id": doc.id})

# 独立 Worker 处理索引
async def index_worker(message):
    await graphrag_service.index_document(doc_id)
```

**优点：**
- API 响应快
- 支持重试和错误处理

**缺点：**
- 需要消息队列（Redis）

**决策：采用方案 B（异步索引）+ 手动触发备选**

使用 SQLite 的简单队列表实现异步处理，不引入额外依赖。

### 6. 错误处理

| 错误码 | 描述 |
|--------|------|
| 404 | 文档不存在 |
| 409 | 版本冲突 |
| 422 | 参数校验失败 |
| 500 | 服务器内部错误 |

```json
// Error Response
{
  "success": false,
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document with ID 'wiki_xyz789' not found",
    "details": {}
  }
}
```

---

## Consequences

### 正面影响

1. **知识结构化**：会议内容自动生成为 Wiki，便于查阅和分享
2. **版本可控**：每次修改都有记录，可追溯可回滚
3. **搜索便捷**：FTS5 支持快速全文搜索
4. **GraphRAG 集成**：文档自动入知识图谱，支持知识关联查询
5. **向后兼容**：复用现有认证和数据库基础设施

### 负面影响 / Trade-offs

1. **数据冗余**：会议摘要同时存在于会议记录和 Wiki 文档
2. **一致性问题**：会议更新后，关联的 Wiki 不会自动同步
3. **FTS 性能**：SQLite FTS5 在超大规模文档（>10万）上性能有限
4. **无权限控制**：当前为单用户设计，所有文档对 API Key 持有者可见

### 数据迁移

现有 GraphRAG 的文档索引数据保持不变，Wiki 系统使用独立的表：

```sql
-- Wiki 文档表
CREATE TABLE wiki_documents (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    doc_type TEXT NOT NULL,
    parent_id TEXT,
    meeting_id TEXT,
    tags TEXT,  -- JSON array
    version INTEGER DEFAULT 1,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY (parent_id) REFERENCES wiki_documents(id)
);

-- 版本历史表
CREATE TABLE wiki_document_versions (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    FOREIGN KEY (document_id) REFERENCES wiki_documents(id)
);

-- FTS5 索引
CREATE VIRTUAL TABLE wiki_fts USING fts5(
    title,
    content,
    tags,
    content='wiki_documents',
    content_rowid='rowid'
);

-- 文档关系表
CREATE TABLE wiki_relationships (
    id TEXT PRIMARY KEY,
    source_doc_id TEXT NOT NULL,
    target_doc_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_doc_id) REFERENCES wiki_documents(id),
    FOREIGN KEY (target_doc_id) REFERENCES wiki_documents(id)
);
```

---

## Implementation Plan

### Phase 1: 基础框架

1. 创建 `backend/app/models/wiki.py` - Pydantic 模型
2. 创建数据库表和迁移脚本
3. 创建 `backend/app/db/wiki_repository.py` - 数据访问层
4. 创建 `backend/app/core/wiki/service.py` - 业务逻辑层
5. 创建 `backend/app/api/v1/wiki.py` - API 路由

### Phase 2: 搜索功能

1. 创建 FTS5 虚拟表和触发器
2. 实现 `backend/app/core/wiki/search.py` - 搜索服务
3. 添加搜索 API 端点

### Phase 3: 版本管理

1. 实现版本创建逻辑（更新时自动创建版本快照）
2. 添加版本查询和恢复 API

### Phase 4: GraphRAG 集成

1. 实现 `backend/app/core/wiki/indexer.py` - 索引服务
2. 添加手动触发索引 API
3. 实现从会议生成 Wiki 的功能

### Phase 5: 文档模板

1. 创建常用模板（会议纪要、项目文档）
2. 实现模板应用 API

---

## Alternatives Considered

### 1. 使用外部 Wiki 系统（Notion/Obsidian）

**优点：**
- 功能完善，开箱即用

**缺点：**
- 丧失数据控制权
- 需要维护第三方集成
- 不适合本地部署

**结论**：自建 Wiki 更符合项目需求。

### 2. 使用 PostgreSQL 替代 SQLite

**优点：**
- 更好的并发性能
- 更好的全文搜索（pg_trgm）

**缺点：**
- 增加部署复杂度
- 与现有架构不一致

**结论**：保持 SQLite，减少复杂度。

### 3. 使用 Meilisearch 作为搜索服务

**优点：**
- 搜索性能更强
- 支持中文分词

**缺点：**
- 增加额外服务
- 增加部署复杂度

**结论**：当前阶段使用 SQLite FTS5 足够，未来可升级。

---

## Open Questions

1. **文档层级深度**：是否限制文档的层级深度（如最大 3 级）？
2. **模板市场**：是否需要支持导入/导出模板，形成模板市场？
3. **多语言内容**：是否需要支持文档内容的国际化（i18n）？
4. **文档权限**：未来多用户时，是否需要文档级别的权限控制？

---

## References

- [SQLite FTS5 文档](https://www.sqlite.org/fts5.html)
- [FastAPI APIRouter 最佳实践](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [ADR-001: API 认证方案](./ADR-001-api-authentication.md)
