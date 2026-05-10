# Multi-App HarnessOS Core Readiness Audit

## Summary

- 是否已经支持多项目复用同一个 Core：**partial**
- 当前最大缺口：没有 `AppProfile/app_id/project_id/workspace_id` 这一层，Store、RPC、Artifact、Job、Trace、Approval 都主要按 `session_id/domain` 隔离，不能保证多个独立项目同时复用同一 Core 时不串数据、不串配置。
- 推荐实现路径：先补 AppProfile + namespace，再把 Pack/Connector/Runtime/Store/Governance 都挂到 profile 上；之后再做外部 Pack/Connector descriptor 和 SDK。

## Verified Facts

### 1. App Profile / Multi-App

- 代码中没有 `AppProfile`、`AppRegistry`、`AppRuntimeProfile`。宽搜只找到 OpenHarness provider profile，不是业务 app profile：`core/config/settings.py`。
- CLI server 只支持 `--host/--port/--no-reload`，没有 `--app-profile`：`main.py`。
- Headless CLI 只支持 `run --model --domain --json`，没有 app profile：`cli/main.py`。
- Core records 有 `tenant_id/user_id/domain/metadata`，但没有 `app_id/project_id/workspace_id` 字段：`core/protocol/models.py`。
- 应新增到 `SessionRecord/ThreadRecord/TurnRecord/ItemRecord/JobRecord/ArtifactRecord/ApprovalRecord/TraceRecord/MemoryRecord/RetryRecord/ConnectorRecord`，并在 SQLite 表建立索引：`core/stores/sqlite.py`。

### 2. 多 UI / 多 Gateway

- FastAPI 入口：`apps/api/__init__.py`。
- HTTP `/v1/runs`、POST SSE `/v1/runs/stream`、`/v1/rpc`：`apps/api/routers/runs.py`。
- stdio JSONL：`apps/gateway/stdio_server.py`。
- CLI/TUI/headless：`cli/main.py`。
- CORS 已配置，来源来自 `API_CORS_ORIGINS` 风格配置：`apps/api/__init__.py`、`core/config/__init__.py`。
- 协议是 JSON-RPC-like，不是完整 JSON-RPC 2.0；`RpcRequest` 只有 `method/params/id`，无 `jsonrpc` 字段：`apps/gateway/protocol.py`。
- 存在旁路旧 API：`/api/agents/invoke` 是 placeholder，`/api/routing/intent` 直接用 intent router，不走 Gateway Core RPC：`apps/api/routers/agents.py`、`apps/api/routers/routing.py`。
- video-studio UI 当前建议调用：`session.start`、`turn.start(domain=video_studio)`、`pack.get`、`workflow.plan`、`workflow.execute_stub`、`artifact.lineage`、`job.list/get/events`、`connector.list/get/health`。

### 3. Domain Pack

- Pack manifest schema 在代码 dataclass 中，不是独立 JSON Schema：`core/packs/registry.py`。
- 默认只加载 repo-local `packs/*/manifest.json`，不支持 external pack path 配置：`core/packs/registry.py`。
- 当前状态：`meeting/knowledge/video_studio` active；`interview/investment` stub。见 `packs/meeting/manifest.json`、`packs/knowledge/manifest.json`、`packs/video_studio/manifest.json`、`packs/interview/manifest.json`、`packs/investment/manifest.json`。
- Pack 能声明 workflows、agents/subagents、skills、connectors、policy bundles、artifact kinds/schemas、memory scopes、evaluation rules：`core/packs/registry.py`。
- 装配不是纯可见性：会校验 workflow、connector、capability、policy bundle、schema version，并返回 `assembled/blocked/stub`：`core/packs/registry.py`。
- 但真实 workflow factory 仍硬编码三类：meeting、knowledge、video，新增外部 workflow 仍要改 Core/Gateway 代码：`apps/gateway/workflows.py`。

### 4. Connector Registry

- 存在 `ConnectorRegistry`：`apps/gateway/connectors.py`。
- ConnectorRecord 支持 `connector_id/kind/domain/version/health/capabilities/config_ref/metadata`，不支持一等字段 `app_scope/secret_ref`：`core/protocol/models.py`。
- 默认注册 `meeting_voice_mcp/funasr_mcp/data_service_mcp/remote_comfyui`：`apps/gateway/connectors.py`。
- Meeting MCP 已作为 connector 注册，但 meeting 专用 RPC 仍直接通过 `MeetingGatewayService` 调用，属于旁路业务入口：`apps/gateway/service.py`。
- 不支持 external connector descriptor；新增 FFmpeg/TTS/本地视频模型 connector 目前要改 `apps/gateway/connectors.py` 和 capability 常量 `apps/gateway/workflows.py`。
- `connector.list/get/health/submit/poll/cancel/collect` 已注册：`apps/gateway/service.py`。

### 5. Runtime Adapter

- RuntimeAdapter 接口在 `core/runtime_adapter/adapters.py`。
- 已有 `SimpleRuntimeAdapter` 和 `OpenHarnessRuntimeAdapter`：`core/runtime_adapter/adapters.py`。
- `GatewayRuntimePool` 可按 session backend 选择 `auto/openharness/simple`，但不是按 app profile 选择：`apps/gateway/runtime.py`。
- RuntimeHandle 挂在 session 上，按 `session_id` 管理，不按 `app_id` 隔离：`apps/gateway/runtime.py`。
- Gateway events 统一为 `turn.started/item.delta/turn.completed/turn.failed/turn.interrupted`：`apps/gateway/runtime.py`。
- Governance metadata 注入 adapter 层已存在：`core/runtime_adapter/adapters.py`。
- 仍有绕过 Adapter 的路径：Domain workflow 在 adapter 前直接执行；fallback 也可能 `session.agent.invoke`：`apps/gateway/runtime.py`。

### 6. Store Namespace / 多项目隔离

- SQLite schema 在 `core/stores/sqlite.py`。
- 所有 CoreObject 都有 `metadata`：`core/protocol/models.py`。
- 没有 `app_id/project_id/workspace_id` 列和查询过滤；当前主要支持 `session_id/thread_id/turn_id/domain/kind/status`：`core/stores/sqlite.py`。
- local JSON/JSONL 兼容路径仍参与主流程 fallback：`apps/gateway/runtime.py`。
- 多 app 并行运行会共享默认 `.harnessos/core.sqlite3`、`.harnessos/artifacts`、`.harnessos/traces`、`.harnessos/approvals`，存在 namespace 污染风险：`core/stores/sqlite.py`、`apps/gateway/artifacts.py`。

### 7. Job / Artifact

- Job 支持 `workflow_id/domain/session/thread/turn/status/progress/trace_id/artifact_ids/metadata`；不支持一等字段 `app_id/project_id/external_job_ref/parent_job_id/child_jobs`：`core/protocol/models.py`。
- Artifact 支持 `domain/kind/owner_session/thread/turn/uri/name/mime/parent_ids/metadata`；不支持一等字段 `app_id/project_id/external_asset_uri/preview_uri/thumbnail_uri`：`core/protocol/models.py`。
- `artifact.read` 直接 `read_text()` 读全量文件，不适合大视频/大二进制：`apps/gateway/artifacts.py`。
- 可以只登记 metadata/URI 的 Core 模型具备 `uri`，但 Gateway `ArtifactRegistry.register_file` 要求本地文件存在，所以外部 asset service 需要新增 `artifact.register_external` 或放宽 registry：`apps/gateway/artifacts.py`。
- Meeting/video 已有 artifact lineage 样板：meeting `transcript -> analysis -> result -> minutes`，video `brief -> script -> storyboard -> shot_list -> asset_plan -> render_output`：`packs/meeting/workflow.py`、`packs/video_studio/workflow.py`。

### 8. Governance

- Policy 支持 `domain` 作为 metadata，但规则不是 domain/app-specific：`apps/gateway/policies.py`。
- Pack manifest 可声明 `policy_bundles`，装配会检查 bundle 是否存在，但没有真正加载/执行 bundle 规则：`core/packs/registry.py`。
- 可识别 write/delete/send/publish 和若干 mutating tools；upload/external API call/overwrite 只有关键词或工具名 pattern 覆盖，不是完整策略模型：`apps/gateway/policies.py`。
- Approval/Retry 无 app/project 隔离；Retry 有一次性状态机，能避免同一 approval 重复 retry：`apps/gateway/retries.py`。
- Secret hygiene 覆盖 trace、approval、retry、artifact.read 等 Gateway 层；job failure_context 通过 CoreAppService 写入时不是统一 mask 的一等边界，需要补强：`apps/gateway/secrets.py`、`core/services/app_service.py`。

### 9. SDK / 外部调用

- 没有面向 harnessOS server 的 Python SDK；`core/api/*Client` 是 LLM provider client，不是 harnessOS SDK：`core/api/client.py`。
- 没有 TypeScript SDK；`apps/web` 是 Vue app 骨架。
- JSON-RPC method registry 可用于生成 SDK 的基础清单：`apps/gateway/rpc_router.py`，但缺少参数/响应 schema，所以还不够稳定生成强类型 SDK。
- 外部 video-studio 后端当前推荐用 HTTP `/v1/rpc` 或 stdio JSONL；浏览器 UI 用 `/v1/rpc` + POST SSE `/v1/runs/stream`，但原生 EventSource 不支持 POST，需要 fetch-stream/polyfill。

### 10. 测试与验收

- 当前完整测试命令：`python3 -m pytest tests -q`。
- `--collect-only` 当前收集 **134 tests**；其中真实音频测试依赖本地 FunASR/Meeting MCP。
- 有 protocol contract tests：`tests/test_gateway_protocol.py`、`tests/test_rpc_stdio_compat.py`。
- 有 store backend tests：`tests/test_core_v15_protocol_store.py`。
- 有 runtime adapter tests：`tests/test_runtime_adapter.py`。
- 有 pack assembly tests：`tests/test_pack_registry.py`、`tests/test_pack_execution.py`。
- 有 connector registry/execution tests：`tests/test_gateway_protocol.py`。
- 没有 app profile / namespace isolation tests。
- 有 job + artifact + trace 组合测试，主要在 gateway/core/trace/artifact 测试中。

## P0 Blockers

- 缺 `AppProfile` 与 `app_id/project_id/workspace_id` 一等字段，无法安全支持多个独立项目共用同一 Core。
- Store 查询与索引没有 namespace 过滤，`session.list/artifact.list/job.list/trace.list/approval.list` 都可能跨项目可见。
- Pack loading 只支持 repo-local `packs/`，外部项目 pack 不能通过配置挂载。
- ConnectorRegistry 是硬编码默认 connector，不支持 external descriptor 和 app-scoped connector。
- Gateway 仍有 meeting 专用 RPC 和 `/api/*` 旁路入口，不是所有业务都统一走 profile-scoped Core RPC。
- ArtifactRegistry 只登记本地文件，`artifact.read` 全量读取，不适合 video-studio 大文件和外部 asset service。

## P1 Improvements

- 为 RPC `method.list` 增加参数/响应 schema，支撑 SDK 生成。
- 将 `AVAILABLE_*` 常量改为从 AppProfile + PackRegistry + ConnectorRegistry 动态计算。
- 把 `policy_bundles` 从装配检查升级为可执行策略包。
- 将 Meeting 专用 service/RPC 降级为 meeting pack connector/workflow 的兼容层。
- 增加 GET SSE 或 stream-json endpoint，改善浏览器原生消费。
- 增加 `artifact.register_external`、range/preview/thumbnail 读取接口。

## Proposed Architecture Changes

- 新增 `core/apps/`：`AppProfile`、`AppRegistry`、profile loader、profile resolver。
- 扩展 `core/protocol/models.py` 与 `core/stores/sqlite.py`：所有核心记录增加 `app_id/project_id/workspace_id`，并加组合索引。
- 扩展 `GatewayService/GatewayRuntimePool`：每个 request/session 解析 `app_id`，按 profile 选择 packs、connectors、runtime adapter、policy profile、store/artifact namespace。
- 扩展 `PackRegistry`：支持 `HARNESSOS_PACK_PATHS` / profile `pack_paths`，加载外部 pack；workflow entrypoint 动态 import。
- 扩展 `ConnectorRegistry`：支持 descriptor JSON/YAML，字段含 `connector_id/domain/app_scope/capabilities/health/config_ref/secret_ref/execution_adapter`。
- 扩展 Governance：policy bundle loader + app/domain-specific rule overlay。
- 新增 SDK：最小 Python/TS JSON-RPC client，覆盖 session、turn、stream、pack、workflow、connector、job、artifact、approval。

## Suggested AppProfile Schema

```json
{
  "app_id": "video_studio",
  "display_name": "Video Studio",
  "enabled_packs": ["video_studio"],
  "enabled_connectors": ["remote_comfyui", "ffmpeg", "tts"],
  "runtime_adapter": "openharness",
  "policy_profile": "video.production",
  "store_namespace": "video_studio",
  "artifact_namespace": "video_studio",
  "job_namespace": "video_studio",
  "pack_paths": ["./packs", "../video-studio/packs"],
  "connector_descriptor_paths": ["../video-studio/connectors"],
  "cors_origins": ["http://localhost:5173"],
  "metadata": {
    "default_domain": "video_studio"
  }
}
```

## Suggested Directory / Config Layout

```text
harnessOS/
  core/apps/
    models.py
    registry.py
  configs/app_profiles/
    meeting.json
    knowledge.json
    video_studio.json
    interview.json
    investment.json
  configs/connectors/
    remote_comfyui.json
    ffmpeg.json
    tts.json
  packs/
    meeting/
    knowledge/
    video_studio/
external-project/
  packs/video_studio/manifest.json
  connectors/*.json
```

## Go / No-Go Recommendation

- 是否可以开始独立 video-studio 项目：**可以开始原型，但不建议作为真正多项目隔离架构上线。**
- 可行限制：video-studio UI/BFF 可以调用同一个 harnessOS `/v1/rpc`，使用 `turn.start(domain=video_studio)`、`workflow.plan`、`workflow.execute_stub`、`artifact.lineage` 做规划和工件链路原型。
- 必须明确限制：当前没有 app namespace 隔离；ComfyUI 只是 connector descriptor/scaffold，不是完整执行；视频文件不应通过现有 `artifact.read` 读取；外部 video pack/connector 还不能不改 Core 动态接入。
- 真正进入“多个独立 AI 项目复用同一 Core”前，P0 必须先补：AppProfile、namespace 字段与查询过滤、external pack path、external connector descriptor、外部 artifact/asset URI 注册。
