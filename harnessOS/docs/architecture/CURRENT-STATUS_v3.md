# harnessOS Current Status V3.0

文档状态：ACTIVE V3.0 STATUS。V2 当前状态文档已归档到 `docs/history/v2-phase-docs/architecture/CURRENT-STATUS_v2.md`。

## 1. 当前阶段

当前活动计划是：

```text
V3.0-PhaseA Multi-App Core Readiness
V3.0-PhaseB Pack Assembly + Connector Registry
V3.0-PhaseC Job / Artifact / Governance Hardening
V3.0-PhaseD Meeting Pack E2E Migration
V3.0-PhaseE Knowledge Pack E2E Migration
```

V3.1 Interview、V3.2 Investment、V3.3 Video Studio 在 Meeting / Knowledge 迁移完成后再推进。

阶段状态：

- V3.0-PhaseA：COMPLETED / FROZEN BASELINE（2026-05-06）
- V3.0-PhaseB：ACTIVE NEXT PHASE
- V3.0-PhaseC/D/E：PLANNED

冻结规则：

- 已完成阶段只允许缺陷修复、证据追加和与实际实现一致的文档校正。
- 后续阶段若引入新合同，必须在自己的阶段文档里承接，不能直接回写已完成阶段的定义和验收口径。

## 2. 当前已落地事实

- AppProfile、AppRegistry、ScopeContext 已有基础实现。
- Core records 与 SQLite Store 已开始支持 `app_id/project_id/workspace_id`。
- Gateway RPC 已开始接受 scope 参数。
- Scope resolver 已支持显式参数、`params.scope`、顶层 scope 字段和 AppProfile 默认 `project/workspace`。
- `session.list/read/transcript/events` 已纳入默认 scope 隔离；`scope_mode=all` 被保留为显式兼容 bypass。
- `turn.start` 的单次 scope override 现在会贯穿 `turn.started -> item.delta -> turn.completed/failed` 整条事件链，session summary / turn memory context 也会跟随该 turn 的真实 scope。
- `turn.continue`、`turn.retry`、`turn.interrupt` 现在会在 Gateway 层复用 session scope 校验，避免跨 app/session 操作运行态。
- Artifact 已支持 external registration 和 metadata-only read。
- `artifact.read` 已开始阻断视频和大文件全文读取。
- `artifact.get/read_metadata/read`、legacy `trace.list/get`、`approval.list/get/approve/reject` 现在也已纳入默认 scope 收口；approval / trace 持久化记录会保留 `app_id/project_id/workspace_id`。
- SQLite scope 补列语义已冻结为 `v3_001_add_scope_columns`，legacy import fixture 已验证默认回填到 `default`，可识别的 meeting legacy 记录回填到 `meeting`。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded`、`blocked_reason` / `disabled_reason` 等正式合同字段，并通过 `pack.list/get` 暴露。
- PackRegistry 现在会拒绝同名 pack、同 domain 和同 workflow_id 的重复注册；多根目录 external pack 加载不再 silent overwrite。
- ConnectorExecutionRuntime 已能通过 ConnectorRegistry 创建 Core Job 并记录 connector result artifact。
- `connector.submit(defer=True)` 现在会启动后台执行路径；MCP connector 若返回 `isError=true`，job 会落为 `failed` 而不是错误地记为 `completed`。
- Connector descriptor 现在会稳定输出 `trust_level`、`execution_mode`、`allowed_commands`、`allowed_paths`、`network_policy`、`secret_ref`、`app_scope` 等 security fields。
- ConnectorExecutionRuntime 现在会在执行前强制校验 stdio command/path allowlist，并对 remote connector 执行 network policy 阻断。
- Meeting / Knowledge pack scaffold 已存在，但仍需按 V3.0-PhaseD 和 V3.0-PhaseE 完成标准 Pack + Connector E2E 迁移。
- 2026-05-06 在仓库本地 `.venv` 下执行默认主线回归 `python -m pytest tests -q -k 'not phase1_meeting_acceptance_uses_workspace_audio_dir and not phase1b_real_audio_turn_start_acceptance'`，当前结果为 `161 passed, 1 skipped, 2 deselected`。
- 2026-05-06 已重新完成一遍 PhaseA 端到端验收：在显式启动本地 Meeting / FunASR 服务、通过 `scripts/check_real_mcp_env.py` 前检查、并使用默认解析到 `meeting-voice-assistant/backend/venv312/bin/python` 的 MCP 解释器后，真实音频显式验收 `tests/test_meeting_audio_acceptance.py` 与 `tests/test_meeting_turn_workflow.py::test_phase1b_real_audio_turn_start_acceptance` 本地结果为 `2 passed`。

## 3. 当前缺口

- ScopeContext 主链路已贯穿常用写入和查询路径，但底层 Store 仍保留不传 scope 的兼容/管理 bypass。
- SQLite Store 已有 scope columns、indexes 和补列逻辑，但底层 `list_*` 不传 scope 时仍可全量查询；默认过滤需要由 Gateway/Core service 调用链强制传入 ScopeContext。
- default-safe query 路径已扩展到 artifact / trace / approval 这批 legacy RPC，但仍有部分底层记录查询依赖调用侧显式带 scope 或走 `scope_mode=all` 兼容 bypass。
- PackAssemblyResult 合同已经冻结到当前实现，但 external pack version policy、跨 app 装配冲突和 severity 分层仍需后续阶段继续收口。
- ConnectorRegistry 仍包含内置 connector 描述代码；Connector Security Model 的 manifest/config 驱动化仍需后续阶段继续推进。
- Protocol version 目前仍是 Gateway `v1alpha`；`v1alpha3`、method/event/error registry、SDK/Auth MVP 尚未冻结。
- Artifact read policy 已阻断视频、大文件和 external-only；音频/图片/binary、统一错误码和 JSON-RPC error shape 尚未冻结。
- Meeting legacy RPC 还需 sunset plan 和 facade equivalence tests。
- 真实音频验收仍依赖相邻 `meeting-voice-assistant` 项目的 Meeting MCP 与 FunASR 服务；若外部服务未启动，或未满足 `.venv + backend/venv312` 环境基线，显式真实音频验收仍会失败。
- 真实音频链路在 `turn.start` 失败时已不再出现空 `final_text` 伪成功；但 `meeting.process_recording` 与 `turn.start` 的错误 envelope / code 仍未完全统一。
- 纯文本会议分析路径现在不再依赖 `meeting_voice_mcp` 健康状态；只有真实音频路径才要求显式 Meeting/FunASR 外部服务可用。

## 4. 冻结原则

- Core 不承载业务逻辑。
- Gateway 不新增业务专用旁路。
- Runtime 只能通过 RuntimeAdapter 调用。
- 高风险 tool/job/artifact persistence 必须经过 Policy / Approval / Trace。
- 大视频文件不得通过 `artifact.read` 全量读取。
- 多 app 查询默认 scope filtering。
