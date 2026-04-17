# ADR-002: Wiki 生成系统架构

## Status

Proposed

## Context

会议语音助手需要将会议记录转换为可管理的知识库。当前系统可以将会议录音转写为文本并通过 LLM 分析，但：

1. **缺乏统一的知识管理**：每次会议的转写、摘要、行动项分散存储
2. **GraphRAG 索引未自动化**：需要手动触发 GraphRAG 索引流程
3. **长期任务和工作流追踪缺失**：无法从会议中提取和追踪跨会议的任务和工作流

需要一个 Wiki 生成系统，实现：
- 监控指定目录（如 `/wiki_input/`）中的会议记录文件
- 自动触发 GraphRAG 索引
- 提取和展示实体摘要、长期任务、工作流

---

## Decision

### 1. 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Wiki Generation System                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐     ┌─────────────────┐     ┌─────────────┐ │
│  │ FileWatcher  │────>│  WikiService    │────>│ GraphRAG    │ │
│  │ (watchdog)   │     │                 │     │ Service     │ │
│  └──────────────┘     └────────┬────────┘     │ (:8002)     │ │
│         ▲                      │              └─────────────┘ │
│         │                      ▼                                │
│  ┌──────────────┐     ┌─────────────────┐                      │
│  │ APScheduler  │     │   WikiDB        │                      │
│  │ (定期扫描)    │────>│   (SQLite)      │                      │
│  └──────────────┘     └─────────────────┘                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     REST API (:8000)                             │
│  POST /api/v1/wiki/config   - 配置输入源                        │
│  POST /api/v1/wiki/generate - 触发生成                          │
│  GET  /api/v1/wiki/status   - 获取状态                          │
│  GET  /api/v1/wiki/summary  - 获取摘要                          │
│  GET  /api/v1/wiki/tasks    - 获取长期任务                       │
│  GET  /api/v1/wiki/workflows - 获取工作流                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2. 数据模型

#### 2.1 WikiSource（输入源配置）

```python
class WikiSource(BaseModel):
    """Wiki 输入源配置"""
    id: str = Field(default_factory=lambda: f"src_{uuid.uuid4().hex[:8]}")
    name: str = Field(description="输入源名称")
    path: Path = Field(description="监控目录路径")
    enabled: bool = Field(default=True)
    scan_interval_seconds: int = Field(default=300, description="扫描间隔（秒）")
    auto_index: bool = Field(default=True, description="文件变更时自动触发索引")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### 2.2 WikiDocument（已索引文档）

```python
class WikiDocument(BaseModel):
    """已索引的 Wiki 文档"""
    id: str = Field(default_factory=lambda: f"doc_{uuid.uuid4().hex[:8]}")
    source_id: str = Field(description="关联的 WikiSource ID")
    file_path: str = Field(description="原始文件路径")
    file_name: str = Field(description="文件名")
    title: Optional[str] = Field(description="文档标题（从文件名或内容提取）")
    content_hash: str = Field(description="内容哈希，用于检测变更")
    indexed_at: Optional[datetime] = Field(description="索引时间")
    index_status: Literal["pending", "indexing", "indexed", "failed"] = Field(default="pending")
    error_message: Optional[str] = Field(description="索引失败错误信息")
    graphrag_doc_id: Optional[str] = Field(description="GraphRAG 文档 ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### 2.3 WikiEntity（实体）

```python
class WikiEntity(BaseModel):
    """Wiki 实体（从 GraphRAG 提取）"""
    id: str = Field(default_factory=lambda: f"ent_{uuid.uuid4().hex[:8]}")
    name: str = Field(description="实体名称")
    entity_type: str = Field(description="实体类型：person/organization/project/task")
    description: Optional[str] = Field(description="实体描述")
    source_document_ids: List[str] = Field(default_factory=list, description="来源文档 ID 列表")
    long_term_task_count: int = Field(default=0, description="关联的长期任务数量")
    community_id: Optional[str] = Field(description="所属社区 ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

#### 2.4 WikiWorkflow（工作流）

```python
class WikiWorkflow(BaseModel):
    """工作流（从会议中提取）"""
    id: str = Field(default_factory=lambda: f"wf_{uuid.uuid4().hex[:8]}")
    name: str = Field(description="工作流名称")
    description: Optional[str] = Field(description="工作流描述")
    steps: List[WorkflowStep] = Field(default_factory=list)
    source_document_ids: List[str] = Field(default_factory=list)
    status: Literal["active", "completed", "paused"] = Field(default="active")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class WorkflowStep(BaseModel):
    """工作流步骤"""
    step_order: int = Field(description="步骤顺序（从 1 开始）")
    name: str = Field(description="步骤名称")
    description: Optional[str] = Field(description="步骤描述")
    assignee: Optional[str] = Field(description="负责人")
    due_date: Optional[datetime] = Field(description="截止日期")
    status: Literal["pending", "in_progress", "completed", "blocked"] = Field(default="pending")
    depends_on: List[int] = Field(default_factory=list, description="依赖的步骤序号列表")
```

#### 2.5 LongTermTask（长期任务）

```python
class LongTermTask(BaseModel):
    """长期任务（跨会议追踪）"""
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    title: str = Field(description="任务标题")
    description: Optional[str] = Field(description="任务描述")
    assignee: Optional[str] = Field(description="负责人")
    due_date: Optional[datetime] = Field(description="截止日期")
    priority: Literal["high", "medium", "low"] = Field(default="medium")
    status: Literal["open", "in_progress", "completed", "cancelled"] = Field(default="open")
    related_entity_ids: List[str] = Field(default_factory=list, description="关联实体 ID")
    source_document_ids: List[str] = Field(default_factory=list, description="来源文档 ID")
    progress_notes: List[ProgressNote] = Field(default_factory=list, description="进度记录")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ProgressNote(BaseModel):
    """进度记录"""
    timestamp: datetime = Field(default_factory=datetime.now)
    note: str = Field(description="进度说明")
    source_document_id: Optional[str] = Field(description="来源文档")
```

---

### 3. API 端点设计

#### 3.1 POST /api/v1/wiki/config

配置 Wiki 输入源。

**Request:**
```json
{
  "name": "会议记录输入源",
  "path": "/path/to/wiki_input",
  "scan_interval_seconds": 300,
  "auto_index": true
}
```

**Response (201):**
```json
{
  "success": true,
  "source": {
    "id": "src_abc123",
    "name": "会议记录输入源",
    "path": "/path/to/wiki_input",
    "scan_interval_seconds": 300,
    "auto_index": true,
    "enabled": true,
    "created_at": "2026-04-16T10:00:00Z"
  }
}
```

#### 3.2 POST /api/v1/wiki/generate

手动触发 Wiki 生成（扫描并索引）。

**Request:**
```json
{
  "source_id": "src_abc123",
  "force_reindex": false
}
```

**Response (202):**
```json
{
  "success": true,
  "job_id": "job_def456",
  "message": "Wiki 生成任务已提交",
  "estimated_documents": 5
}
```

#### 3.3 GET /api/v1/wiki/status

获取生成任务状态。

**Query Parameters:**
- `job_id` (optional): 指定任务 ID，不提供则返回最新任务状态

**Response (200):**
```json
{
  "success": true,
  "job": {
    "job_id": "job_def456",
    "source_id": "src_abc123",
    "status": "running",
    "progress": 60,
    "total_documents": 5,
    "indexed_documents": 3,
    "failed_documents": 0,
    "started_at": "2026-04-16T10:05:00Z",
    "updated_at": "2026-04-16T10:07:00Z",
    "error_message": null
  }
}
```

#### 3.4 GET /api/v1/wiki/summary

获取 Wiki 摘要。

**Response (200):**
```json
{
  "success": true,
  "summary": {
    "total_documents": 25,
    "indexed_documents": 23,
    "pending_documents": 2,
    "total_entities": 156,
    "entity_types": {
      "person": 45,
      "organization": 23,
      "project": 67,
      "task": 21
    },
    "total_workflows": 8,
    "active_workflows": 5,
    "total_long_term_tasks": 12,
    "open_tasks": 8
  }
}
```

#### 3.5 GET /api/v1/wiki/tasks

获取长期任务列表。

**Query Parameters:**
- `status` (optional): 过滤任务状态 (open/in_progress/completed/cancelled)
- `assignee` (optional): 按负责人过滤
- `limit` (optional): 返回数量限制，默认 50
- `offset` (optional): 分页偏移，默认 0

**Response (200):**
```json
{
  "success": true,
  "tasks": [
    {
      "id": "task_ghi789",
      "title": "完成产品路线图规划",
      "description": "在 Q2 前完成 2026 年产品路线图",
      "assignee": "张三",
      "due_date": "2026-06-30T00:00:00Z",
      "priority": "high",
      "status": "in_progress",
      "related_entity_ids": ["ent_xxx", "ent_yyy"],
      "progress_notes": [
        {
          "timestamp": "2026-04-10T10:00:00Z",
          "note": "已完成初步调研",
          "source_document_id": "doc_aaa"
        }
      ],
      "created_at": "2026-04-01T10:00:00Z",
      "updated_at": "2026-04-10T10:00:00Z"
    }
  ],
  "total": 12,
  "limit": 50,
  "offset": 0
}
```

#### 3.6 GET /api/v1/wiki/workflows

获取工作流列表。

**Query Parameters:**
- `status` (optional): 过滤工作流状态 (active/completed/paused)
- `limit` (optional): 返回数量限制，默认 50
- `offset` (optional): 分页偏移，默认 0

**Response (200):**
```json
{
  "success": true,
  "workflows": [
    {
      "id": "wf_jkl012",
      "name": "产品发布流程",
      "description": "从需求到发布的完整流程",
      "steps": [
        {
          "step_order": 1,
          "name": "需求评审",
          "description": "评审需求文档",
          "assignee": "产品经理",
          "status": "completed"
        },
        {
          "step_order": 2,
          "name": "开发实现",
          "description": "完成功能开发",
          "assignee": "开发团队",
          "depends_on": [1],
          "status": "in_progress"
        },
        {
          "step_order": 3,
          "name": "测试验证",
          "description": "完成测试",
          "assignee": "测试团队",
          "depends_on": [2],
          "status": "pending"
        }
      ],
      "status": "active",
      "source_document_ids": ["doc_bbb", "doc_ccc"],
      "created_at": "2026-04-05T10:00:00Z",
      "updated_at": "2026-04-15T10:00:00Z"
    }
  ],
  "total": 8,
  "limit": 50,
  "offset": 0
}
```

---

### 4. 定时任务框架

#### 4.1 双重机制设计

采用 **Watchdog 事件驱动 + APScheduler 兜底** 的双重机制：

```
┌─────────────────────────────────────────────────────────────┐
│                    WikiTaskScheduler                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────┐      ┌─────────────────────────┐  │
│  │   FileWatcher       │      │    APScheduler          │  │
│  │   (watchdog)        │      │    (兜底扫描)            │  │
│  │                     │      │                         │  │
│  │  - 实时响应文件变更   │      │  - 每 N 分钟扫描一次     │  │
│  │  - 低延迟            │      │  - 进程重启后恢复        │  │
│  │  - 可能漏检（重启）   │      │  - 确保无遗漏           │  │
│  └──────────┬──────────┘      └──────────┬──────────────┘  │
│             │                            │                  │
│             └──────────┬─────────────────┘                  │
│                        ▼                                    │
│              ┌─────────────────┐                           │
│              │  TaskQueue      │                           │
│              │  (去重 + 合并)   │                           │
│              └────────┬────────┘                           │
│                       ▼                                    │
│              ┌─────────────────┐                           │
│              │  WikiIndexer    │                           │
│              │  (实际索引任务)   │                           │
│              └─────────────────┘                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

#### 4.2 WikiTaskScheduler 实现

```python
class WikiTaskScheduler:
    """Wiki 定时任务调度器"""

    def __init__(self):
        self.scheduler = APScheduler()
        self.watchers: Dict[str, FileWatcher] = {}
        self.indexing_queue: asyncio.Queue = asyncio.Queue()
        self._start_worker()

    def add_source(self, source: WikiSource) -> None:
        """添加 Wiki 输入源并启动监控"""
        # 启动 Watchdog 监控
        watcher = FileWatcher(source.path, source.id)
        watcher.on_created = lambda f: self._queue_index(source.id, f)
        watcher.on_modified = lambda f: self._queue_index(source.id, f)
        watcher.start()
        self.watchers[source.id] = watcher

        # 添加 APScheduler 定时扫描
        self.scheduler.add_job(
            func=self._scheduled_scan,
            trigger="interval",
            seconds=source.scan_interval_seconds,
            args=[source.id],
            id=f"scan_{source.id}",
            replace_existing=True,
        )

    def remove_source(self, source_id: str) -> None:
        """移除 Wiki 输入源并停止监控"""
        if source_id in self.watchers:
            self.watchers[source_id].stop()
            del self.watchers[source_id]
        self.scheduler.remove_job(f"scan_{source_id}")

    async def _queue_index(self, source_id: str, file_path: Path) -> None:
        """将索引任务加入队列（去重）"""
        # 实现去重逻辑，避免同一文件多次入队
        await self.indexing_queue.put((source_id, file_path))

    async def _scheduled_scan(self, source_id: str) -> None:
        """定时扫描任务"""
        source = WikiDB.get_source(source_id)
        if not source or not source.enabled:
            return

        for file_path in source.path.glob("*.txt"):
            await self._queue_index(source_id, file_path)

    async def _start_worker(self) -> None:
        """启动索引工作协程"""
        while True:
            source_id, file_path = await self.indexing_queue.get()
            await self._process_index(source_id, file_path)

    async def _process_index(self, source_id: str, file_path: Path) -> None:
        """处理单个文件索引"""
        # 1. 检查文件是否已索引或正在索引
        # 2. 调用 GraphRAG API 索引
        # 3. 更新 WikiDocument 状态
        # 4. 提取实体、工作流、长期任务
        pass
```

#### 4.3 GraphRAG 索引集成

```python
async def index_to_graphrag(file_path: Path) -> str:
    """调用 GraphRAG API 索引文档"""
    async with aiohttp.ClientSession() as session:
        # 调用 GraphRAG 索引端点
        with open(file_path, 'rb') as f:
            form = aiohttp.FormData()
            form.add_field('file', f, filename=file_path.name)
            async with session.post(
                f"{config.GRAPHRAG_ENDPOINT}/api/v1/index/",
                data=form,
                timeout=aiohttp.ClientTimeout(total=300)
            ) as resp:
                if resp.status != 200:
                    raise Exception(f"GraphRAG indexing failed: {await resp.text()}")
                result = await resp.json()
                return result.get("document_id", "")
```

---

### 5. 数据库 Schema

```sql
-- Wiki 输入源表
CREATE TABLE wiki_sources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    scan_interval_seconds INTEGER DEFAULT 300,
    auto_index BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wiki 文档表
CREATE TABLE wiki_documents (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    title TEXT,
    content_hash TEXT NOT NULL,
    indexed_at TIMESTAMP,
    index_status TEXT DEFAULT 'pending',
    error_message TEXT,
    graphrag_doc_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES wiki_sources(id)
);

-- Wiki 实体表
CREATE TABLE wiki_entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    source_document_ids TEXT,  -- JSON array
    long_term_task_count INTEGER DEFAULT 0,
    community_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Wiki 工作流表
CREATE TABLE wiki_workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    steps TEXT NOT NULL,  -- JSON array of WorkflowStep
    source_document_ids TEXT,  -- JSON array
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 长期任务表
CREATE TABLE long_term_tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    assignee TEXT,
    due_date TIMESTAMP,
    priority TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    related_entity_ids TEXT,  -- JSON array
    source_document_ids TEXT,  -- JSON array
    progress_notes TEXT,  -- JSON array of ProgressNote
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引任务表
CREATE TABLE index_jobs (
    id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    total_documents INTEGER DEFAULT 0,
    indexed_documents INTEGER DEFAULT 0,
    failed_documents INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES wiki_sources(id)
);
```

---

## Consequences

### 变容易的事

- **自动化知识管理**：文件放入监控目录后自动索引，无需手动操作
- **跨会议追踪**：长期任务和工作流可在多个会议中持续追踪
- **GraphRAG 集成**：通过 Wiki 系统统一触发 GraphRAG 索引

### 变困难的事

- **依赖 GraphRAG**：系统依赖 GraphRAG 服务的可用性
- **实体提取准确性**：从非结构化文本提取高质量实体需要 LLM 质量
- **去重和合并**：同一实体在不同文档中可能出现，需要去重逻辑

### 需要考虑的问题

1. **文件格式**：初期仅支持 `.txt`，后续可扩展支持 `.md`、`.pdf`
2. **并发索引**：大量文件同时变更时的并发控制
3. **错误恢复**：索引失败后的重试策略

---

## Implementation Phases

### Phase 1: 核心框架
1. 创建 `WikiTaskScheduler` 类
2. 实现 SQLite 数据库表
3. 实现基础 API 端点

### Phase 2: 文件监控
1. 集成 watchdog FileWatcher
2. 集成 APScheduler 定时扫描
3. 实现任务队列去重

### Phase 3: GraphRAG 集成
1. 调用 GraphRAG `/api/v1/index/` 端点
2. 解析 GraphRAG 响应，提取实体
3. 实现 WikiEntity、WikiWorkflow、LongTermTask 提取

### Phase 4: API 完善
1. 实现 `/wiki/summary` 聚合查询
2. 实现 `/wiki/tasks` 和 `/wiki/workflows` 查询
3. 添加分页和过滤支持

---

## References

- [APScheduler 文档](https://apscheduler.readthedocs.io/)
- [watchdog 文档](https://pythonhosted.org/watchdog/)
- ADR-001: API 认证方案
- GraphRAG 集成设计 (2026-04-16-system-architecture-analysis.md)
