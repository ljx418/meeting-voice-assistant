# harnessOS V3.0 Multi-App Core Development Plan

文档状态：ACTIVE PLAN。本文是当前 V3.0-PhaseA 到 V3.0-PhaseE 的活动实施计划。

本文替代“直接做通用低代码 Agent 工作流平台”的旧 V3.0 执行口径。当前优先级固定为：先稳 harnessOS Core，再用 Meeting / Knowledge 两个 reference packs 验证平台边界，最后扩展 Interview / Investment / Video Studio。

## 1. 总体目标

- 一份 harnessOS Core 代码支持多个 app：`meeting`、`knowledge`、`interview`、`investment`、`video_studio`。
- 不同 app 可以拥有不同 UI、workflow、connector，但共用协议、Store、Job、Artifact、Trace、Policy、Approval、Retry。
- 新业务不得写入 Core 或 Gateway，必须通过 AppProfile、Pack、Connector、RuntimeAdapter 接入。
- Meeting 和 Knowledge 在当前阶段是标准 Pack + Connector 的 reference packs / validation samples，用于验证平台抽象，而不是平台内置业务终局。
- V3.0 的阶段出口以“平台中立性”衡量：新增 app 理论上应只增加 AppProfile、Pack、Connector descriptor 和 workflow descriptor，而不是再改 Core / Gateway 业务逻辑。

## 1.1 统一编号规则

| 类型 | 规则 | 示例 |
| --- | --- | --- |
| 架构平面 | `Plane-N` | `Plane-3 Harness Core` |
| 当前阶段 | `V3.0-PhaseX` | `V3.0-PhaseA` |
| 当前切片 | `V3.0-PhaseX-Xn` | `V3.0-PhaseB-B2` |
| 验收项 | `V3.0-PhaseX-ACnn` | `V3.0-PhaseC-AC04` |
| 阻塞级别 | `P0/P1/P2` | `P0` |

`Plane-N` 只用于架构平面；`P0/P1/P2` 只用于优先级，不再表示架构层。

## 1.2 阶段状态与冻结规则

| 阶段 | 当前状态 | 变更控制 |
| --- | --- | --- |
| V3.0-PhaseA | COMPLETED / FROZEN BASELINE（2026-05-06） | 仅允许缺陷修复、验收证据追加、与实际实现一致的文档校正；不得被后续规格漂移直接覆写。 |
| V3.0-PhaseB | ACTIVE NEXT PHASE | 当前主开发阶段。 |
| V3.0-PhaseC | PLANNED | 以 PhaseB 交付稳定后再进入。 |
| V3.0-PhaseD | PLANNED | 以 PhaseB/PhaseC 交付稳定后再进入。 |
| V3.0-PhaseE | PLANNED | 以 PhaseB/PhaseC/PhaseD 交付稳定后再进入。 |

已完成阶段若需调整合同、DoD 或验收边界，必须在后续 Phase 或新增切片中显式承接，不能直接回写原阶段定义。

## 2. V3.0 阶段

### V3.0-PhaseA：Multi-App Core Readiness

阶段状态：COMPLETED / FROZEN BASELINE（2026-05-06）

详细实施文件：`docs/design/V3.0/v3_phasea_multi_app_core_readiness.md`  
辅助验收基线：`docs/design/V3.0/v3_phasea_multi_app_core_readiness_acceptance.md`

- 实现 `AppProfile`、`AppRegistry`、`ScopeContext`。
- 为 `Session / Thread / Turn / Item / Job / Artifact / Approval / Trace / Retry / Connector` 增加 `app_id/project_id/workspace_id`。
- Store 查询默认按 ScopeContext 过滤。
- RPC 支持 `app_id/project_id/workspace_id`。
- 新增 meeting、knowledge、interview、investment、video_studio app profiles。
- 增加 namespace isolation tests，禁止多个 app 查询结果串数据。

Definition of Done：

- AppProfile/AppRegistry/ScopeContext 可用，并有 meeting、knowledge、interview、investment、video_studio profiles。
- `Session / Thread / Turn / Item / Job / Artifact / Approval / Trace / Retry / Connector` 写入包含 scope。
- Store list/query 默认按 ScopeContext 过滤。
- 当前代码状态：SQLite Store 已支持 scope columns、indexes 和按参数过滤；底层 `list_*` 未传 scope 时仍可全量查询。V3.0-PhaseA 的实现边界是让 Gateway/Core service 普通调用链默认传 ScopeContext，并把不传 scope 的全量查询定义为受控兼容/管理 bypass。
- 当前代码状态：`resolve_scope_context()` 已支持 `params.scope`、AppProfile 默认 project/workspace；`session.list/read/transcript/events` 已进入默认 scope 隔离；`v3_001_add_scope_columns` 和 legacy backfill fixtures 已落地。
- legacy records backfill 到 `default` 或可识别 app。
- namespace isolation tests 通过，meeting 与 knowledge 同名 records 不串数据。
- meeting real audio acceptance 不回归；该项属于显式外部服务验收，不应阻断默认 stub/contract 回归。

PR slices / implementation order：

1. `V3.0-PhaseA-A1` AppProfile schema + default profiles。
2. `V3.0-PhaseA-A2` ScopeContext resolver + RPC scope params。
3. `V3.0-PhaseA-A3` Core records scope fields + Store filtering。
4. `V3.0-PhaseA-A4` Store migration/backfill + legacy import compatibility。
5. `V3.0-PhaseA-A5` namespace isolation tests + meeting e2e regression。

当前验收状态：

- 2026-05-06 已重新完成前检查、默认主线和显式真实音频三条验收线：
  - `.venv/bin/python scripts/check_real_mcp_env.py` -> `status=ok`
  - `.venv/bin/python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'` -> `145 passed, 1 skipped, 2 deselected`
  - `.venv/bin/python -m pytest -q tests/test_meeting_audio_acceptance.py tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` -> `2 passed`
- 以当前文档口径，V3.0-PhaseA 已达到完成定义；后续仅保留跨阶段延续问题，不再阻塞进入 PhaseB。
- 冻结规则：后续不得把 PhaseB/PhaseC/PhaseD/PhaseE 的新需求直接回写为 PhaseA 合同变化；若发现缺陷，只能作为 PhaseA bugfix 或后续阶段兼容约束处理。

### V3.0-PhaseB：Pack Assembly + Connector Registry

阶段状态：ACTIVE NEXT PHASE

详细实施文件：`docs/design/V3.0/v3_phaseb_pack_connector_registry.md`

- 正式化 Pack manifest schema。
- Pack 驱动 workflow、skill、connector、policy bundle、artifact kind 装配。
- 支持 external pack paths。
- 正式化 ConnectorRegistry。
- Connector 支持 capabilities、health、config_ref、secret_ref、app_scope。
- Meeting MCP 和 Knowledge MCP 必须通过 ConnectorRegistry 接入，不允许硬编码路径。

当前代码状态：

- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded`、`blocked_reason` / `disabled_reason` 等正式合同字段，并已通过 `pack.list/get` 暴露。
- PackRegistry 已开始显式拒绝 duplicate pack name / domain / workflow_id；external pack roots 不再 silent overwrite。
- Connector descriptor 已开始稳定输出 security fields，并在执行前阻断未 allowlist 的 stdio command/path 与不满足 network policy 的 remote connector。
- external pack version policy、severity 分层和 Meeting / Knowledge 的标准装配入口去硬编码化仍需在本阶段继续收口。

Definition of Done：

- PackAssemblyResult 返回 `assembled/blocked/degraded/stub`。
- missing connector 时返回 blocked，并提供 missing_dependencies、blocked_reason、next_actions。
- connector.health 通过 ConnectorRegistry 执行。
- meeting/knowledge connector assembly 通过 AppProfile + ConnectorRegistry 完成。
- Meeting MCP 和 Knowledge MCP 不再依赖硬编码路径作为标准入口。

PR slices / implementation order：

1. `V3.0-PhaseB-B1` Pack manifest schema + assembly result contract。
2. `V3.0-PhaseB-B2` Pack conflict / missing dependency handling。
3. `V3.0-PhaseB-B3` external pack paths。
4. `V3.0-PhaseB-B4` ConnectorRegistry descriptor schema + health/capabilities。
5. `V3.0-PhaseB-B5` meeting/knowledge connector registry assembly tests。
6. `V3.0-PhaseB-B6` reference pack standard-entry hardening。
7. `V3.0-PhaseB-B7` descriptor-driven workflow registration。

退出门：

- `PackAssemblyResult` 可稳定表达 `assembled/blocked/degraded/stub` 及其原因。
- `connector.list/get/health` 能通过 registry 暴露 descriptor 与 health。
- 未 allowlist 的 stdio command/path/network 被 blocked。
- Meeting / Knowledge 的标准装配入口回到 pack/registry，不再以硬编码路径作为主入口。
- 新增 sample/reference pack 的发现与装配不再要求修改 Core/Gateway 业务逻辑。

### V3.0-PhaseC：Job / Artifact / Governance Hardening

- JobRecord 增加 `app_id/project_id/workspace_id`、`external_job_ref`、`parent_job_id`、`progress`、`failure_context`、`artifact_ids`。
- ArtifactRecord 增加 `app_id/project_id/workspace_id`、`external_asset_uri`、`preview_uri`、`thumbnail_uri`、`parent_ids`、`metadata`。
- 新增 `artifact.register_external`、`artifact.read_metadata`、`artifact.lineage`。
- Policy 覆盖 tool invocation、job execution、artifact persistence。
- RuntimeAdapter 默认注入 policy、approval、trace、secret hygiene、scope context。

Definition of Done：

- Job 状态机支持 queued/running/succeeded/failed/cancelled。
- JobRecord 支持 progress、failure_context、external_job_ref、parent_job_id、artifact_ids。
- Artifact large file policy 和错误码冻结。
- Policy 覆盖 tool invocation、job execution、artifact persistence。
- RuntimeAdapter 默认注入 scope、policy、approval、trace、secret hygiene。

PR slices / implementation order：

1. `V3.0-PhaseC-C1` JobRecord schema + state machine hardening。
2. `V3.0-PhaseC-C2` ArtifactRecord external/preview/thumbnail/lineage fields。
3. `V3.0-PhaseC-C3` artifact read metadata-only + large file policy。
4. `V3.0-PhaseC-C4` Policy hooks for tool/job/artifact persistence。
5. `V3.0-PhaseC-C5` RuntimeAdapter governance context injection tests。
6. `V3.0-PhaseC-C6` platform-neutral governance audit。

### V3.0-PhaseD：Meeting Reference Pack Validation

- `packs/meeting` 作为 reference pack 验证真实外部执行链路和 artifact lineage，不作为平台内置业务特权入口。
- Meeting pack manifest 装配 workflow、connector、skills、artifact kinds、policy。
- 通过 Meeting MCP / FunASR MCP connector 完成真实音频分析。
- 输出 transcript、analysis、result、minutes artifacts。
- 确保 job、trace、turn、artifact 关联完整。
- 旧 meeting RPC 只保留兼容 facade，内部走标准 Pack / Connector 路径。

Definition of Done：

- Meeting reference pack 通过真实音频 E2E。
- 通过 Meeting MCP / FunASR MCP connector 生成 transcript、analysis、result、minutes artifacts。
- legacy meeting facade 与 pack workflow 产出等价。
- job、trace、turn、artifact 关联完整。
- 旧硬编码 meeting 旁路被移除或降级为兼容入口。
- Meeting 验证结果能够证明平台不需要为该 pack 继续保留 Core/Gateway 特判。
- 当前代码状态：fake/unit 覆盖已基本稳定，但真实音频验收仍依赖相邻 `meeting-voice-assistant` 项目的 Meeting MCP 与 FunASR 服务；未满足该外部前置时，不能把 PhaseD 视为已完成。

PR slices / implementation order：

1. `V3.0-PhaseD-D1` Meeting pack manifest assembly 完整化。
2. `V3.0-PhaseD-D2` Meeting MCP / FunASR connector registry 接入。
3. `V3.0-PhaseD-D3` Pack workflow 真实音频 E2E。
4. `V3.0-PhaseD-D4` legacy facade -> pack workflow adapter。
5. `V3.0-PhaseD-D5` artifact/job/trace equivalence tests。

### V3.0-PhaseE：Knowledge Reference Pack Validation

- `packs/knowledge` 作为 reference pack 验证状态型 connector、workflow lifecycle、data boundary 与 connector replaceability。
- 通过 Knowledge MCP connector 接入本地知识库服务。
- 支持 ingest、search、summarize、citation。
- 输出 note、brief、citation_bundle artifacts。
- 确保 trace、artifact、job、turn 关联完整。
- 不改 Core 即可替换 knowledge connector。

Definition of Done：

- Knowledge reference pack 通过 `data_service_mcp` 完成 ingest/search/citation E2E。
- 输出 note、brief、citation_bundle artifacts。
- Knowledge workflow 不直接读写 data_service 内部目录。
- trace、artifact、job、turn 关联完整。
- 替换 knowledge connector 不需要修改 Core。
- Knowledge 验证结果能够证明平台不需要为该 pack 继续保留 Core/Gateway 特判。

PR slices / implementation order：

1. `V3.0-PhaseE-E1` Knowledge pack manifest assembly 完整化。
2. `V3.0-PhaseE-E2` data_service_mcp connector registry 接入。
3. `V3.0-PhaseE-E3` ingest/search/summarize/citation workflow E2E。
4. `V3.0-PhaseE-E4` Knowledge data boundary tests。
5. `V3.0-PhaseE-E5` connector replacement fixture + lineage regression。

## 3. AppProfile Schema

`app_id` 是应用隔离边界；`domain` 是业务分类；`project_id` 是业务项目实例；`workspace_id` 是本地或用户工作区。不得用 `domain=video_studio` 代替 `app_id=video_studio`。

```json
{
  "app_id": "video_studio",
  "display_name": "AI Video Studio",
  "status": "stub",
  "default_domain": "video_studio",
  "enabled_packs": ["video_studio", "knowledge"],
  "enabled_connectors": ["remote_comfyui", "ffmpeg", "data_service_mcp"],
  "runtime_adapter": "openharness",
  "policy_profile": "video_studio.default",
  "store_namespace": "video_studio",
  "artifact_namespace": "video_studio",
  "job_namespace": "video_studio",
  "pack_paths": ["./packs", "../video-studio/packs"],
  "connector_descriptor_paths": ["./connectors", "../video-studio/connectors"],
  "metadata": {}
}
```

Meeting 示例：

```json
{
  "app_id": "meeting",
  "display_name": "Meeting Assistant",
  "status": "active",
  "default_domain": "meeting",
  "enabled_packs": ["meeting"],
  "enabled_connectors": ["meeting_voice_mcp", "funasr_mcp"],
  "runtime_adapter": "openharness",
  "policy_profile": "meeting.default",
  "store_namespace": "meeting",
  "artifact_namespace": "meeting",
  "job_namespace": "meeting",
  "pack_paths": ["./packs"],
  "connector_descriptor_paths": ["./connectors"],
  "metadata": {}
}
```

Knowledge 示例：

```json
{
  "app_id": "knowledge",
  "display_name": "Personal Knowledge Base",
  "status": "active",
  "default_domain": "knowledge",
  "enabled_packs": ["knowledge"],
  "enabled_connectors": ["data_service_mcp"],
  "runtime_adapter": "openharness",
  "policy_profile": "knowledge.default",
  "store_namespace": "knowledge",
  "artifact_namespace": "knowledge",
  "job_namespace": "knowledge",
  "pack_paths": ["./packs"],
  "connector_descriptor_paths": ["./connectors"],
  "metadata": {}
}
```

## 4. ScopeContext Propagation

ScopeContext 必须沿以下路径传播：

```text
RPC Request
  -> AppProfileResolver
  -> ScopeContext(app_id, project_id, workspace_id, user_id?)
  -> Session / Thread / Turn creation
  -> Orchestrator
  -> Workflow Engine
  -> Runtime Adapter
  -> Tool Registry
  -> Connector Registry
  -> Job Service
  -> Artifact Service
  -> Trace / Approval / Retry Store
```

硬规则：

- 任何 Core Store 写入都必须带 ScopeContext。
- 任何 list/query 默认按 ScopeContext 过滤。
- 任何 tool/job/artifact/approval/trace 事件都必须绑定 ScopeContext。
- RPC 未显式传 scope 时，只能使用 AppProfileResolver 给出的默认 scope。

## 5. Store Migration / Backfill

Migration 名称：`v3_001_add_scope_columns`。

需要新增 scope columns 的对象：

- sessions
- threads
- turns
- items
- jobs
- artifacts
- approvals
- traces
- retries
- connectors

Backfill rule：

- 既有 legacy records 默认 `app_id = "default"`。
- 可通过 domain/kind/path 明确识别的 meeting records 可以映射为 `app_id = "meeting"`。
- 无法确认的记录保持 `app_id = "default"`，不得猜测业务归属。

Rollback 策略：

- migration 不删除旧字段。
- forward-only rollback 优先，正常 rollback 不删除 scope columns。
- 只允许通过 compatibility flag 临时关闭 scope filtering。
- destructive rollback 必须先 backup + restore，且不得作为默认恢复路径。
- legacy JSON/JSONL import 继续支持无 scope 输入，但导入时必须补默认 ScopeContext。

测试要求：

- scope isolation fixture 覆盖 meeting 与 knowledge 同名 artifact/job/thread 不串数据。
- legacy import fixture 覆盖无 scope records backfill 到 default。

## 6. PackAssemblyResult Contract

V3.0-PhaseB 的 Pack Assembly 交付物是装配结果对象，不只是 manifest loader。

当前代码状态：`PackAssemblyResult` 已能稳定表达 `assembled`、`blocked`、`degraded`、`stub`，并暴露 `app_id`、`missing_dependencies`、`conflicts`、`blocked_reason` alias 和 `next_actions`；`PackRegistry` 也已在注册和 `load_from_paths()` 阶段显式拒绝 duplicate pack name / domain / workflow_id。当前剩余工作不再是“补字段”，而是冻结 severity 语义、external pack version policy、cross-app conflict 边界和 sample-pack neutrality 验收。

```python
PackAssemblyResult:
  pack_name
  app_id
  status: assembled | blocked | degraded | stub
  workflows
  subagents
  skills
  connector_requirements
  policy_bundles
  artifact_kinds
  missing_dependencies
  conflicts
  blocked_reason
  next_actions
```

冲突处理：

- 两个 Pack 注册同名 workflow：同 app 内 blocked，跨 app 按 app scope 隔离。
- 两个 Pack 注册同名 artifact kind：同 app 内 blocked，除非 manifest 显式声明兼容 alias。
- Pack 需要 connector 但 AppProfile 未启用：assembly status 为 blocked。
- Pack policy bundle 缺失：assembly status 为 degraded 或 blocked，由 manifest policy severity 决定。
- External pack 版本不兼容：assembly status 为 blocked，并返回 required/current version。

## 7. Connector Security Model

Connector 是外部能力边界，尤其 MCP stdio connector。MCP 用于把 AI 应用连接到数据源、工具和工作流，因此 connector 能力必须经过治理。MCP Tool Annotations 只能作为风险词汇提示，不能作为可信授权合同。

Connector descriptor 增加：

```json
{
  "trust_level": "trusted_local | untrusted_local | remote | sandboxed",
  "execution_mode": "stub | stdio | http | sse",
  "allowed_commands": [],
  "allowed_paths": [],
  "network_policy": "none | allowlist | unrestricted",
  "capabilities": [],
  "config_ref": "connector.config.local",
  "secret_ref": "connector.secret.local",
  "app_scope": ["meeting"],
  "tool_risk_defaults": {
    "read_only": true,
    "destructive": false,
    "external_side_effect": false
  },
  "requires_approval_for": ["write", "delete", "publish", "external_call"]
}
```

硬规则：

- connector-declared capabilities are not policy authority.
- policy engine is the authority.
- stdio connector 的 command/path/network 必须经过 allowlist。
- secret_ref 只能传引用，不能把密钥写入 manifest 或 trace。

当前代码状态：ConnectorRegistry 已能登记 Meeting/FunASR/Data Service/ComfyUI 等 connector，并能执行 `connector.health`；内置 connector 现已开始通过 descriptor definition 驱动注册，而不是散落在平台层的条件分支。V3.0-PhaseB 剩余工作是继续压缩内置业务描述、把更多 descriptor 字段收敛到 config/manifest 输入，并证明新增 sample connector 不需要新增平台业务判断。

参考：

- MCP Intro: https://modelcontextprotocol.io/docs/getting-started/intro
- MCP Tool Annotations: https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/

## 8. Job Worker MVP Boundary

V3.0-PhaseC 只实现本地最小 worker，不实现分布式调度。

包含：

- local in-process async worker
- SQLite-backed job state
- queued/running/succeeded/failed/cancelled
- progress update
- failure_context
- artifact_ids binding
- external_job_ref
- parent_job_id

明确不做：

- distributed workers
- GPU resource scheduling
- cron scheduling
- DAG execution engine
- multi-worker lease

## 9. Artifact Large File Policy

`artifact.read` 行为：

- text/markdown/json 且小于 `MAX_INLINE_ARTIFACT_BYTES`：返回 content。
- binary：拒绝全文读取，返回 `artifact.read_metadata` 建议。
- video/audio/image：拒绝 content read，返回 metadata + preview_uri。
- external-only artifact：拒绝 content read，返回 external_asset_uri metadata。
- 大于 `MAX_INLINE_ARTIFACT_BYTES`：拒绝 content read。

当前代码状态：已阻断 video、large 和 external-only artifact inline read；audio/image/binary 分类、统一错误码和 JSON-RPC error shape 仍需在 V3.0-PhaseC 冻结。

默认阈值：`MAX_INLINE_ARTIFACT_BYTES = 1048576`。

错误码：

- `ARTIFACT_TOO_LARGE`
- `ARTIFACT_BINARY_READ_BLOCKED`
- `ARTIFACT_EXTERNAL_ONLY`

JSON-RPC 响应必须遵守 JSON-RPC 2.0：`result` 与 `error` 不得同时存在。参考：https://www.jsonrpc.org/specification

## 10. Protocol / SDK / Auth

目标 Protocol version：

```text
core/protocol/VERSION = "v1alpha3"
```

V3.0 硬前置：

- Protocol version、method registry、event registry、error code registry 必须在 V3.0-PhaseA 和 V3.0-PhaseB 期间冻结。
- JSON-RPC `result` 与 `error` 不得同时存在。
- 当前代码状态：Gateway initialize 仍返回 `v1alpha`，因此 `v1alpha3` 只能作为 V3.0 目标合同，不能标记为已完成。

需要维护：

- `docs/protocol/methods.md`
- `docs/protocol/events.md`
- `docs/protocol/errors.md`
- `schemas/jsonrpc/*.json`

SDK 策略：

- Python SDK for backend/BFF 建议尽早完成，用于 Meeting / Knowledge 迁移和 contract tests。
- TypeScript SDK for Web Gateway/frontend 可推迟到 Web / Video Studio 前。
- 优先从 JSON schema 生成。
- contract tests against local app-server。

最小方法：

- `session.start`
- `turn.start`
- `events.subscribe`
- `artifact.list`
- `artifact.register_external`
- `job.get`
- `approval.respond`
- `pack.list`
- `connector.health`

Auth MVP：

- local dev mode 只能通过显式 flag 关闭鉴权。
- 默认使用 local capability token。
- dev mode 不能阻塞本地开发，但必须显式开启。
- AppProfile 可定义 allowed origins。
- scope 从 token/app profile 推导，不允许客户端任意扩大 scope。

## 11. Legacy API Sunset

Legacy meeting RPC 三阶段：

- Stage 1：facade internally calls Pack workflow。
- Stage 2：logs deprecation warning。
- Stage 3：disabled by default, enabled only with compatibility flag。

回归要求：

- legacy meeting RPC and pack-based meeting workflow produce equivalent artifacts。

## 12. Knowledge Pack Data Boundary

Knowledge Pack 必须：

- never read/write data_service internal artifact dirs directly。
- call only data_service_mcp lifecycle/v2 tools。
- enforce DATA_SERVICE_WORKSPACE_ROOT allowlist。
- validate source path allowlist。
- enforce file size limit。
- deduplicate by sha256。
- block symlink escape。

## 13. Deferred Items

以下能力属于 V3.x+ 远期方向，不进入 V3.0-PhaseA 到 V3.0-PhaseE 验收范围：

- Low-Code Workflow Runtime
- Core Memory System
- Feedback Optimization Loop
- Workflow Library

后续扩展阶段：

- V3.1：Interview Pack
- V3.2：Investment Pack
- V3.3：Video Studio external project integration

## 14. 当前落地切片

当前代码已完成 V3.0-PhaseA 基座的一部分和 V3.0-PhaseC 的 artifact/job 部分硬化，但以下均属于基础实现，不等于阶段验收完成：

- `core.apps` 新增 AppProfile/AppRegistry/ScopeContext。
- Core records 与 SQLite Store 支持 `app_id/project_id/workspace_id`。
- Gateway RPC 开始接受 scope 参数。
- Artifact 支持 external registration 和 metadata-only read。
- `artifact.read` 拒绝视频、大文件和 external-only 全量读取。
- PackAssemblyResult 已有 assembled/blocked/stub 基础。
- ConnectorExecutionRuntime 已能创建 connector job 并登记结果 artifact。

下一步进入 V3.0-PhaseB 的 PackAssemblyResult 完整合同、Connector Security Model 和 manifest/config 驱动对齐；同时补 V3.0-PhaseA 的 protocol version、migration/backfill 与 scope bypass 边界，再推进 Meeting / Knowledge 标准迁移。
