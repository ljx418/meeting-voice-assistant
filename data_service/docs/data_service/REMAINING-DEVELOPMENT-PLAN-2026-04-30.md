# 剩余开发计划

日期：2026-05-07

## 总目标

当前项目已重新收敛为独立的 MCP-first 本地知识治理服务。剩余开发目标不是把 `/knowledge` 做成普通用户知识消费产品，而是把服务能力治理化、契约化、可迁移化。

本服务作为最小可分粒度，应保留完整 MCP Server、CLI、HTTP API、控制台、GraphRAG 服务、LLMWiki 固化、workspace 存储、质量治理和本地安全边界。

## 已完成阶段

- `Phase 1` 稳定双引擎工作流。
- `Phase 2` distill 正式中间层。
- `Phase 3` GraphRAG 职责收口。
- `Phase 4` MCP / Agent 化收口，外部 HarnessOS 真实 stdio MCP 验收通过。
- `Phase 5.1` GraphRAG 图谱质量面板。
- `Phase 5.2` Workspace & Source Manager。
- `Phase 5.3` Refresh Operation UI。
- `Phase 5.4` Source Distill Trace。
- `Phase 5.5` Directory Watcher。
- `Phase 5.6` Low Signal Audit。

## Phase 5.7：Knowledge Service Console Productization

状态：下一阶段主线。

目标：

- 将 `/knowledge` 定位为 Local Knowledge Service Console。
- 面向开发者、运维者和上层应用集成者展示服务治理状态。
- 不作为会议、学习、面试、代码助手的终端用户 App。

控制台一级导航建议：

- Overview
- Workspaces
- Sources
- Build Operations
- Distill Units
- Wiki Artifacts
- GraphRAG
- Trace Explorer
- Quality Governance
- MCP Debugger
- Settings

P0 验收标准：

- 首屏展示当前服务状态、workspace 数量、最近 build 状态、失败 source 数、low-signal source 数、GraphRAG 图谱状态。
- Workspaces 使用 `workspace_id` 作为稳定 ID，展示绑定 `root_path`。
- Sources 展示递归扫描文件数量、source registry、failed/unreadable/low-signal sources。
- Build Operations 展示 queued/running/completed/failed/cancelled/blocked 和 stage/progress/error。
- Quality Governance 能查看 feedback、rules、review queue、correction plan。
- MCP Debugger 能列出当前稳定 MCP tool 分组和最近调用状态。
- 移动端无横向溢出；控制台信息密度以治理任务为主。

P1 验收标准：

- Trace Explorer 以 source 为中心展示 `source -> normalized -> distill units -> wiki -> graph -> retrieval hit -> quality impact`。
- GraphRAG 页展示 entity/relation/community 数量、quality diagnostics 和 graph snapshot。
- Distill Units 页支持按 unit kind、source、authority、low-signal、title-derived 筛选。
- Wiki Artifacts 页展示 pages/topics/sources 与 source trace 回跳。

P2 验收标准：

- CLI / HTTP / MCP 三入口能力矩阵在 Settings 或 MCP Debugger 中可见。
- 控制台错误状态区分 API key、allowlist、source path、build failure、GraphRAG native CLI failure。
- 危险动作明确展示影响范围和二次确认语义。

## Phase 5.8：Format Expansion

目标：

- 新增 `docx` extractor。
- 新增 `yaml/yml` extractor 或结构化文本解析。
- 在 CLI preflight、HTTP scan、MCP source import 和测试中声明支持。

验收标准：

- `docx` 文件能被抽取、蒸馏、进入 Wiki 和 GraphRAG 输入。
- `yaml/yml` 文件能按结构化 source 进入 normalize/distill。
- README 和 backend README 的当前支持格式更新。

## Phase 5.9：Typed Distill Units

目标：

- 将当前通用 distill units 升级为更适合上层应用复用的 typed units。
- 保持现有 `DistilledUnitKind` 兼容，新增映射层或 schema version。

目标 unit 类型：

- `definition`
- `concept`
- `claim`
- `decision`
- `task`
- `workflow`
- `constraint`
- `risk`
- `example`
- `misconception`
- `entity_evidence`
- `relation_evidence`
- `meeting_summary`
- `code_symbol`
- `code_dependency`
- `code_call_edge`
- `architecture_note`

验收标准：

- distill schema 新版本可表达 typed units。
- LLMWiki、GraphRAG、retrieval 和 quality 能消费新旧 unit。
- 会议转写和代码分析产物至少各有一组 typed unit fixture。

## Phase 6：Interface Convergence

目标：

- MCP 是默认主入口。
- CLI 和 HTTP 与 MCP 共享语义。
- 当前 `data_service`、`/api/v1/knowledge/*` 保持兼容，新增目标接口计划。

目标 MCP tools 分组：

- workspace
- source
- build
- query / retrieve
- graph
- distill
- trace
- quality

目标 CLI 形态：

```bash
knowledge workspace list
knowledge workspace create --name work --root /path/to/folder
knowledge scan --workspace work
knowledge build --workspace work
knowledge query --workspace work "..."
knowledge graph snapshot --workspace work
knowledge trace source --workspace work --source-id xxx
knowledge quality report --workspace work
knowledge mcp serve
knowledge http serve
```

目标 HTTP 形态：

```text
GET /api/workspaces
POST /api/workspaces
GET /api/workspaces/{id}
POST /api/workspaces/{id}/scan
POST /api/workspaces/{id}/build
GET /api/workspaces/{id}/sources
POST /api/workspaces/{id}/sources
GET /api/workspaces/{id}/sources/{source_id}/trace
POST /api/workspaces/{id}/query
POST /api/workspaces/{id}/retrieve
GET /api/workspaces/{id}/graph
POST /api/workspaces/{id}/graph/query
GET /api/workspaces/{id}/quality
POST /api/workspaces/{id}/quality/feedback
POST /api/workspaces/{id}/quality/rules
POST /api/workspaces/{id}/quality/correction-plan
```

## 回归要求

每次较大开发进展完成后运行：

```bash
python3 -m pytest backend/tests/test_data_service.py backend/tests/test_data_service_api.py backend/tests/test_data_service_mcp.py -q
```

必要时补充：

```bash
python3 -m pytest backend/tests/test_llmwiki.py -q
```

真实知识库回归继续使用：

```text
/Users/Zhuanz/Desktop/workspace/知识库/row/deepseek_split
```
