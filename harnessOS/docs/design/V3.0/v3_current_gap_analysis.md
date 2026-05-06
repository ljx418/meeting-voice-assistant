# harnessOS V3.0 Current Gap Analysis

文档状态：CODE FACTS / GAP AUDIT。本文记录当前代码事实和 V3.0 活动计划缺口，不替代 `v3_development_plan_multi_app_core.md`。

已完成阶段冻结规则：

- V3.0-PhaseA 已在 2026-05-06 完成重新验收并进入冻结基线。
- 后续 gap 分析只记录“跨阶段遗留问题”或“PhaseA 缺陷修复”，不再把新的 PhaseB-E 需求回写成 PhaseA 的未完成项。

## 1. 已具备能力

- Core 已有 Session、Thread、Turn、Item、Job、Artifact、Trace、Approval、Retry、Connector records。
- SQLite Store 已是 Core 查询和持久化基础，并已有 scope columns、indexes 和兼容补列逻辑。
- Pack Registry 已支持 manifest、workflow template、agents、connector refs、policy bundle、artifact schemas。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded` 和 `blocked_reason` 合同，`pack.list/get` 现在可稳定返回这些字段。
- PackRegistry 已经开始显式拒绝 duplicate pack name / domain / workflow_id，external pack roots 不再 silent overwrite。
- ConnectorExecutionRuntime 已支持 gated MCP stdio execution。
- Meeting Pack 和 Knowledge Pack 已有 manifest 与 workflow scaffold。
- V3.0-PhaseA 基础 scope 字段已经开始进入 records、Store schema 和 Gateway RPC。
- Artifact 已开始支持 external registration、metadata-only read，以及视频/大文件/external-only inline read 阻断。
- PhaseA 主链路中的 resolver、Gateway session 查询隔离、命名 migration 语义和 legacy backfill fixture 已落地。
- turn 级 scope override、memory scope、`turn.continue/retry/interrupt` 的 Gateway scope 防护已经补进主链路。
- ConnectorExecutionRuntime 现在已具备 `defer=True` 后台执行路径，并会把 MCP `isError=true` 正确映射为 failed job。
- Artifact / Trace / Approval 的 legacy RPC 默认 scope 收口已经补齐，approval / trace 写入记录也会保留 scope 三元组。
- PhaseA 的默认回归、显式真实音频验收与环境前检查已形成冻结基线，相关测试与文档只允许做兼容性维护。

## 2. 主要差距

- Multi-app scope 仍需要继续补齐到剩余底层查询与少数兼容路径；底层 Store 不传 scope 时仍可全量查询，需要由 Gateway/Core service 调用链默认传 ScopeContext，或增加受控 bypass 语义。
- AppProfile / AppRegistry 已有基础实现，但 schema、profile 示例、resolver 默认规则和 allowed scope 仍需冻结。
- Gateway initialize 目前仍返回 `v1alpha`；缺少 `v1alpha3` protocol version、method schema、event schema、error code registry。
- 缺少 Python / TypeScript SDK 与 external app contract。
- 缺少 auth / local capability token 最小策略。
- ConnectorRegistry 仍有较多默认 connector 描述代码，需要进一步改为 connector manifest/config 驱动。
- ConnectorRegistry / ConnectorExecutionRuntime 已开始执行 security descriptor：stdio connector 的 command/path allowlist 与 remote connector 的 network policy 会在执行前阻断。
- Pack Assembly 已有正式结果合同，但仍需要继续推进 manifest/config 驱动、severity 分级和跨 app external pack 版本兼容策略。
- Meeting 仍存在 legacy RPC facade，需要 legacy API sunset plan。
- Knowledge Pack 已声明 data_service_mcp，但还需要补端到端 Pack workflow 验证和 data boundary 验收。
- Artifact 保护已经有基础行为，但还需冻结音频/图片/binary 策略、阈值、错误码和 JSON-RPC error shape。
- 仓库自有默认主线回归在 2026-05-06 的最新本地验证结果已更新为 `161 passed, 1 skipped, 2 deselected`；真实音频验收已被显式排除为独立集成线。
- 真实音频显式集成线已在 2026-05-06 的本地 `.venv + backend/venv312` 环境基线下重新验收通过，说明当前代码实现与相邻服务在满足前检查条件时可跑通完整 transcript/analysis/result/minutes 链路。
- `turn.start` 会议路径在失败时不再返回空 `final_text` 伪成功；但 `meeting.process_recording` 与 `turn.start` 的错误 envelope / code 仍未完全统一，这说明 PhaseD 的失败合同尚未冻结。
- 纯文本会议分析不再依赖 `meeting_voice_mcp` 健康状态，因此 Meeting workflow 的剩余 gap 主要集中在真实音频链路、失败合同和 legacy facade 对齐，而不是文本 path 的可用性。

## 3. 阻塞项

- 必须先稳定 Pack manifest schema 与 PackAssemblyResult 合同，再做 meeting / knowledge 标准迁移。
- 必须先把 ConnectorRegistry 抽象到 app_scope/config_ref/secret_ref/security descriptor，才能支持外部项目复用 Core。
- 必须先冻结 artifact large file policy，避免后续 Video Studio 接入时通过 `artifact.read` 全量读取大视频。
- 必须先冻结 RuntimeAdapter governance injection 规则，避免高风险 tool 绕过 Policy / Approval。

## 4. 当前实施原则

- Core 只提供协议、状态、治理、作业、产物、运行时适配边界。
- 业务能力只能通过 Pack / Connector / RuntimeAdapter 接入。
- 旧接口保留兼容，但不能作为新业务扩展模板。
- 代码主回归应以 stub / contract mode 为默认基线；真实 MCP / 真实音频验收属于显式集成验证。
- 真实音频 E2E 仍需保持不回归，但当前执行前提是相邻 Meeting/FunASR 服务先可用，且 MCP 默认解释器优先使用 `meeting-voice-assistant/backend/venv312/bin/python`。

## 5. 待补验收边界

- Namespace isolation：meeting 与 knowledge 同名 session/job/artifact 不互相可见。
- Protocol compatibility：JSON-RPC `result` 与 `error` 不同时存在，错误码来自 registry。
- Connector security：untrusted stdio connector 未在 allowlist 内时 blocked；remote connector 的 network policy 也要保持显式可解释。
- Artifact read：视频、音频、图片、binary、external-only 和超过阈值文件返回 metadata-only error，并使用统一错误码。
- Legacy meeting RPC：legacy facade 与 pack workflow 产出等价 artifacts，并在后续阶段输出 deprecation warning。
