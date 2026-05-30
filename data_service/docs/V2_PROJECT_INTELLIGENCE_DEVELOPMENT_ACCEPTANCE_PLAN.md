# V2 Development and Acceptance Plan: Project Intelligence MVP

## Summary

V2.0 先交付一个可被外部 Agent 稳定调用的 Project Intelligence MVP，而不是一次性完成 DevWiki、Code Graph、Quality 全量扩展。MVP 闭环为：导入 codebase -> 生成 snapshot -> 抽取 public surface 和 Python symbols -> 建立 surface/symbol/evidence 映射 -> 通过 HTTP/MCP/CLI 暴露 -> 生成 task-aware Agent Context Pack。

V2.0 必须基于当前 V1 底座扩展：复用 workspace、MCP registry、target HTTP envelope、query/trace/quality 的合同思想；但 codebase asset、code artifacts、code graph artifacts 独立持久化，不混入现有 source registry，也不继续扩大 `backend/app/api/v1/data_service.py` 和 `backend/data_service/service.py`。

## Development Plan

### PR 1：Codebase Registry + Artifact Foundation

目标：建立 V2 codebase asset 独立注册表和 artifact layout。

关键实现：

- 新增 `backend/data_service/code_assets/` package，包含 registry、models、artifact paths、schema constants。
- 新增独立 HTTP router，例如 `backend/app/api/v1/code_assets.py`，并在 API bootstrap 中注册。
- 新增 MCP module `backend/data_service/mcp_code_tools.py`，注册 `knowledge_codebase_import`。
- CLI 新增 `knowledge code import`。
- 持久化位置使用：
  `workspace/assets/codebase/{codebase_id}/codebase.json`

合同要求：

- `codebase_id` 默认生成规则：`codebase_` + normalized repo name；同 workspace 内唯一。
- `CodebaseAsset.status`：`active | archived | blocked | missing_path | permission_denied`
- 所有 artifact 包含 `schema_version`, `created_at`, `updated_at`, `workspace_id`, `codebase_id`。
- import path 必须在 workspace root 或 configured allowed roots 下。
- 默认 response 返回 repo-relative path；debug/admin 以外不返回 absolute path。

验收：

- 可导入当前 `data_service` repo。
- 重复导入同一路径返回已有 codebase。
- 非 allowed root 路径返回 `PATH_NOT_ALLOWED`。
- archive 后不作为默认 active codebase。
- 不修改现有 source registry。

### PR 2：Repo Snapshot + File Manifest

目标：生成稳定、可复读的 repo snapshot。

关键实现：

- 新增 snapshot service，扫描文件树、语言、LOC、重要路径、git metadata。
- 生成：
  `snapshot.json`, `files.jsonl`, `stats.json`, `warnings.jsonl`
- 支持 ignore policy：`.git`, `.venv`, `node_modules`, `dist`, `build`, `__pycache__`，并默认跳过 `.env`、credentials、private keys、binary、超大文件。

合同要求：

- `snapshot_id` 基于 commit_sha、dirty fingerprint、scan policy hash；无 git 时基于 file manifest hash。
- warning 类型至少包含：`IGNORED`, `BINARY_SKIPPED`, `FILE_TOO_LARGE`, `UNREADABLE`, `SYMLINK_SKIPPED`, `PARTIAL_SCAN`。
- 状态：`queued | running | completed | failed | canceled | stale`，V2.0 可以同步执行，但 artifact 中保留状态字段。

验收：

- 当前 repo snapshot 成功。
- 输出 README/docs/config/tests/frontend/backend/entrypoints。
- dirty git state 可记录。
- 不可读文件或超限文件不导致全局失败。
- 同一代码状态和 scan policy 下 snapshot_id 稳定。

### PR 3：Public Surface Inventory

目标：抽取 HTTP API、MCP tools、CLI commands、frontend API usage，并按 capability 聚合。

关键实现：

- 新增 inventory extractors：FastAPI route、MCP registry、CLI parser/static branch、frontend API client。
- 生成 `surfaces.jsonl`, `capabilities.jsonl`, `alignment_matrix.json`。
- 首发 HTTP API：
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory`
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces`

合同要求：

- `surface_id` deterministic：
  `http:{METHOD}:{PATH}`, `mcp:{tool_name}`, `cli:{command path}`, `frontend:{page_or_api}`。
- `stability`：`target | legacy | internal | experimental | unknown`
- 每个 surface 必须包含 source file、line range、extractor、confidence。
- unresolved capability 显式标记，不允许静默归类。

验收：

- 当前 repo 至少识别 FastAPI app、target/legacy HTTP routes、MCP stdio tools、`data-service`/`knowledge` CLI、Vue console entry。
- 当前 40 个 MCP tools 可被识别。
- 输出 HTTP/MCP/CLI 对齐矩阵。
- README 与代码的明显不一致可作为 warning 输出。

### PR 4：Python Symbol Index

目标：用 AST 抽取 Python 符号和 import 依赖。

关键实现：

- 新增 Python AST extractor。
- 生成 `symbols.jsonl`, `imports.jsonl`。
- 首发 HTTP API：
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols`
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/symbols/{symbol_id}`
- MCP 新增 `knowledge_code_symbol_search`。
- CLI 新增 `knowledge code symbols`。

合同要求：

- 支持 `module | class | function | method | import | constant`。
- `symbol_id` 使用 `py:{kind}:{qualified_name}`；冲突时加 path hash。
- 每个 symbol 包含 path、line_range、signature、docstring、decorators、visibility、confidence。
- 语法错误文件生成 warning，不中断全局索引。

验收：

- 当前 backend Python 文件可解析。
- 能检索 handler、MCP tool handler、CLI parser 相关 symbols。
- import graph 可输出模块依赖摘要。
- 语法错误 fixture 被隔离。

### PR 5：Surface-to-Symbol Mapping + Code Evidence Trace

目标：把 public surface 追踪到 handler symbol、source file、line range。

关键实现：

- 新增 mapping service 和 evidence service。
- 生成 `mappings.jsonl`, `evidence.jsonl`。
- 首发 HTTP API：
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/surface/{surface_id}`
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/symbol/{symbol_id}`
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/trace/capability/{capability}`
- MCP 新增 `knowledge_public_surface_trace`。
- CLI 新增 `knowledge code trace` 可作为只读命令。

合同要求：

- `evidence_id` 基于 path + line range + extractor hash。
- mapping relation：`HANDLED_BY`, `REGISTERED_BY`, `EXPOSED_BY`, `IMPLEMENTS_CAPABILITY`, `EVIDENCED_BY`。
- mapping 失败必须输出 `unresolved` 和原因。
- 所有 inferred mapping 必须有 confidence。

验收：

- source import、query、build、quality 等核心能力能 trace 到 HTTP/MCP/CLI surface 和关键文件行号。
- 能从 capability 找到 surfaces，再到 symbols，再到 evidence。
- unresolved mapping 不被当作成功。
- evidence path 默认 repo-relative。

### PR 6：MCP / HTTP / CLI Read API Convergence

目标：让 V2 MVP 的主要读能力三端对齐。

首发 MCP tools：

- `knowledge_codebase_import`
- `knowledge_codebase_snapshot`
- `knowledge_project_inventory`
- `knowledge_code_symbol_search`
- `knowledge_public_surface_trace`

首发 HTTP：

- codebase import/list/describe/archive
- snapshot create/list/get
- inventory/surfaces
- symbols
- trace

首发 CLI：

- `knowledge code import`
- `knowledge code snapshot`
- `knowledge code inventory`
- `knowledge code symbols`
- `knowledge code trace`

验收：

- 三端输入输出 envelope 一致。
- MCP tool schema、HTTP request/response、CLI JSON 输出可互相映射。
- 不新增 legacy wrapper。
- 现有 V1 MCP tools、HTTP routes、CLI commands 不破坏。

### PR 7：Agent Context Pack MVP

目标：生成 task-aware、证据驱动、token-budget aware 的 Agent Context Pack。

关键实现：

- 新增 context pack service，消费 snapshot、surfaces、symbols、mappings、evidence。
- MCP 新增 `knowledge_agent_context_pack`。
- HTTP 新增：
  `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack`
  `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}`
- CLI 新增 `knowledge code context-pack`。
- 持久化：
  `workspace/assets/codebase/{codebase_id}/agent_context/{pack_id}.json`

合同要求：

- 输入包含 `task`, `snapshot_id`, `max_tokens`, `format`, `include`, optional `focus`。
- 输出 JSON 和 Markdown 共享同一个结构化中间模型。
- 每个 pack item 包含 `reason`, `evidence`, `confidence`, `token_cost`, `status`。
- `status`：`confirmed | inferred | needs_review`
- token 裁剪优先级：direct public surface、handler symbols、tests、risks、similar patterns、overview。
- 超出 budget 时必须输出 omitted items 和原因。

验收：

- 给定“新增 codebase import MCP tool”任务，输出相关 MCP registry、dispatcher、existing source/build tool patterns、HTTP router、CLI parser、tests。
- 所有关键建议有 evidence。
- evidence 不足时标记 `needs_review`。
- Markdown 输出可直接作为 Coding Agent 上下文使用。
- JSON 输出稳定可测。

### PR 8：DevWiki Baseline Stretch

目标：基于 V2 artifacts 生成最小 DevWiki 页面。此 PR 不阻塞 V2.0 MVP，除非产品决定首发必须包含。

页面：

- project-overview
- public-surface
- http-api
- mcp-tools
- cli
- developer-onboarding

验收：

- 页面包含 `snapshot_id`, `schema_version`, evidence。
- 页面可判断 stale。
- 页面可被 project query 或 context pack 使用。

### PR 9：Code Graph Baseline Stretch

目标：生成确定性 code graph artifact，不做完整调用图。

节点：

- Codebase, Snapshot, File, Module, Class, Function, Method, HTTPRoute, MCPTool, CLICommand, Capability, EvidenceSpan

边：

- CONTAINS, DEFINES, IMPORTS, HANDLED_BY, IMPLEMENTS_CAPABILITY, EVIDENCED_BY, GENERATED_FROM

验收：

- 支持 JSON graph 和 Mermaid export。
- 支持 neighbors。
- 所有边有 extractor/confidence。
- 不写入现有 GraphRAG DB；query 层可桥接。

### PR 10：Quality Extension Stretch

目标：把现有 quality governance 扩展到 code intelligence 对象。

新增 target_type：

- codebase
- repo_snapshot
- code_file
- code_symbol
- public_surface
- capability
- devwiki_page
- agent_context_pack
- code_graph_edge

新增 rule_type：

- missing_evidence
- stale_snapshot
- wrong_surface_mapping
- wrong_capability_mapping
- doc_code_mismatch
- low_confidence_inference
- overbroad_agent_context
- unsafe_path_exposure

验收：

- 可对 agent_context_pack 记录 feedback。
- 可生成 correction rule 和 correction plan。
- approved rule 可在 context pack 生成时应用。
- 不影响 V1 quality 对象。

## Acceptance Plan

### MVP Completion Definition

V2.0 MVP 完成必须同时满足：

- 外部 Agent 可通过 MCP 导入当前 repo 为 codebase。
- 可生成当前 repo snapshot，并记录 git、文件、语言、重要路径、warnings。
- 可列出 HTTP/MCP/CLI/frontend public surface。
- 可搜索 Python symbols。
- 可从 capability/surface 追踪到 symbol、file、line range。
- 可生成 Agent Context Pack，且关键建议都有 evidence。
- HTTP/MCP/CLI 三端覆盖 MVP 核心能力。
- 所有 V2 artifacts 可重复读取，包含 `schema_version`。
- 现有 V1 workspace/source/build/query/quality/MCP/CLI 测试不破坏。

### Self-Bootstrap Fixture

以当前 `data_service` repo 作为强制自举样例，验收必须识别：

- FastAPI 入口：`backend/app/main.py`
- MCP stdio 入口：`backend/data_service/mcp_stdio.py`
- MCP registry 和当前 40 个 tools
- CLI console scripts：`data-service`, `knowledge`
- Vue frontend entry 和 API client
- target/legacy HTTP route 分层
- 主要 tests 目录和测试文件
- 当前高耦合中心：HTTP 大文件和 DataService 大文件

### Contract Tests

必须新增并纳入 CI 或本地验收：

- codebase import contract test
- snapshot artifact golden test
- public surface inventory golden test
- Python symbol extraction fixture test
- surface-to-symbol mapping test
- evidence trace test
- MCP tool schema test
- HTTP route test
- CLI JSON output test
- Agent Context Pack golden test
- V1 regression smoke test

### Nonfunctional Acceptance

- 支持 5,000 文件 / 100k LOC 级别 repo snapshot。
- 单文件默认大小限制 2MB，可配置。
- binary/sensitive/unreadable 文件以 warning 记录，不静默失败。
- LLM synthesis 只消费 structured facts 和 evidence snippets，不直接全仓上传源码。
- 所有 response 默认 repo-relative path。
- partial scan、unresolved mapping、low confidence inference 必须显式暴露。

## Assumptions

- V2.0 MVP 不实现真正增量构建，只允许基于 snapshot diff 做 changed file detection，产物刷新可以全量。
- V2.0 首发语言语义支持 Python；Markdown/JSON/YAML/TOML/TS/Vue 先做文件与 surface inventory。
- DevWiki、Code Graph、Quality Extension 是 stretch 或 V2.1，除非产品明确调整为 V2.0 必须项。
- 新 HTTP router 独立注册，不继续扩大 `backend/app/api/v1/data_service.py`。
- 新 V2 core modules 独立于 `backend/data_service/service.py`，只通过 adapter/contract 与 V1 能力桥接。
- Codebase asset 独立于 source registry；未来可桥接 query/trace/quality，但不共享 registry schema。
