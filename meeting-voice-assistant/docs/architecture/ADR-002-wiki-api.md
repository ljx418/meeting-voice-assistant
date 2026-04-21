# ADR-002: Wiki 生成系统架构

## Status

Accepted

## Context

会议语音助手需要将会议记录转化为结构化的 Wiki 知识库文档。用户应能够：
1. 从会议转写和分析结果自动生成 Wiki 页面
2. 手动创建和编辑 Wiki 页面
3. 按分类和标签组织 Wiki 内容
4. 通过 GraphRAG 进行知识检索

**需求分析：**

| 需求 | 说明 |
|------|------|
| 会议转 Wiki | 将会议分析结果（摘要、关键点、行动项）自动生成 Wiki 页面 |
| Wiki 增删改查 | 支持 Wiki 页面的创建、读取、更新、删除 |
| 分类与标签 | 支持分类和多标签组织内容 |
| 版本历史 | 支持 Wiki 页面的历史版本 |
| GraphRAG 集成 | Wiki 内容可索引到 GraphRAG 进行知识查询 |
| 搜索功能 | 支持全文搜索和 GraphRAG 语义搜索 |

**约束条件：**
1. 复用现有 GraphRAG 存储（SQLite）
2. 使用现有 LLM 进行 Wiki 内容生成
3. Wiki 页面以 Markdown 格式存储
4. 支持未来扩展为多用户协作

---

## Decision

**采用模块化 Wiki 架构：**

```
┌─────────────────────────────────────────────────────────────────┐
│                      Wiki API Layer (FastAPI)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │ Page CRUD  │ │ Categories │ │   Tags     │ │  Search   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                      Wiki Service Layer                          │
│  ┌─────────────────────┐ ┌─────────────────────────────────┐  │
│  │ WikiPageService     │ │ WikiGeneratorService            │  │
│  │ (CRUD + 版本管理)    │ │ (会议 → Wiki 自动生成)           │  │
│  └─────────────────────┘ └─────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│                      Storage Layer (SQLite)                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   pages     │ │ categories  │ │    tags     │ │page_tags │ │
│  │ (Wiki页面)  │ │ (分类)      │ │ (标签)      │ │(多对多)   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
├─────────────────────────────────────────────────────────────────┤
│                   Integration Layer                               │
│  ┌─────────────────────┐ ┌─────────────────────────────────┐  │
│  │ GraphRAGIndexer     │ │ LLMGenerator                    │  │
│  │ (索引到知识图谱)     │ │ (LLM 生成 Wiki 内容)            │  │
│  └─────────────────────┘ └─────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### WikiPage

```sql
CREATE TABLE wiki_pages (
    id TEXT PRIMARY KEY,              -- UUID
    title TEXT NOT NULL,              -- 页面标题
    slug TEXT UNIQUE NOT NULL,        -- URL 友好的别名
    content TEXT NOT NULL DEFAULT '', -- Markdown 内容
    summary TEXT,                     -- 摘要（自动生成或手动）
    category_id TEXT,                 -- 外键到 categories
    meeting_id TEXT,                  -- 关联的会议 ID（可选）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT DEFAULT 'system',  -- 创建者
    version INTEGER DEFAULT 1,         -- 版本号
    is_published BOOLEAN DEFAULT FALSE,-- 是否发布
    FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE INDEX idx_wiki_pages_slug ON wiki_pages(slug);
CREATE INDEX idx_wiki_pages_category ON wiki_pages(category_id);
CREATE INDEX idx_wiki_pages_meeting ON wiki_pages(meeting_id);
```

### Category

```sql
CREATE TABLE categories (
    id TEXT PRIMARY KEY,              -- UUID
    name TEXT NOT NULL UNIQUE,        -- 分类名称
    slug TEXT UNIQUE NOT NULL,        -- URL 别名
    description TEXT,                 -- 分类描述
    parent_id TEXT,                   -- 父分类（支持层级）
    sort_order INTEGER DEFAULT 0,    -- 排序顺序
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id)
);

CREATE INDEX idx_categories_slug ON categories(slug);
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

### Tag

```sql
CREATE TABLE tags (
    id TEXT PRIMARY KEY,              -- UUID
    name TEXT NOT NULL UNIQUE,        -- 标签名称
    slug TEXT UNIQUE NOT NULL,        -- URL 别名
    color TEXT DEFAULT '#6B7280',     -- 标签颜色（前端展示用）
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE page_tags (
    page_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (page_id, tag_id),
    FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);
```

### PageVersion (版本历史)

```sql
CREATE TABLE page_versions (
    id TEXT PRIMARY KEY,
    page_id TEXT NOT NULL,
    version INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,              -- 变更说明
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (page_id) REFERENCES wiki_pages(id) ON DELETE CASCADE
);

CREATE INDEX idx_page_versions_page ON page_versions(page_id, version DESC);
```

---

## API Endpoints

### Wiki Pages

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wiki/pages` | 列表查询（支持分页、分类、标签过滤） |
| `GET` | `/api/v1/wiki/pages/{id}` | 获取单个页面 |
| `GET` | `/api/v1/wiki/pages/slug/{slug}` | 通过 slug 获取页面 |
| `POST` | `/api/v1/wiki/pages` | 创建新页面 |
| `PUT` | `/api/v1/wiki/pages/{id}` | 更新页面 |
| `DELETE` | `/api/v1/wiki/pages/{id}` | 删除页面 |
| `GET` | `/api/v1/wiki/pages/{id}/versions` | 获取版本历史 |
| `POST` | `/api/v1/wiki/pages/{id}/revert/{version}` | 恢复到指定版本 |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wiki/categories` | 获取所有分类（树形结构） |
| `GET` | `/api/v1/wiki/categories/{id}` | 获取单个分类 |
| `POST` | `/api/v1/wiki/categories` | 创建分类 |
| `PUT` | `/api/v1/wiki/categories/{id}` | 更新分类 |
| `DELETE` | `/api/v1/wiki/categories/{id}` | 删除分类 |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wiki/tags` | 获取所有标签 |
| `POST` | `/api/v1/wiki/tags` | 创建标签 |
| `PUT` | `/api/v1/wiki/tags/{id}` | 更新标签 |
| `DELETE` | `/api/v1/wiki/tags/{id}` | 删除标签 |

### Wiki Generation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/wiki/generate` | 从会议生成 Wiki 页面 |
| `GET` | `/api/v1/wiki/generate/preview` | 预览生成结果 |

### Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/wiki/search` | 全文搜索 |
| `POST` | `/api/v1/wiki/search/semantic` | GraphRAG 语义搜索 |

---

## API Request/Response Specifications

### POST /api/v1/wiki/generate

**Request:**
```json
{
  "meeting_id": "sess_abc123",
  "title": "项目启动会议纪要",
  "category_id": "cat_xxx",
  "tags": ["会议纪要", "项目"],
  "include_transcript": true,
  "include_analysis": true
}
```

**Response:**
```json
{
  "page": {
    "id": "wiki_xxx",
    "title": "项目启动会议纪要",
    "slug": "project-kickoff-meeting-2026-04-17",
    "content": "# 项目启动会议纪要\n\n## 摘要\n...\n\n## 关键点\n...\n\n## 行动项\n...\n\n## 转写记录\n...",
    "category_id": "cat_xxx",
    "meeting_id": "sess_abc123",
    "created_at": "2026-04-17T10:00:00Z",
    "is_published": false
  },
  "generation_stats": {
    "transcript_length": 1500,
    "generated_length": 800,
    "processing_time_ms": 2500
  }
}
```

### GET /api/v1/wiki/pages

**Query Parameters:**
- `page` (int): 页码，默认 1
- `page_size` (int): 每页数量，默认 20
- `category_id` (string, optional): 分类过滤
- `tag_id` (string, optional): 标签过滤
- `search` (string, optional): 搜索关键词
- `include_unpublished` (bool): 是否包含未发布页面，默认 false

**Response:**
```json
{
  "items": [
    {
      "id": "wiki_xxx",
      "title": "项目启动会议纪要",
      "slug": "project-kickoff-meeting-2026-04-17",
      "summary": "讨论了项目计划和分工...",
      "category": {"id": "cat_xxx", "name": "会议纪要"},
      "tags": [{"id": "tag_1", "name": "会议纪要"}, {"id": "tag_2", "name": "项目"}],
      "created_at": "2026-04-17T10:00:00Z",
      "updated_at": "2026-04-17T10:30:00Z",
      "is_published": true
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### GET /api/v1/wiki/search

**Query Parameters:**
- `q` (string): 搜索关键词
- `category_id` (string, optional): 分类过滤
- `limit` (int): 返回数量，默认 10

**Response:**
```json
{
  "query": "项目计划",
  "results": [
    {
      "page_id": "wiki_xxx",
      "title": "项目启动会议纪要",
      "slug": "project-kickoff-meeting-2026-04-17",
      "snippet": "...讨论了下一阶段的项目计划...",
      "relevance_score": 0.95
    }
  ],
  "total": 5
}
```

### POST /api/v1/wiki/search/semantic

**Request:**
```json
{
  "query": "项目计划和时间安排",
  "limit": 10,
  "category_id": "cat_xxx"
}
```

**Response:**
```json
{
  "query": "项目计划和时间安排",
  "results": [
    {
      "page_id": "wiki_xxx",
      "title": "项目启动会议纪要",
      "slug": "project-kickoff-meeting-2026-04-17",
      "snippet": "...讨论了下一阶段的项目计划和时间安排...",
      "community": "社区 1",
      "relevance_score": 0.92
    }
  ],
  "graph_context": {
    "entities": ["项目", "计划", "时间安排"],
    "relationships": ["项目-包含-计划", "计划-需要-时间安排"]
  }
}
```

---

## Wiki Content Generation Prompt

```markdown
你是一个专业的会议记录助手。请根据以下会议信息生成结构化的 Wiki 页面内容。

## 会议信息
- 会议主题: {meeting_title}
- 会议时间: {meeting_time}
- 参会人员: {speakers}

## 会议摘要
{summary}

## 关键点
{key_points}

## 行动项
{action_items}

## 转写记录
{transcript}

请生成符合以下格式的 Wiki 页面:
1. 使用 Markdown 格式
2. 包含摘要、关键点、行动项等标准章节
3. 使用适当的标题层级 (h1, h2, h3)
4. 行动项使用 - [ ] 未完成 / - [x] 已完成 格式
5. 保留关键引述
6. 生成目录链接
```

---

## Project Structure

```
backend/app/
├── api/v1/
│   ├── wiki/
│   │   ├── __init__.py
│   │   ├── router.py          # Wiki API 路由聚合
│   │   ├── pages.py           # Wiki 页面 CRUD
│   │   ├── categories.py      # 分类管理
│   │   ├── tags.py            # 标签管理
│   │   ├── generate.py        # Wiki 生成
│   │   └── search.py          # 搜索
│   └── main.py                 # FastAPI 入口
├── core/
│   └── wiki/
│       ├── __init__.py
│       ├── models.py           # Pydantic 模型
│       ├── service.py          # WikiService
│       ├── generator.py        # WikiGeneratorService
│       └── search.py           # SearchService
├── models/
│   └── wiki.py                 # SQLAlchemy 模型
└── storage/
    └── wiki_db.py              # Wiki 专用数据库操作
```

---

## Implementation Notes

### 1. ID Generation
使用 `uuid.uuid4().hex[:8]` 生成短 ID，前缀区分类型：
- `wiki_` - Wiki 页面
- `cat_` - 分类
- `tag_` - 标签

### 2. Slug Generation
从标题自动生成 URL 友好的 slug：
- 转小写
- 替换空格为 `-`
- 移除特殊字符
- 避免重复（追加数字后缀）

### 3. Version Control
- 每次 `PUT` 更新页面时，先保存当前版本到 `page_versions`
- 版本号递增
- `revert` 操作创建新版本，而非物理删除旧版本

### 4. GraphRAG Integration
- Wiki 页面创建/更新时，自动触发 GraphRAG 索引
- 删除页面时，从 GraphRAG 移除对应索引
- 使用 `meeting_id` 作为外部关联键

### 5. Caching Strategy
- Wiki 列表使用内存缓存（TTL: 5 分钟）
- 单个页面直接读取数据库
- 分类树结构缓存（TTL: 15 分钟）

---

## Consequences

### 变容易的事
- 会议记录自动转化为可搜索的知识库
- Wiki 内容通过 GraphRAG 支持语义搜索
- 结构化的内容组织（分类+标签）

### 变困难的事
- 引入新的数据库表和存储逻辑
- 需要处理 Wiki 生成的质量问题
- 多用户编辑冲突处理（未来扩展）

### 明确不解决的问题
- 多用户并发编辑冲突 → 需要 OT/CRDT 算法（未来）
- Wiki 页面富文本编辑器 → 前端实现
- 权限精确控制 → 复用 API Key 认证

---

## References

- [ADR-001: API Authentication](./ADR-001-api-authentication.md)
- [GraphRAG Integration](../graphrag/design.md)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
