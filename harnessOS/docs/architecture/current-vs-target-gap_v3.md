# harnessOS 当前实现与 V3.0 目标架构差异

配套 draw.io 图：`docs/architecture/current-vs-target-gap_v3.drawio`

文档状态：ACTIVE V3.0 GAP / 工程路线图。V2 差异文档已归档到 `docs/history/v2-phase-docs/architecture/current-vs-target-gap_v2.md`。

本文是 V3.0 的“现状 -> 差距 -> 目标 -> 阶段 -> 验收”执行视图；实现 source of truth 仍是 `docs/design/V3.0/v3_development_plan_multi_app_core.md`。

## 1. 文档定位与阅读方式

本文同时回答四个问题：

1. V2.0 之前和 V2.0 阶段已经完成了什么。
2. 当前 V3.0 为什么要从“做更多业务”调整为“先稳 multi-app Core”。
3. 每个差距对应六大平面的哪一层、由 V3.0 哪个阶段解决。
4. 每个阶段如何拆 PR、如何验收、什么证据算完成。

阅读顺序：

```text
已完成历史路标
  -> 当前事实基线
  -> 六大平面关系
  -> 当前状态 / 差距 / 目标状态映射
  -> V3.0-PhaseA 到 V3.0-PhaseE 开发计划
  -> V3.0 验收里程碑
  -> V3.x+ 远期路线
```

### 1.1 统一编号规则

本文统一使用两套编号，避免“平面 P1/P2”和“优先级 P0/P1”混淆：

| 类型 | 规则 | 示例 | 说明 |
| --- | --- | --- | --- |
| 架构平面 | `Plane-N` | `Plane-3 Harness Core` | 表示六大架构平面，不再使用 `P1/P2`。 |
| 历史路标 | `V版本-Phase阶段-切片` | `V1.0-Phase1-A` | 表示 V3.0 前已经完成或沉淀的开发路标。 |
| 当前阶段 | `V3.0-PhaseX` | `V3.0-PhaseA` | 表示当前 active plan 的 A-E 阶段。 |
| 当前切片 | `V3.0-PhaseX-Xn` | `V3.0-PhaseB-B2` | 表示某阶段内可拆 PR / implementation slice。 |
| 验收项 | `V3.0-PhaseX-ACnn` | `V3.0-PhaseC-AC04` | 表示 acceptance checkpoint。 |
| 阻塞级别 | `P0/P1/P2` | `P0` | 仅表示优先级，不表示架构平面。 |

### 1.2 阶段状态与冻结规则

| 阶段 | 状态 | 说明 |
| --- | --- | --- |
| V3.0-PhaseA | COMPLETED / FROZEN BASELINE（2026-05-06） | 已重新完成前检查、默认回归和显式真实音频验收；后续不得被新规格直接覆写。 |
| V3.0-PhaseB | COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08） | Pack / Connector 装配边界已完成平台链路与显式真实服务双轨验收。 |
| V3.0-PhaseC | ACTIVE NEXT PHASE | 以 PhaseB 收官证据为基线进入 Job / Artifact / Governance Hardening。 |
| V3.0-PhaseD | PLANNED | 等待 PhaseB/PhaseC 稳定后进入。 |
| V3.0-PhaseE | PLANNED | 等待前置阶段稳定后进入。 |

冻结规则：

- 已完成阶段只允许缺陷修复、验收证据追加和文档口径校正。
- 若后续需求需要改变已完成阶段的合同、DoD 或验收边界，必须在后续 Phase 或新增切片中显式承接。

## 2. 远期蓝图总览

harnessOS 的远期目标是从“多业务助手集合”演进为 **可交互、可编排、可扩展、可组装的 Agent 工作流平台**。

长期形态：

- 多个 app 复用同一份 Core：meeting、knowledge、interview、investment、video_studio，以及未来外部项目。
- App 通过 AppProfile 声明 scope、pack、connector、runtime、policy，而不是把业务逻辑写进 Core/Gateway。
- Pack 是业务能力发布单元，Connector 是外部能力边界，RuntimeAdapter 是执行内核隔离层。
- Job、Artifact、Trace、Policy、Approval、Retry、Store 是跨 app 复用的治理和状态底座。
- V3.x+ 再扩展 Low-Code Workflow Runtime、Core Memory、Feedback Optimization、Workflow / Pack Library。

当前 V3.0 不直接做完整低代码平台或 Memory 系统，而是先把 reusable Core 做稳，并用 Meeting / Knowledge 作为标准迁移样板与 reference packs 验证平台抽象。

## 3. 已完成历史路标

以下路标是 V3.0 的前置事实，精简记录，不再重复旧文档的完整验收细节。

| 统一编号 / 路标 | 已完成内容 | 沉淀能力 | 对 V3.0 的意义 |
| --- | --- | --- | --- |
| V0.0-Phase0-A / 底座与骨架 | 项目可运行，CLI/API 基础入口、基础工具和健康检查可用 | 最小运行链路 | 为后续 Gateway 和 Core 演进提供可回归底座 |
| V0.5-Phase0-A / 协议优先控制面 | Gateway RPC、SSE、stdio JSONL、session/turn 生命周期、错误码和事件归一化 | 协议入口 | V3.0 继续沿用统一协议，不新增业务 Gateway 旁路 |
| V0.7-Phase0-A / 控制面收口 | turn interrupt、headless CLI 回归、RPC/stdio 同构、真实模型 smoke 门控 | 控制面稳定性 | V3.0 scope/RPC 改动必须保持 CLI/RPC/stdio 兼容 |
| V1.0-Phase1-A / Meeting MCP MVP | meeting.* RPC、Meeting MCP capabilities、文本分析、真实音频处理、会议音频自动路由 | 第一个真实业务链路 | V3.0-PhaseD 以 Meeting Pack 重新迁移并验证不回归 |
| V1.0-Phase1-C / Meeting Artifact Store | transcript、analysis、result、minutes 注册为 artifacts | 会议产物化 | V3.0-PhaseC 和 V3.0-PhaseD 继续强化 artifact lineage 和 scope 绑定 |
| V1.0-Phase1-D / Lead Orchestrator / DomainWorkflow | meeting/knowledge workflow registry、普通聊天与会议路由分流 | 初始业务编排 | V3.0-PhaseB、V3.0-PhaseD 和 V3.0-PhaseE 将 workflow 入口收敛到 Pack assembly |
| V2.0-Phase2-A / Trace/Audit | trace.list/get，turn/workflow/artifact trace chain | 可追踪性 | V3.0-PhaseC 要把 tool/job/artifact persistence 都纳入 trace |
| V2.0-Phase2-B / Approval | approval request/list/get/approve/reject | 审批生命周期 | V3.0-PhaseC RuntimeAdapter 默认注入 approval |
| V2.0-Phase2-C / Policy | policy.evaluate，写/发送/发布类动作预检 | 治理入口 | V3.0-PhaseC 扩展到 tool/job/artifact persistence |
| V2.0-Phase2-D / Retry/Resume | turn.retry，approved-action continuation | 可恢复执行 | V3.0-PhaseC 保持治理链路可重试 |
| V2.0-Phase2-E / Secret Hygiene | 持久化边界脱敏 | 密钥卫生 | V3.0-PhaseB 和 V3.0-PhaseC connector secret_ref 不落明文 |
| V2.0-Phase2-F / Persistence Hardening | 文件锁和原子写 | 本地持久化稳定性 | V3.0-PhaseA migration/backfill 不能破坏已有记录 |
| V2.0-Phase3-A / App Lifecycle | FastAPI app-scoped GatewayService DI | 服务生命周期 | V3.0 不回到模块级 gateway 单例 |
| V2.0-Baseline1.5-A / 协议与 Store | Core protocol models、CoreAppService、SQLite CRUD/filtering、legacy import | Core Store 基础 | V3.0-PhaseA 在此基础上补 app scope |
| V2.0-Baseline1.5-E / Runtime Adapter 边界 | RuntimeHandle、Simple/OpenHarness adapter、Gateway adapter path | Runtime 边界 | V3.0-PhaseC 强化 adapter-level governance injection |
| V2.0 目标架构 | 六大平面目标口径确立 | 全局架构视野 | V3.0 保留六大平面，并叠加 active overlay |
| V2.0-Roadmap3-B / Core-native session/event store | Core-native session/event store | Core-first 查询 | V3.0-PhaseA 默认按 scope 查询 |
| V2.0-Roadmap3-C / Job worker MVP | 本地 in-process Job worker、job.events、failure_context、cancel 语义 | Job MVP | V3.0-PhaseC 硬化 job 状态机和 artifact binding |
| V2.0-Roadmap3-D / Adapter governance MVP | Adapter-level governance injection MVP | 执行层治理 | V3.0-PhaseC 统一注入 scope/policy/approval/trace |
| V2.0-Roadmap3-E / Pack Assembly MVP | Pack Assembly MVP | Pack 可装配雏形 | V3.0-PhaseB 正式化 PackAssemblyResult |
| V2.0-Roadmap3-F / Connector Registry MVP | connector.list/get/health | Connector MVP | V3.0-PhaseB 增加 connector security descriptor 和 app_scope |
| V2.0-Phase4-5-A / Cross-domain MCP MVP | Meeting artifact lineage、Core-native RPC、Tool approval、connector execution、Meeting -> Knowledge cross-domain MCP | 跨域 MCP 验证 | V3.0-PhaseD 和 V3.0-PhaseE 重新作为标准 Pack + Connector 样板迁移 |

## 4. 当前事实基线

| 方向 | 当前事实 | 主要证据 | 仍需处理 |
| --- | --- | --- | --- |
| Client / Gateway | CLI、FastAPI、SSE、JSON-RPC、stdio JSONL 已有 MVP | Gateway service、headless CLI、RPC tests | 保持稳定，不新增业务旁路 |
| Core objects | Session、Thread、Turn、Item、Job、Artifact、Approval、Trace、Retry、Connector 已存在 | Core records、CoreSQLiteStore | scope 字段和默认过滤需全覆盖 |
| Store | SQLite Store 已是 Core 查询和持久化基础，已有 scope columns/indexes 和补列逻辑 | session/event Core-first 查询、CoreSQLiteStore schema | 命名 migration/backfill、scope isolation fixture；底层不传 scope 仍可全量查询，需由调用链强制传 ScopeContext |
| Runtime Adapter | Simple/OpenHarness adapter 已存在，并已有治理注入基础 | RuntimeHandle / RuntimeAdapter | scope/policy/approval/trace/secret hygiene 默认注入 |
| Governance | Policy、Approval、Trace、Retry、Secret Hygiene 已有 MVP | policy/approval/retry/trace tests | 覆盖 tool/job/artifact persistence |
| Pack | meeting、knowledge、video_studio 等 pack scaffold 已存在，PackAssemblyResult 已有 assembled/blocked/stub 基础 | packs manifests、PackRegistry | conflict/degraded/app_id/conflicts 字段和 blocked/degraded reason 仍需冻结 |
| Connector | Meeting/FunASR/Data Service MCP 已有 connector execution 基础 | ConnectorExecutionRuntime、ConnectorRegistry | ConnectorRegistry 仍有内置描述代码；security descriptor、config_ref、secret_ref、app_scope 需正式化 |
| Artifact | external registration、metadata-only read 和视频/大文件/external-only 阻断已有基础 | artifact RPC/tests | 统一错误码、preview/thumbnail/lineage、音频/图片/binary 读取策略 |
| Scope | `app_id/project_id/workspace_id` 已开始进入 records/RPC/Store | V3.0-PhaseA 初始实现 | 所有写入和查询路径必须完整传播 |

## 5. 六大平面关系与职责

```text
Plane-1 Client / Gateway
  -> Plane-2 Protocol App Server
  -> Plane-3 Harness Core
      -> Plane-4 Runtime Adapter
      -> Plane-5 Domain Pack
      -> Plane-6 Connector / Tool / Store

治理链路贯穿：
  Plane-2 request scope
  -> Plane-3 policy / trace / approval / job / artifact
  -> Plane-4 runtime execution
  -> Plane-6 connector / tool / store side effects
```

| 平面 | 职责 | 与其他平面的关系 | V3.0 状态 |
| --- | --- | --- | --- |
| Plane-1 Client / Gateway | CLI/API/Web/Bot 等入口，transport 和用户体验绑定 | 只进入 Plane-2，不直接承载业务 workflow | 已完成 / 回归保护 |
| Plane-2 Protocol App Server | JSON-RPC、SSE、stdio、method/event/error registry、SDK 合同 | 解析请求、注入 scope，进入 Plane-3 | 当前主改动 |
| Plane-3 Harness Core | Session/Turn/Store/Job/Artifact/Trace/Policy/Approval/Retry | 中心平面，连接 Plane-2/Plane-4/Plane-5/Plane-6 | 当前主改动 |
| Plane-4 Runtime Adapter | 隔离 OpenHarness/SimpleRuntime/未来 runtime | 承接 Plane-3 执行请求，调用 Plane-5/Plane-6 能力 | 当前主改动 |
| Plane-5 Domain Pack | workflow、skill、policy bundle、artifact kind、业务装配 | 通过 Plane-3 装配，通过 Plane-4 执行，声明 Plane-6 connector 依赖 | 当前主改动 |
| Plane-6 Connector / Tool / Store | MCP、本地工具、外部服务、SQLite/未来 store | 提供外部能力和持久化事实源，受 Plane-3 治理 | 当前主改动 |

## 6. 当前状态 / 差距 / 目标状态映射

| 当前状态 | 差距 | 目标状态 | 影响阶段 | 影响平面 | 验收证据 | 阻塞级别 |
| --- | --- | --- | --- | --- | --- | --- |
| Core records 已开始包含 scope 字段 | 写入路径和查询路径未全覆盖；底层 Store 不传 scope 仍可全量查询 | Gateway/Core service 调用链强制携带 ScopeContext，普通 list/query 默认过滤 | V3.0-PhaseA | Plane-2/Plane-3/Plane-6 | namespace isolation、legacy backfill、scope bypass fixture | P0 |
| SQLite Store 已是主持久化基础 | 已有命名 migration 语义和 legacy backfill fixture，但底层 `list_*` 不传 scope 仍是受控 bypass | `v3_001_add_scope_columns` forward-only migration 可回归 | V3.0-PhaseA | Plane-3/Plane-6 | migration test、legacy import fixture、compat flag test | P0 |
| Gateway RPC 可用 | 运行时仍返回 `v1alpha`；protocol version/method/event/error registry 未冻结 | `v1alpha3` protocol contract 和 errors registry 可供 SDK 使用 | V3.0-PhaseA 和 V3.0-PhaseB | Plane-2/Plane-3 | protocol registry tests | P0 |
| Pack scaffold 可见，PackAssemblyResult 已完成正式合同 | descriptor 数据外置化与 cross-app 解释文本仍可继续优化，但不再阻塞装配边界 | PackAssemblyResult 表达 assembled/blocked/degraded/stub，包含 conflicts、blocked_reason、next_actions，并对 external pack / connector gap 给出稳定解释 | V3.0-PhaseC / V3.0-PhaseD / V3.0-PhaseE | Plane-3/Plane-5 | pack.get response、missing dependency fixture、conflict fixture | P1 |
| Connector execution 有基础 | ConnectorRegistry descriptor 数据仍主要在 Python 中声明，manifest/config 驱动尚未完全落地 | ConnectorRegistry 管理 capabilities/health/config/secret/security，并支持 descriptor/config 驱动 | V3.0-PhaseC / V3.0-PhaseD / V3.0-PhaseE | Plane-5/Plane-6 | connector.health、blocked untrusted connector | P1 |
| Job worker MVP 已存在 | 状态机、progress、failure_context、artifact_ids 不完整 | queued/running/succeeded/failed/cancelled 和 artifact binding 可查询 | V3.0-PhaseC | Plane-3/Plane-6 | job state tests | P0 |
| Artifact metadata-only read 有基础 | 当前已阻断视频/大文件/external-only；音频/图片/binary、错误码和 JSON-RPC error shape 需统一 | `artifact.read` 对大文件/媒体/binary 拒绝全文读取并返回 metadata 建议和统一错误码 | V3.0-PhaseC | Plane-3/Plane-6 | artifact read policy tests | P0 |
| RuntimeAdapter 已存在 | 治理注入还不统一 | RuntimeAdapter 默认注入 scope/policy/approval/trace/secret hygiene | V3.0-PhaseC | Plane-3/Plane-4/Plane-6 | runtime governance tests | P0 |
| Meeting 已有真实音频链路 | legacy RPC/facade 仍可能成为旁路 | Meeting Pack 通过 connector 完成真实音频 E2E，legacy facade 等价 | V3.0-PhaseD | Plane-2/Plane-3/Plane-5/Plane-6 | real audio E2E、equivalence report | P1 |
| Knowledge workflow 和 data_service_mcp 有基础 | 可能直接读写 data_service 内部目录，connector 替换不清晰 | Knowledge Pack 只通过 data_service_mcp lifecycle/v2 tools 完成 E2E | V3.0-PhaseE | Plane-3/Plane-5/Plane-6 | data boundary tests、connector replacement fixture | P1 |

## 7. 阶段影响矩阵

| 平面 | 已完成历史路标 | V3.0-PhaseA | V3.0-PhaseB | V3.0-PhaseC | V3.0-PhaseD | V3.0-PhaseE | V3.x+ |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Plane-1 Client / Gateway | 已完成 CLI/API/RPC/SSE/stdio | 回归保护 | 回归保护 | 回归保护 | legacy meeting facade 兼容 | Knowledge 入口回归 | Web/Video UI 前置 |
| Plane-2 Protocol App Server | 已完成 Gateway protocol MVP | 主改动：scope params | 受影响：pack/connector RPC | 受影响：job/artifact/policy RPC | 受影响：meeting facade | 受影响：knowledge RPC | SDK/低代码协议 |
| Plane-3 Harness Core | 已完成 Core objects/SQLite MVP | 主改动：ScopeContext/Store | 受影响：assembly state | 主改动：Job/Artifact/Governance | 验证复用能力 | 验证复用能力 | Memory/Feedback |
| Plane-4 Runtime Adapter | 已完成 adapter MVP | 受影响：scope context | 受影响：connector runtime | 主改动：governance injection | Meeting 执行验证 | Knowledge 执行验证 | 多 runtime 扩展 |
| Plane-5 Domain Pack | 已完成 pack scaffold | 受影响：app profile packs | 主改动：PackAssemblyResult | 受影响：artifact/job contracts | 主改动：Meeting Pack | 主改动：Knowledge Pack | Interview/Investment/Video/Low-Code |
| Plane-6 Connector / Tool / Store | 已完成 Connector Registry MVP 和 SQLite | 主改动：scope migration | 主改动：connector security | 主改动：artifact/job/store policy | Meeting/FunASR connector | data_service_mcp connector | 外部 store/GPU/视频工具 |

## 8. V3.0 详细开发计划

V3.0-PhaseA 的详细实施文件与辅助验收基线已独立落盘到：

- `docs/design/V3.0/v3_phasea_multi_app_core_readiness.md`
- `docs/design/V3.0/v3_phasea_multi_app_core_readiness_acceptance.md`

本节继续保留执行视图摘要；PhaseA 的实现边界、影响范围、开发路径、架构冲击和验收细则以 PhaseA 专项文档为准。

### V3.0-PhaseA Multi-App Core Readiness

阶段状态：COMPLETED / FROZEN BASELINE（2026-05-06）

目标定位：

- 把 multi-app 能力从“records/store 已开始带 scope”推进到“默认调用链真正隔离”。
- 冻结 `AppProfile -> ScopeContext -> Gateway/Core service -> Store` 这条最小主链路。
- 为后续 Pack、Connector、Meeting、Knowledge 迁移提供稳定的 app 隔离边界。
- 保持默认 stub/contract 回归稳定，同时不破坏显式真实音频验收入口。

当前代码事实：

- `AppProfile`、`AppRegistry`、`ScopeContext` 已存在，meeting/knowledge/interview/investment/video_studio 五个 profile 已可加载。
- Core records 与 SQLite schema 已支持 `app_id/project_id/workspace_id`，并已有 scope indexes。
- Gateway/Core service 已开始在常用查询路径上传递 scope。
- 底层 SQLite `list_*` 在不传 scope 时仍可全量查询，但 Gateway/Core service 默认安全路径已经闭合，`scope_mode=all` 被显式保留为兼容 bypass。
- 2026-05-06 已重新完成一遍 PhaseA 端到端验收：
  - `.venv/bin/python scripts/check_real_mcp_env.py` 返回 `status=ok`
  - 默认 stub/contract 回归为 `145 passed, 1 skipped, 2 deselected`
  - 显式真实音频验收 `tests/test_meeting_audio_acceptance.py` 与 `tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` 为 `2 passed`
- 真实音频验收仍依赖外部 Meeting/FunASR 服务，但在 `.venv + backend/venv312 + 本地服务启动` 基线下已可稳定复验。
- PhaseA 相关测试、文档和验收口径现已转为冻结基线；后续阶段只能在保持兼容的前提下扩展，不能删除或弱化该阶段约束。

本阶段必须解决的问题：

- `ScopeContext` 的来源规则要冻结，避免 RPC、CLI、Gateway 内部默认值不一致。
- “普通调用链默认过滤”和“管理/兼容 bypass”要明确分层，不能继续只靠隐式约定。
- legacy records 的 backfill 口径要固定，避免后续 migration 对历史数据做不一致猜测。
- 隔离测试要从“存在 scope 字段”升级到“同名 session/job/artifact/thread 不串数据”。

建议执行顺序：

1. 先冻结 profile/schema/resolver 合同，再推进 Store 过滤。
2. 已完成 migration/backfill 约束与 fixture。
3. 已完成 namespace isolation 和默认 meeting 回归基线验证；真实音频仍保留为显式集成验收。

建议代码落点：

- `core/apps/profiles.py`
- `core/apps/scope.py`
- `apps/gateway/service.py`
- `core/services/app_service.py`
- `core/stores/sqlite.py`
- `tests/test_v3_multi_app_core.py`
- `tests/test_gateway_protocol.py`
- `tests/test_meeting_turn_workflow.py`

| 切片 | 目标 | 主要改动 | 影响平面 | 完成标准 |
| --- | --- | --- | --- | --- |
| V3.0-PhaseA-A1 | AppProfile schema + default profiles | meeting、knowledge、interview、investment、video_studio profiles | Plane-3/Plane-5/Plane-6 | profiles 可加载 |
| V3.0-PhaseA-A2 | ScopeContext resolver + RPC scope params | RPC request -> AppProfileResolver -> ScopeContext | Plane-2/Plane-3 | session/turn RPC 可传 scope |
| V3.0-PhaseA-A3 | Core records scope fields | records 增加 `app_id/project_id/workspace_id` | Plane-3 | 写入包含 scope |
| V3.0-PhaseA-A4 | Store filtering | Gateway/Core service 调用链默认传 ScopeContext；底层 Store 增加防误用 fixture 或明确 privileged bypass | Plane-3/Plane-6 | 跨 app 查询不串数据 |
| V3.0-PhaseA-A5 | migration/backfill | `v3_001_add_scope_columns` forward-only migration | Plane-3/Plane-6 | legacy records backfill |
| V3.0-PhaseA-A6 | namespace tests + meeting e2e regression | meeting/knowledge 同名 records fixture；真实音频回归 | Plane-1/Plane-2/Plane-3/Plane-5/Plane-6 | isolation + e2e 通过 |

#### V3.0-PhaseA-A1 AppProfile schema + default profiles

目标：

- 把 app 隔离边界从“文档概念”变成代码里的稳定对象。
- 统一 meeting、knowledge、interview、investment、video_studio 的默认 profile。

最小交付：

- `app_id`、`display_name`、`domain`、`default_pack`、`connector_refs`、`runtime_adapter` 字段稳定。
- 默认 profile 列表可通过 `app.list`、`app.get` 和单元测试验证。
- 明确哪些字段是当前实现已有合同，哪些仍属于 V3.0-PhaseB/Beyond 才会补齐。

实现重点：

- 当前代码里 `display_name` 使用中文 UI 文案，这可以保留；但 profile 语义字段和注释继续使用英文。
- 不要在 PhaseA 引入超前字段把 PhaseB 的 connector/security/pack path 合同偷带进来，除非文档已声明为“基础字段，行为后续补齐”。

#### V3.0-PhaseA-A2 ScopeContext resolver + RPC scope params

目标：

- 冻结 scope 的解析优先级。
- 保证 RPC 未显式传 scope 时，不会因为默认值不一致导致跨 app 污染。

最小交付：

- 明确 `params.app_id -> explicit app_id -> default_app_id` 的解析顺序。
- `session.start`、`turn.start`、`artifact/job/trace/approval/retry` 查询面使用同一套 resolver。
- 对非法 scope 值维持一致报错，而不是静默降级。

实现重点：

- PhaseA 不要求做复杂 auth scope，只要求把本地单进程调用的解析逻辑统一。
- AppProfileResolver 现在更多体现为“默认 app/profile 选择逻辑”；若未单独抽象类，至少要保证 service 层使用同一函数族。

#### V3.0-PhaseA-A3 Core records scope fields

目标：

- 让所有 Core 记录类型都带上 app/project/workspace 三元组。
- 让 Gateway 写入 Core 的所有入口在语义上都能绑定 scope。

最小交付：

- Session、Thread、Turn、Item、Job、Artifact、Approval、Trace、Retry、Connector 的写入路径全部可见 scope。
- Gateway event / approval / retry / artifact registration 这些 legacy-to-core 适配路径不能漏字段。

实现重点：

- 这里的核心不是“表里有列”，而是“每条写入路径都真的写了值”。
- 优先检查 `record_gateway_*`、`record_runtime_session`、`create_job`、`artifact.register_external`、`connector.submit` 这类桥接点。

#### V3.0-PhaseA-A4 Store filtering

目标：

- 让普通调用链默认安全。
- 把“无 scope 全量查询”降级为显式受控行为，而不是默认行为。

最小交付：

- Gateway/Core service 常规 list/query 入口默认传入 resolved scope。
- 底层 `list_*` 不传 scope 时的行为在文档和测试里被标识为管理/兼容 bypass，而不是推荐路径。
- 至少有一组 fixture 证明 meeting 与 knowledge 的同名 records 不互相可见。

实现重点：

- 这一步的验收重点应放在 service 层与 RPC 层，而不是直接把所有风险压给 SQLite store。
- 如果短期不改底层 store 默认行为，必须在测试和文档中明确“调用方责任边界”。

#### V3.0-PhaseA-A5 migration/backfill

目标：

- 把当前“补列逻辑已存在”推进到“迁移口径可复现、可解释”。

最小交付：

- 固定 `v3_001_add_scope_columns` 作为 migration 名称。
- legacy records 的 backfill 规则固定为：默认 `app_id=default`，可识别 meeting 才映射 meeting，其余不猜。
- forward-only rollback 原则写清，不做 destructive rollback 默认路径。

实现重点：

- 当前仓库已经把 `v3_001_add_scope_columns`、forward-only rollback 和 legacy backfill fixture 固化为可验证语义。
- 如果暂时没有独立 migration runner，也应有 fixture 或说明文档能复演该语义。

#### V3.0-PhaseA-A6 namespace tests + meeting e2e regression

目标：

- 用测试证明隔离边界真的成立。
- 证明 PhaseA 没把现有会议主链路打坏。

最小交付：

- namespace isolation fixture 覆盖 session/thread/job/artifact 至少四类对象。
- 默认回归命令不包含真实音频依赖时稳定通过。
- 显式真实音频验收仍保留，并明确写出外部前置条件。

实现重点：

- 当前仓库事实已经表明：默认回归和真实音频验收是两条不同基线，应明确拆开。
- 真实音频依赖未启动时，错误语义目前仍不统一；这属于后续 PhaseD 要继续收口的问题，不应在 PhaseA 文案里假装已经解决。
- PhaseA 当前不再以“继续补做真实音频验收”为未完成项；该显式集成线已经通过，后续保留为跨阶段回归线。

风险：底层 Store bypass 被误当成默认查询路径、meeting 真实音频环境不可用。

退出门：namespace isolation tests 已通过；legacy backfill 已可验证；meeting real audio e2e 已重新验收通过，并继续作为显式集成线维护。

### V3.0-PhaseB Pack Assembly + Connector Registry

详细实施文件：`docs/design/V3.0/v3_phaseb_pack_connector_registry.md`

目标定位：

- 把现有 pack scaffold 和 connector MVP 升级为正式合同。
- 让 PackAssemblyResult、connector descriptor、assembly blocked reason 成为对上层稳定可消费的接口。
- 为 Meeting/Knowledge 两个 reference packs 准备“无硬编码路径、无平台长期特判”的装配入口。

当前代码事实：

- Pack manifest、workflow templates、agents、artifact schemas 已有基础支持。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded`、`blocked_reason` / `disabled_reason` 等正式合同字段，并已通过 `pack.list/get` 暴露；blocked/degraded reason 现已开始按依赖类别细分。
- PackRegistry 已显式拒绝 duplicate pack name / domain / workflow_id，external pack roots 不再 silent overwrite。
- AppProfile `pack_paths` 已进入默认 pack registry 装配路径，external pack 现在既可通过环境变量，也可通过 app profile 声明加载。
- Connector descriptor 已开始稳定输出 security fields，并在执行前阻断未 allowlist 的 stdio command/path 与不满足 network policy 的 remote connector。
- ConnectorRegistry 已开始通过 descriptor definition 统一注册 built-in connector，并支持注入新的 sample connector definition；connector availability 也已开始严格由 registry 决定，而不是把 AppProfile refs 直接当成“可用”。
- Gateway / RuntimePool 的 pack assembly 输入已开始从 `app_registry + connector_registry` 推导；Meeting / Knowledge 的 assembly 不再只依赖固定 connector 常量集合。
- pack assembly 现在会同时校验 registry 可用性与 AppProfile enabled connectors；未显式启用的 connector 会返回 `app_profile_connector:*` blocked dependency。
- external pack `metadata.target_version` 已进入 assembly policy：缺失 target_version 目前记为 degraded，不兼容 target_version 记为 blocked。
- 2026-05-08 已完成一轮 PhaseB 收官验收：平台链路回归 `15 passed`，显式真实服务验收 `check_real_mcp_env / funasr_mcp / data_service_mcp / meeting_to_knowledge_mcp` 均返回 `status=ok`。
- PhaseB 的未尽事项已转入 PhaseC / D / E，不再作为 Pack / Connector 装配边界阻塞项。

| 切片 | 目标 | 主要改动 | 影响平面 | 完成标准 |
| --- | --- | --- | --- | --- |
| V3.0-PhaseB-B1 | Pack manifest schema | workflow、skill、connector、policy、artifact kind schema | Plane-5 | schema test 通过 |
| V3.0-PhaseB-B2 | PackAssemblyResult | 冻结 assembled/blocked/degraded/stub、reason 和 next_actions 合同 | Plane-3/Plane-5 | pack.get 返回完整装配结果 |
| V3.0-PhaseB-B3 | conflict / missing dependency | 同名 workflow/artifact kind 冲突处理 | Plane-5 | missing connector blocked |
| V3.0-PhaseB-B4 | external pack paths | AppProfile pack_paths 支持外部路径 | Plane-3/Plane-5 | external pack fixture |
| V3.0-PhaseB-B5 | connector descriptor/security | capabilities、health、config_ref、secret_ref、app_scope、trust_level；descriptor-driven registration | Plane-5/Plane-6 | untrusted connector 被拦截 |
| V3.0-PhaseB-B6 | meeting/knowledge assembly | Meeting/Knowledge connector 不硬编码路径 | Plane-2/Plane-5/Plane-6 | connector.health 走 registry |
| V3.0-PhaseB-B7 | descriptor-driven workflow registration | sample pack 注册不再依赖静态业务 factory | Plane-2/Plane-3/Plane-5 | external/sample pack fixture |

阶段展开：

- B1：Pack manifest schema
  - 开发目的：正式化 workflow、skill、connector、policy、artifact kind 声明能力。
- B2：PackAssemblyResult 合同
  - 开发目的：让 pack 装配结果可表达 assembled / blocked / degraded / stub 与原因。
- B3：冲突与缺失依赖处理
  - 开发目的：把 connector 缺失、schema 冲突、重复注册转为结构化 blocked/conflicts。
- B4：external pack paths
  - 开发目的：支持通过 AppProfile/外部路径加载 pack，并对不兼容版本做阻断。
- B5：connector descriptor / security
  - 开发目的：固定 capabilities、health、config/secret/app_scope 与 command/path/network allowlist 安全边界。
- B6：meeting / knowledge assembly
  - 开发目的：让 Meeting/Knowledge 回到 pack + registry 标准装配入口，减少硬编码路径依赖。
- B7：descriptor-driven workflow registration
  - 开发目的：让 reference pack 的发现和注册不再依赖平台层静态业务枚举。

风险：connector descriptor 外置化节奏不足、reference pack 真实业务质量波动、外部服务运行环境不一致会影响显式集成验收稳定性。

收官结论：

- V3.0-PhaseB 已完成。
- 后续只允许缺陷修复、证据追加和与实际实现一致的文档校正。
- Pack / Connector 的后续演进以 PhaseC 的治理硬化、PhaseD 的 Meeting reference pack validation、PhaseE 的 Knowledge reference pack validation 显式承接。

退出门：PackAssemblyResult 可解释 blocked；connector.health 可用；meeting/knowledge connector assembly 不硬编码路径；新增 sample pack 不需要新增平台业务分支。

### V3.0-PhaseC Job / Artifact / Governance Hardening

目标定位：

- 把“已能工作”的 job/artifact/runtime 边界推进到“治理口径稳定”。
- 在进入 Meeting/Knowledge 真实业务迁移前，把大文件读取、approval/policy/trace 注入、artifact lineage 这些基础风险收住。

当前代码事实：

- Job、Artifact、Trace、Approval、Retry 基础记录和查询面已存在。
- artifact external registration、metadata-only read、视频/大文件/external-only 阻断已部分实现。
- RuntimeAdapter governance injection 已有测试覆盖基础能力，但统一错误码和完整策略尚未冻结。

| 切片 | 目标 | 主要改动 | 影响平面 | 完成标准 |
| --- | --- | --- | --- | --- |
| V3.0-PhaseC-C1 | Job state machine | queued/running/succeeded/failed/cancelled、progress、failure_context | Plane-3 | job state tests |
| V3.0-PhaseC-C2 | Artifact external/lineage fields | external_asset_uri、preview_uri、thumbnail_uri、parent_ids、metadata | Plane-3/Plane-6 | lineage fixture |
| V3.0-PhaseC-C3 | artifact large file policy | 在现有视频/大文件/external-only 阻断基础上补音频、图片、binary 和统一错误码 | Plane-3/Plane-6 | error code asserts |
| V3.0-PhaseC-C4 | policy hooks | tool/job/artifact persistence 经过 policy/approval/trace | Plane-3/Plane-6 | governance coverage tests |
| V3.0-PhaseC-C5 | RuntimeAdapter governance injection | scope、policy、approval、trace、secret hygiene 默认注入 | Plane-3/Plane-4 | runtime governance tests |

阶段展开：

- C1/C2 负责补齐记录模型与 lineage 关系。
- C3 负责冻结 artifact read policy，而不是继续散落在实现细节里。
- C4/C5 负责把 policy/approval/trace 从“已有能力”变成“默认必经链路”。

风险：过度设计分布式队列、大文件被 inline read、高风险 tool 绕过 approval。

退出门：job 状态机通过；artifact large file policy 返回统一错误码；RuntimeAdapter 默认注入治理上下文。

### V3.0-PhaseD Meeting Reference Pack Validation

目标定位：

- 让 `packs/meeting` 成为真正的会议标准入口，而不是现有 legacy facade 的旁挂层。
- 用真实音频、artifact lineage、legacy equivalence 证明 Pack + Connector 路径可替代旧入口。

当前代码事实：

- fake/unit 级 meeting workflow、artifact registration 和 lineage 覆盖已比较稳定。
- 真实音频验收仍依赖相邻 `meeting-voice-assistant` 项目的 Meeting MCP / FunASR 服务。
- 真实依赖失败时，`meeting.process_recording` 与 `turn.start` 的失败语义还不完全一致。

| 切片 | 目标 | 主要改动 | 影响平面 | 完成标准 |
| --- | --- | --- | --- | --- |
| V3.0-PhaseD-D1 | Meeting manifest assembly | meeting workflow、skills、artifact kinds、policy bundle | Plane-5 | pack.get meeting assembled |
| V3.0-PhaseD-D2 | Meeting/FunASR connector registry | Meeting MCP / FunASR MCP 通过 ConnectorRegistry | Plane-5/Plane-6 | connector.health 通过 |
| V3.0-PhaseD-D3 | real audio Pack workflow | 真实音频 -> transcript/analysis/result/minutes | Plane-3/Plane-4/Plane-5/Plane-6 | real audio E2E |
| V3.0-PhaseD-D4 | legacy facade -> pack workflow | 旧 meeting RPC 内部走 Pack workflow | Plane-2/Plane-5 | legacy equivalence |
| V3.0-PhaseD-D5 | equivalence + lineage tests | artifact/job/trace/turn 关联完整 | Plane-3/Plane-6 | lineage query 通过 |

阶段展开：

- D1/D2 先收入口径，把 Meeting workflow 和 Meeting/FunASR connectors 都挂到标准装配入口。
- D3 是真正的业务验收门，需要外部服务前置明确、产物链路完整。
- D4/D5 负责清理旧旁路并验证 artifacts/job/trace/turn 等价与可追踪。

风险：legacy RPC 与 Pack workflow 产物不一致、真实音频服务不可用、旧旁路继续扩散。

退出门：real audio E2E 产出 transcript、analysis、result、minutes；legacy facade 与 pack workflow artifacts 等价。

### V3.0-PhaseE Knowledge Reference Pack Validation

目标定位：

- 让 `packs/knowledge` 成为个人知识库标准入口。
- 验证替换 connector 不改 Core 的目标在 Knowledge 场景下真实成立。

当前代码事实：

- Knowledge manifest、workflow scaffold、data_service_mcp connector contract 已有基础。
- Cross-domain 与 data_service_mcp 的历史真实验证证据存在，但当前 V3 文档口径下仍需补标准化 PhaseE 验收。

| 切片 | 目标 | 主要改动 | 影响平面 | 完成标准 |
| --- | --- | --- | --- | --- |
| V3.0-PhaseE-E1 | Knowledge manifest assembly | ingest/search/summarize/citation workflow | Plane-5 | pack.get knowledge assembled |
| V3.0-PhaseE-E2 | data_service_mcp registry | Knowledge MCP connector 通过 registry | Plane-5/Plane-6 | connector.health 通过 |
| V3.0-PhaseE-E3 | ingest/search/summarize/citation E2E | note、brief、citation_bundle artifacts | Plane-3/Plane-4/Plane-5/Plane-6 | data_service_mcp E2E |
| V3.0-PhaseE-E4 | data boundary tests | 不直接读写 data_service 内部目录 | Plane-5/Plane-6 | boundary tests |
| V3.0-PhaseE-E5 | connector replacement fixture | 替换 connector 不改 Core | Plane-3/Plane-5/Plane-6 | replacement fixture |

阶段展开：

- E1/E2 先冻结装配与 connector registry 入口。
- E3 验证 ingest/search/summarize/citation 的标准产物链路。
- E4/E5 负责把 data boundary 和 connector replaceability 变成可回归证据。

风险：直接读写 data_service 内部目录、source path allowlist 漏洞、connector 替换需要改 Core。

退出门：data_service_mcp E2E 通过；不直接读写内部目录；替换 connector 不改 Core。

## 9. V3.0 验收里程碑

| 编号 | 阶段 | 验收场景 | 入口/命令 | 期望结果 | 验收证据 | 阻塞级别 |
| --- | --- | --- | --- | --- | --- | --- |
| V3.0-PhaseA-AC01 | V3.0-PhaseA | AppProfile 加载 | `pytest tests/test_v3_multi_app_core.py` | 五个 app profiles 可加载 | 测试输出 | P0 |
| V3.0-PhaseA-AC02 | V3.0-PhaseA | Scope 隔离 | Core Store namespace fixture | meeting 查询不到 knowledge 同名 records | fixture 断言 | P0 |
| V3.0-PhaseA-AC03 | V3.0-PhaseA | Legacy 记录回填 | migration/import fixture | legacy records backfill 到 default 或可识别 app | migration 测试 | P0 |
| V3.0-PhaseA-AC04 | V3.0-PhaseA | RPC scope 参数 | `/v1/rpc` session/turn/artifact/job methods | 请求可传 app/project/workspace scope | RPC 响应 | P0 |
| V3.0-PhaseA-AC05 | V3.0-PhaseA | Meeting 回归 | meeting real audio e2e | transcript/minutes 不回归 | 真实音频证据 | P0 |
| V3.0-PhaseB-AC01 | V3.0-PhaseB | Pack manifest schema | pack registry tests | workflow、skill、connector、policy bundle、artifact kind 可声明并通过 registry 校验 | 测试输出 | P0 |
| V3.0-PhaseB-AC02 | V3.0-PhaseB | PackAssemblyResult | `pack.get` / pack tests | 返回 assembled/blocked/degraded/stub、missing_dependencies、conflicts、blocked_reason、next_actions | JSON 响应 | P0 |
| V3.0-PhaseB-AC03 | V3.0-PhaseB | External pack paths | external pack fixture | 外部 pack 可加载；版本不兼容时返回 blocked | fixture 结果 | P0 |
| V3.0-PhaseB-AC04 | V3.0-PhaseB | Connector Registry | `connector.health` / `connector.get` | 通过 registry 暴露 capabilities、health、config_ref、secret_ref、app_scope | connector 响应 | P0 |
| V3.0-PhaseB-AC05 | V3.0-PhaseB | Connector 安全模型 | untrusted stdio fixture | 未 allowlist command/path/network 被 blocked；合法 connector 不被误拦截 | policy 结果 | P0 |
| V3.0-PhaseB-AC06 | V3.0-PhaseB | Sample-pack neutrality | external/sample pack fixture + `workflow.list` / `turn.start` | 新增 sample pack 的发现、装配、注册与执行不需要修改 Core/Gateway 业务逻辑 | 测试输出 | P0 |
| V3.0-PhaseB-AC07 | V3.0-PhaseB | Descriptor-driven assembly | `pack.list/get` + `connector.list/get/health` | 装配结果由 AppProfile + Pack manifest + ConnectorRegistry 推导；sample connector 可通过 descriptor definition 注入 | 测试输出 | P0 |
| V3.0-PhaseC-AC01 | V3.0-PhaseC | Job 状态机 | job service tests | queued/running/succeeded/failed/cancelled 可查询 | 测试输出 | P0 |
| V3.0-PhaseC-AC02 | V3.0-PhaseC | Artifact 大文件策略 | artifact read tests | media/binary/large/external-only 拒绝全文读取 | error code 断言 | P0 |
| V3.0-PhaseC-AC03 | V3.0-PhaseC | Artifact lineage | artifact.lineage fixture | parent_ids 可查询 | lineage 输出 | P0 |
| V3.0-PhaseC-AC04 | V3.0-PhaseC | 治理覆盖 | runtime adapter tests | tool/job/artifact persistence 命中 policy/trace | trace 证据 | P0 |
| V3.0-PhaseC-AC05 | V3.0-PhaseC | Meeting 回归 | meeting real audio e2e | C 阶段改动不破坏会议链路 | 真实音频证据 | P0 |
| V3.0-PhaseD-AC01 | V3.0-PhaseD | Meeting Pack 真实音频 | real audio E2E | transcript、analysis、result、minutes artifacts | artifact ids | P0 |
| V3.0-PhaseD-AC02 | V3.0-PhaseD | Legacy 等价性 | legacy facade vs pack workflow test | artifacts 等价 | 对比报告 | P0 |

2026-05-08 PhaseB 收官证据：

- 平台链路回归：
  - `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_v3_multi_app_core.py -q -k 'test_default_pack_registry_loads_active_and_stub_packs or test_pack_registry_resolves_pack_by_domain_and_workflow or test_pack_registry_evaluates_default_pack_assembly or test_pack_registry_marks_active_pack_blocked_when_connector_missing or test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing or test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible or test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing or test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible or test_gateway_pack_list_and_get_returns_phaseb_pack_contract_fields or test_gateway_pack_list_and_get_support_app_profile_pack_paths or test_gateway_can_register_and_run_external_pack_workflow_from_manifest_entrypoint or test_gateway_connector_registry_lists_meeting_mcp or test_gateway_reference_pack_standard_entry_consistency or test_connector_registry_supports_descriptor_driven_custom_connector or test_gateway_connector_submit_blocks_unallowlisted_payload_path or test_gateway_workflow_list_and_knowledge_route'` -> `15 passed`
- 显式真实服务验收：
  - `scripts/check_real_mcp_env.py` -> `status=ok`
  - `scripts/e2e_funasr_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_data_service_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_meeting_to_knowledge_mcp_validation.py` -> `status=ok`
| V3.0-PhaseD-AC03 | V3.0-PhaseD | Meeting lineage | artifact/job/trace queries | job、trace、turn、artifact 关联完整 | lineage 查询 | P0 |
| V3.0-PhaseD-AC04 | V3.0-PhaseD | 硬编码路径清理 | rg/static tests | 标准入口不依赖硬编码 meeting path | rg 输出 | P1 |
| V3.0-PhaseE-AC01 | V3.0-PhaseE | Knowledge MCP E2E | data_service_mcp acceptance | ingest/search/citation 成功 | operation ids | P0 |
| V3.0-PhaseE-AC02 | V3.0-PhaseE | 数据边界 | boundary tests | 不直接读写 data_service 内部目录 | path/assert logs | P0 |
| V3.0-PhaseE-AC03 | V3.0-PhaseE | Connector 替换 | connector replacement fixture | 替换 connector 不改 Core | fixture 结果 | P0 |
| V3.0-PhaseE-AC04 | V3.0-PhaseE | Citation artifacts | knowledge workflow E2E | note、brief、citation_bundle artifacts | artifact ids | P1 |
| V3.0-PhaseE-AC05 | V3.0-PhaseE | Lineage 完整性 | trace/artifact/job queries | trace、artifact、job、turn 关联完整 | lineage 查询 | P1 |

默认测试使用 stub / contract mode。真实 MCP 验收必须显式开启环境变量或手工启动相关服务。

## 10. V3.x+ 远期阶段影响范围

| 阶段 | 目标 | 主要影响平面 | 前置条件 | 非当前 V3.0 原因 |
| --- | --- | --- | --- | --- |
| V3.1 Interview Pack | 面试流程、技能学习、模拟面试、评分报告 | Plane-5/Plane-6，受 Plane-2/Plane-3/Plane-4 支撑 | Meeting/Knowledge reference packs 验证完成；Pack/Connector 稳定 | 需要先验证 Pack 样板 |
| V3.2 Investment Pack | 投资研究、风险摘要、策略复盘、只读治理默认 | Plane-3/Plane-5/Plane-6 | Governance/Policy model 稳定 | 金融域治理要求更高 |
| V3.3 Video Studio Integration | 外部视频项目、渲染任务、媒体 artifact lineage | Plane-3/Plane-4/Plane-5/Plane-6 | Job/Artifact 大文件策略稳定 | 大文件和长任务必须先硬化 |
| V3.x Low-Code Workflow Runtime | 配置式 workflow、节点、边、审批点、局部重跑 | Plane-2/Plane-3/Plane-5 | PackAssemblyResult 和 protocol registry 稳定 | 当前优先级是 Core 稳定 |
| V3.x Core Memory | Session/Project/Workflow/Agent/User/Evaluation Memory | Plane-3/Plane-4/Plane-5 | Scope、Policy、Trace 稳定 | Memory 需要治理和可撤销边界 |
| V3.x Feedback Optimization | 反馈驱动局部重跑和 workflow 优化 | Plane-3/Plane-5/Plane-6 | Artifact lineage 和 evaluation model 稳定 | 当前无稳定评价闭环 |
| V3.x Workflow / Pack Library | 可复用 workflow/role/skill/connector templates | Plane-2/Plane-5/Plane-6 | 低代码和 Pack schema 成熟 | 需要先沉淀真实 Pack |

## 11. 当前禁区

- 不允许把新业务逻辑写入 Core。
- 不允许新增业务专用 Gateway 旁路。
- 不允许绕过 RuntimeAdapter 调用底层 runtime。
- 不允许高风险 tool 绕过 Policy / Approval。
- 不允许大视频文件通过 `artifact.read` 全量读取。
- 不允许多个 app 查询结果互相串数据。
- 不允许把 Low-Code、Core Memory、Feedback、Workflow Library 放进 V3.0-PhaseA 到 V3.0-PhaseE 验收。
