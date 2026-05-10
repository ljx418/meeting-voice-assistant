# harnessOS V3.0-PhaseA Multi-App Core Readiness

文档状态：FROZEN PHASEA IMPLEMENTATION BASELINE（COMPLETED 2026-05-06）。

本文是 `docs/design/V3.0/v3_development_plan_multi_app_core.md` 中 V3.0-PhaseA 的详细实施文件。2026-05-06 完成重新验收后，本文从“实施中”转为“冻结基线”。后续仅允许追加验收证据、记录缺陷修复和做与实际实现一致的口径校正，不得被后续阶段需求直接覆写。

## 1. 目标摘要

V3.0-PhaseA 的目标不是新增业务能力，而是把 multi-app 隔离从“records/store 已开始带 scope”推进到“默认调用链真实隔离”。本阶段必须冻结 `AppProfile -> ScopeContext -> Gateway/Core service -> Store` 这条最小主链路，为后续 Pack、Connector、Meeting、Knowledge 迁移提供稳定的 app 边界。

本阶段完成后，开发团队应能明确区分两类路径：

- 默认安全路径：Gateway/Core service 的普通调用链，默认按 `app_id/project_id/workspace_id` 过滤。
- 受控兼容路径：底层 Store 不传 scope 的全量查询，仅作为管理或兼容 bypass，不得继续被视为正常调用模式。

## 1.1 冻结边界

- 本文定义的 PhaseA 合同、最小交付、DoD 和验收边界已经冻结。
- PhaseB 以后若需要新增字段、扩展协议、调整 Pack/Connector/Knowledge/Meeting 合同，必须在对应后续阶段文档中承接。
- 不允许为了后续阶段实现方便，反向弱化 PhaseA 的 scope、migration、namespace isolation 和显式真实音频验收基线。

## 2. 当前代码事实

以下事实已在当前仓库实现中验证，应作为 PhaseA 的起点，而不是目标描述：

- `core/apps/profiles.py` 已有 `AppProfile`、`AppRegistry` 和五个默认 profiles：meeting、knowledge、interview、investment、video_studio。
- `core/apps/scope.py` 已有 `ScopeContext` 与 `resolve_scope_context()`。
- `core/stores/sqlite.py` 已支持 `app_id/project_id/workspace_id` columns 与对应 indexes。
- `apps/gateway/service.py` 与 `core/services/app_service.py` 已在部分常用查询路径上传递 scope。
- `resolve_scope_context()` 已支持显式参数、`params.scope`、顶层 scope 字段和 AppProfile 默认 `project/workspace`。
- `session.list/read/transcript/events` 已收口到默认 scope 隔离，`scope_mode=all` 被显式保留为兼容/管理 bypass。
- SQLite scope 补列语义已在代码中冻结为 `v3_001_add_scope_columns`，并有 legacy schema/backfill fixtures。
- `list_*` 底层查询在不传 scope 时仍可能全量返回结果，因此当前隔离仍部分依赖调用约定。
- 当前默认回归可通过：

```bash
.venv/bin/python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'
```

- 2026-05-06 本地验证结果：`145 passed, 1 skipped, 2 deselected`。
- 2026-05-06 显式真实音频验收历史基线依赖相邻 `meeting-voice-assistant` 项目的 Meeting MCP / FunASR 服务，不属于默认 stub/contract 回归；当时在满足 `.venv + backend/venv312 + 本地服务启动` 的环境基线后，本地显式验收结果为 `2 passed`。
- 2026-05-08 之后，当前真实音频平台验收以前置 `voice_service` FunASR HTTP + MCP stdio 为准；Meeting MCP 分析服务不可用时，HarnessOS 使用本地 fallback 保持 lineage 验收不被外部开发中项目阻塞。

## 3. 影响范围

### 3.1 Protocol / Request Resolution

- RPC 请求中 `app_id/project_id/workspace_id` 的输入合同。
- CLI / Gateway / service 层未显式传 scope 时的默认来源。
- `session.start`、`turn.start`、artifact/job/trace/approval/retry 查询面的 scope 解析一致性。

### 3.2 Core Model / Store

- Session、Thread、Turn、Item、Job、Artifact、Approval、Trace、Retry、Connector 的 scope 写入完整性。
- SQLite Store 的 scope filtering 语义。
- legacy records 的 backfill 规则与 forward-only migration 口径。

### 3.3 Gateway / Service Layer

- `GatewayService` 普通 list/query 路径是否默认传入 resolved scope。
- `CoreAppService` 中 legacy gateway adapters 是否保留 scope。
- `session.list/read`、`artifact.list`、`job.list`、`trace.list`、`approval.list`、`retry.list` 的默认隔离行为。

### 3.4 Runtime / Workflow Bridge

- `turn.start` 写入 turn/item/trace/artifact 时的 scope 绑定。
- `connector.submit`、`artifact.register_external` 等桥接点的 scope 绑定。
- meeting / knowledge / video workflow 写入 Core records 时不丢失 scope。

### 3.5 Test Baseline

- 默认 stub/contract 回归必须稳定。
- namespace isolation fixture 必须覆盖同名 records 的隔离。
- 显式真实音频验收必须单独记录前置条件与失败原因。

## 4. 架构冲击范围

### Plane-1 Client / Gateway

- 受影响：入口层必须统一 scope 参数约定。
- 不改动：不新增业务专用旁路或新的 app-specific Gateway route。

### Plane-2 Protocol App Server

- 主改动：冻结 scope params 和默认解析规则。
- PhaseA 内不新增新的协议版本，只要求现有 `v1alpha` 路径在 scope 语义上保持一致。

### Plane-3 Harness Core

- 主改动：records 写入完整性、默认查询隔离、legacy backfill 口径。
- 是本阶段的主要风险承载面。

### Plane-4 Runtime Adapter

- 轻度受影响：只要求与 turn/job/artifact 相关桥接保持 scope 一致。
- 不在 PhaseA 扩展 runtime 稳态能力或 connector execution 能力。

### Plane-5 Domain Pack

- 受影响：app profile 与 pack 选择关系需要明确。
- 不在 PhaseA 冻结 PackAssemblyResult 全合同，这属于 PhaseB。

### Plane-6 Connector / Tool / Store

- 主改动：scope migration、store filtering、connector/job/artifact 相关写入的 scope 绑定。
- 不在 PhaseA 冻结 connector security descriptor，这属于 PhaseB。

## 5. 实施路径

### V3.0-PhaseA-A1 AppProfile schema + default profiles

目标：

- 把 app 隔离边界从文档概念变成稳定代码对象。
- 统一五个默认 profiles 的最小合同。

最小交付：

- 冻结当前最小字段合同：
  - `app_id`
  - `display_name`
  - `domain`
  - `default_pack`
  - `connector_refs`
  - `runtime_adapter`
  - `default_project_id`
  - `default_workspace_id`
  - `metadata`
- `app.list`、`app.get` 与单元测试返回五个默认 profiles。
- 明确哪些字段属于 PhaseA 基础合同，哪些扩展字段延后到 PhaseB 或更晚阶段。

实现重点：

- `display_name` 保留中文 UI 文案。
- 本阶段不引入未实现的 `pack_paths`、`connector_descriptor_paths`、`policy_profile` 等一等执行合同，除非明确标注为“后续阶段字段”。

建议检查点：

- `core/apps/profiles.py`
- `tests/test_v3_multi_app_core.py`

### V3.0-PhaseA-A2 ScopeContext resolver + RPC scope params

目标：

- 冻结 scope 解析优先级。
- 避免 RPC 未显式传 scope 时因为默认值不一致导致跨 app 污染。

最小交付：

- 统一解析顺序并写入文档：
  - 方法显式参数
  - `params` 中的 scope 字段
  - app/profile 默认值
  - fallback `default`
- `session.start`、`turn.start`、artifact/job/trace/approval/retry 查询面使用同一套 resolver 逻辑。
- 对非法 scope 类型维持一致错误，而不是静默降级。

实现重点：

- 只统一本地单进程调用的 scope 解析，不引入 auth/token 维度的额外复杂度。
- 若仓库内未单独实现 `AppProfileResolver`，至少保证 service 层使用同一组 resolver 函数。

建议检查点：

- `core/apps/scope.py`
- `apps/gateway/service.py`
- `tests/test_gateway_protocol.py`

### V3.0-PhaseA-A3 Core records scope fields

目标：

- 让所有 Core 记录类型都带上 app/project/workspace 三元组。
- 让 Gateway 写入 Core 的所有入口在语义上都能绑定 scope。

最小交付：

- 核对以下记录类型的普通写入路径全部可见 scope：
  - Session
  - Thread
  - Turn
  - Item
  - Job
  - Artifact
  - Approval
  - Trace
  - Retry
  - Connector
- legacy gateway adapters 不能遗漏 scope：
  - `record_runtime_session`
  - `record_gateway_event`
  - `record_gateway_trace`
  - `record_gateway_approval`
  - `record_gateway_artifact`
  - retry context 记录

实现重点：

- 验收重点不是“表里有列”，而是“普通写入路径实际写了值”。
- 优先检查 bridge/adapter 入口，而不是重复修改已经带字段的 record 定义。

建议检查点：

- `core/services/app_service.py`
- `core/stores/sqlite.py`
- `apps/gateway/runtime.py`

### V3.0-PhaseA-A4 Store filtering

目标：

- 让普通调用链默认安全。
- 把“无 scope 全量查询”降级为显式受控行为。

最小交付：

- Gateway/Core service 常规 list/query 入口默认传入 resolved scope。
- 底层 `list_*` 不传 scope 的行为被明确定义为管理/兼容 bypass。
- 至少有一组 fixture 证明 meeting 与 knowledge 同名 records 不互相可见。

实现重点：

- PhaseA 的验收重点在 service 层与 RPC 层，不要求一次性重构 Store 的所有内部默认行为。
- 任何继续依赖“调用者忘记传 scope 也没问题”的路径都应被记录为未完成项或兼容路径。

建议检查点：

- `apps/gateway/service.py`
- `core/services/app_service.py`
- `tests/test_v3_multi_app_core.py`

### V3.0-PhaseA-A5 migration/backfill

目标：

- 把当前“补列逻辑已存在”推进到“迁移口径可复现、可解释”。

最小交付：

- 固定 migration 名称：`v3_001_add_scope_columns`
- 固定 backfill 规则：
  - 默认 `app_id = "default"`
  - 明确可识别的 meeting records 可映射 `meeting`
  - 其余不猜测业务归属
- 固定 rollback 原则：
  - forward-only 优先
  - 不删除旧字段
  - 不以 destructive rollback 作为默认恢复路径

实现重点：

- 即使短期没有独立 migration runner，也必须冻结 migration 语义和 fixture 口径。
- 文档要区分“语义已冻结”和“执行器/脚本已工程化”。

建议检查点：

- `core/stores/sqlite.py`
- `docs/design/V3.0/v3_development_plan_multi_app_core.md`
- PhaseA 验收附录

### V3.0-PhaseA-A6 namespace tests + meeting regression

目标：

- 用测试证明隔离边界成立。
- 用回归证明 PhaseA 改动没有破坏现有主链路。

最小交付：

- namespace isolation fixture 覆盖至少以下四类对象：
  - session
  - thread
  - job
  - artifact
- 默认回归命令稳定通过。
- 显式真实音频验收单独维护，并明确外部服务前置条件。

实现重点：

- 当前仓库事实已表明：默认回归与真实音频验收是两条不同基线，必须显式拆开。
- 2026-05-08 PhaseD 已将 `meeting.process_recording` 降级为 runtime-backed compatibility facade；该路径现在复用 `meeting.workflow` 的 job/trace/turn/artifact 绑定。PhaseA 冻结合同本身不因该后续修复而改变。

建议检查点：

- `tests/test_v3_multi_app_core.py`
- `tests/test_gateway_protocol.py`
- `tests/test_meeting_audio_acceptance.py`
- `tests/test_meeting_turn_workflow.py`

## 6. 开发实现顺序

推荐严格按以下顺序推进，避免在 scope 语义尚未冻结时扩散修改面：

1. A1：冻结 profiles 最小合同与默认 profiles。
2. A2：冻结 resolver 规则与 RPC scope params。
3. A3：核对并补齐所有普通写入路径的 scope 绑定。
4. A4：关闭普通调用链的默认隔离缺口，并显式标记 bypass。
5. A5：冻结 migration/backfill 语义。
6. A6：用 namespace isolation 与回归测试证明上述改动成立。

## 7. 非目标

以下内容不属于 PhaseA 实施范围，避免实现时越界：

- Pack manifest 正式 schema 与 PackAssemblyResult 全合同冻结
- connector descriptor/security model
- artifact large-file 统一错误码冻结
- Meeting Pack 真实音频正式 E2E 收口
- Knowledge Pack data_service_mcp 标准 E2E
- Low-Code Workflow Runtime、Core Memory、Feedback Optimization

## 8. 文档联动要求

PhaseA 实施落盘后，以下文档必须与本文保持引用关系一致：

- `docs/design/V3.0/00_README.md`
- `docs/design/V3.0/v3_development_plan_multi_app_core.md`
- `docs/design/V3.0/v3_phasea_multi_app_core_readiness_acceptance.md`
- `docs/design/V3.0/current-vs-target-gap_v3.md`
- `docs/design/V3.0/test-acceptance-plan_v3.md`

## 9. 当前默认验证基线

默认 stub/contract 回归：

```bash
.venv/bin/python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'
```

显式真实音频验收：

```bash
.venv/bin/python -m pytest -q \
  tests/test_meeting_audio_acceptance.py \
  tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance
```

默认回归失败应优先视为 PhaseA 开发缺陷；真实音频验收失败必须先区分是代码行为缺陷，还是外部 Meeting/FunASR 服务未就绪。
