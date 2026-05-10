# harnessOS V3.0 Multi-App Core Development Plan

文档状态：V3.0 FINAL CLOSEOUT PLAN。本文记录 V3.0-PhaseA 到 V3.0-PhaseE 的完成状态、冻结合同和 V3.x+ 后续边界。

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
| V3.0-PhaseB | COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08） | Pack / Connector 装配边界已完成收官验收；后续仅允许缺陷修复、证据追加和文档校正。 |
| V3.0-PhaseC | COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08） | Job / Artifact / Governance 平台合同已完成收官验收；后续仅允许缺陷修复、证据追加和文档校正。 |
| V3.0-PhaseD | VALIDATION PASSED | Meeting Pack assembly、legacy facade equivalence、strict/resilience real-audio E2E 已通过；业务分析质量继续由外部 Meeting MCP 迭代。 |
| V3.0-PhaseE | VALIDATION PASSED | Knowledge Pack + migrated `/workspace/data_service` MCP E2E 已通过；HarnessOS 仍只通过 connector 边界调用 data_service。 |

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

阶段状态：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）

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
- 2026-05-08 已完成平台链路与显式真实服务双轨验收；PhaseB 的剩余工作已转入 PhaseC / PhaseD / PhaseE。

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

当前验收状态：

- 2026-05-08 平台链路收官回归：
  - `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_v3_multi_app_core.py -q -k 'test_default_pack_registry_loads_active_and_stub_packs or test_pack_registry_resolves_pack_by_domain_and_workflow or test_pack_registry_evaluates_default_pack_assembly or test_pack_registry_marks_active_pack_blocked_when_connector_missing or test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing or test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible or test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing or test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible or test_gateway_pack_list_and_get_returns_phaseb_pack_contract_fields or test_gateway_pack_list_and_get_support_app_profile_pack_paths or test_gateway_can_register_and_run_external_pack_workflow_from_manifest_entrypoint or test_gateway_connector_registry_lists_meeting_mcp or test_gateway_reference_pack_standard_entry_consistency or test_connector_registry_supports_descriptor_driven_custom_connector or test_gateway_connector_submit_blocks_unallowlisted_payload_path or test_gateway_workflow_list_and_knowledge_route'` -> `15 passed`
- 2026-05-08 显式真实服务验收：
  - `scripts/check_real_mcp_env.py` -> `status=ok`
  - `scripts/e2e_funasr_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_data_service_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_meeting_to_knowledge_mcp_validation.py` -> `status=ok`
- 以当前文档口径，V3.0-PhaseB 已达到完成定义；后续相关工作只允许作为 PhaseC / D / E 的显式承接项继续推进。

### V3.0-PhaseC：Job / Artifact / Governance Hardening

阶段状态：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）

- JobRecord 增加 `app_id/project_id/workspace_id`、`external_job_ref`、`parent_job_id`、`progress`、`failure_context`、`artifact_ids`。
- ArtifactRecord 增加 `app_id/project_id/workspace_id`、`external_asset_uri`、`preview_uri`、`thumbnail_uri`、`parent_ids`、`metadata`。
- 新增 `artifact.register_external`、`artifact.read_metadata`、`artifact.lineage`。
- Policy 覆盖 tool invocation、job execution、artifact persistence。
- RuntimeAdapter 默认注入 policy、approval、trace、secret hygiene、scope context。

Definition of Done：

- Job 状态机支持 queued/running/completed/failed/cancelled。
- JobRecord 支持 progress、failure_context、external_job_ref、parent_job_id、artifact_ids。
- Artifact large file policy 和 `ARTIFACT_READ_BLOCKED` JSON-RPC error shape 冻结。
- Policy 覆盖 tool invocation、job execution、artifact persistence。
- RuntimeAdapter 默认注入 scope、policy、approval、trace、secret hygiene。
- 当前代码状态：`failure_context` 已同时写入 `JobRecord.failure_context` 顶层字段与 metadata；`connector.submit(defer=True)` 与 approval-required 路径已作为正式 job 路径，approval retry 会复用同一 connector job，不再产生 orphan queued job；`connector.submit` 可从 `session_id` 继承 scope，connector/job 查询和取消路径已做 scope 隔离。
- 当前代码状态：`artifact.read` 已阻断视频、音频、图片、binary、external-only 和大文件 inline read，并返回 `ARTIFACT_READ_BLOCKED`、blocked reason、metadata-only artifact 与 `artifact.read_metadata` 建议；`artifact.register_external`、`artifact.read_metadata`、`artifact.lineage` 已作为统一 registry 视图使用。
- 当前代码状态：job、connector execution、artifact read/lineage 已进入 Core trace；RuntimeAdapter governance metadata 已包含 scope 三元组；治理链路覆盖正式 tool / connector / job / artifact 主路径，底层 Store 的无 scope 调用仅保留为兼容/管理 bypass。

PR slices / implementation order：

1. `V3.0-PhaseC-C1` JobRecord schema + state machine hardening。
2. `V3.0-PhaseC-C2` ArtifactRecord external/preview/thumbnail/lineage fields。
3. `V3.0-PhaseC-C3` artifact read metadata-only + large file policy。
4. `V3.0-PhaseC-C4` Policy hooks for tool/job/artifact persistence。
5. `V3.0-PhaseC-C5` RuntimeAdapter governance context injection tests。
6. `V3.0-PhaseC-C6` platform-neutral governance audit。

当前验收状态：

- 2026-05-08 默认全量回归：`.venv/bin/python -m pytest -q` -> `182 passed, 3 skipped, 6 warnings`
- 2026-05-08 PhaseC / Meeting 相关切片：`.venv/bin/python -m pytest tests/test_meeting_turn_workflow.py tests/test_gateway_protocol.py::test_knowledge_workflow_connector_approval_can_retry_to_completion tests/test_gateway_protocol.py::test_job_and_connector_rpcs_enforce_scope_and_inherit_session_scope tests/test_acceptance_scripts.py -q` -> `14 passed, 1 skipped`
- 以当前文档口径，V3.0-PhaseC 已达到完成定义；Meeting facade / real-audio 验证已在 PhaseD 收官，Knowledge data-boundary 验证继续留在 PhaseE。

### V3.0-PhaseD：Meeting Reference Pack Validation

阶段状态：VALIDATION PASSED（Meeting Pack assembly、legacy facade equivalence、strict/resilience real-audio E2E passed）

目标定位：

- `packs/meeting` 作为 reference pack 验证真实外部执行链路和 artifact lineage，不作为平台内置业务特权入口。
- PhaseD 是 Meeting Pack 文档同步 + 后续实施阶段，不重开 PhaseA-C 平台合同。
- 标准链路必须通过 Pack / Connector / RuntimeAdapter / Job / Artifact / Trace 完成，旧 meeting RPC 只保留兼容 facade。

PhaseD Preconditions：

- `app_id=meeting` profile 可用。
- `ScopeContext` 可用于 session/thread/turn/job/artifact/trace。
- `PackAssemblyResult` 可查询。
- `ConnectorRegistry` 支持 `connector.get` / `connector.health` / capabilities。
- `artifact.lineage`、`job.get/events`、`trace.list/get` 可用。
- RuntimeAdapter governance injection 生效。
- meeting 与 knowledge scope isolation 测试通过。

Definition of Done：

- Meeting reference pack 通过真实音频 E2E。
- 通过 `funasr_mcp` 与 `meeting_voice_mcp` 生成 transcript、analysis、result、minutes artifacts。
- legacy meeting facade 与 pack workflow 产出等价。
- job、trace、turn、thread、artifact 关联完整。
- 旧硬编码 meeting 旁路被移除或降级为兼容入口。
- strict mode 不允许 silent fallback 掩盖 connector 缺失；resilience mode 的 fallback 必须写入 trace 与 artifact metadata。
- Meeting 验证结果能够证明平台不需要为该 pack 继续保留 Core/Gateway 特判。
- 当前代码状态：Meeting workflow 真实音频路径已优先通过相邻 `voice_service` 的 `funasr_mcp.funasr_recognize_file` 执行转写；该路径支持 approval-required -> `approval.approve` -> `turn.retry`，并复用同一个 connector job。
- 当前代码状态：FunASR 转写成功后，若相邻 `meeting-voice-assistant` 的 Meeting MCP 分析阶段不可用或超时，HarnessOS 会使用本地 fallback 生成 `transcript / analysis / result / minutes` artifacts。这个 fallback 是为了让 HarnessOS 的 platform lineage 验收不被仍在开发中的外部项目阻塞，不表示 Meeting 业务分析质量已完成。
- 当前收官项：legacy meeting facade 与 pack workflow artifact/job/trace/lineage equivalence 已补齐；Meeting MCP 业务分析质量继续由外部依赖迭代，不再作为 HarnessOS PhaseD 平台验收阻塞项。

PR slices / implementation order：

1. `V3.0-PhaseD-D0` Documentation Sync：同步 active plan、status、gap、drawio、acceptance、test plan。
2. `V3.0-PhaseD-D1` Meeting Pack Assembly：标准化 `packs/meeting` 结构；`pack.get(app_id=meeting)` 必须返回 `meeting.workflow`、`funasr_mcp`、`meeting_voice_mcp`、`meeting-minutes`、`action-items`、`meeting.default`、`transcript/analysis/result/minutes`、assembly status、`missing_dependencies`、`blocked_reason`、`next_actions`。
3. `V3.0-PhaseD-D2` Meeting Connector Contracts：`funasr_mcp` 负责 `audio.transcribe`；`meeting_voice_mcp` 负责 `meeting.analyze` / `minutes.generate`；二者都必须通过 ConnectorRegistry 管理；connector 缺失、stdio 路径不可用、tool 不存在时返回 explainable blocked/degraded。
4. `V3.0-PhaseD-D3` Meeting Workflow Standard Path：`audio input -> transcribe -> analyze -> generate minutes -> register transcript/analysis/result/minutes -> bind job/trace/turn/thread`；strict mode 禁止 silent fallback；resilience mode fallback 必须记录 fallback reason。
5. `V3.0-PhaseD-D4` Legacy Facade Compatibility：legacy `meeting.process_recording` 内部调用 `meeting.workflow`，返回兼容 response，并写入 deprecation warning。
6. `V3.0-PhaseD-D5` Equivalence / Lineage Verification：比较 artifact kinds、parent_ids、metadata、scope、job binding、trace binding、lineage roots/leaves/edges、response compatibility；`connector_result` 可作为额外 root/leaf，但不能替代四件套。
7. `V3.0-PhaseD-D6` Real Audio Strict + Resilience E2E：固化 `HARNESS_FUNASR_MCP_EXECUTION=stdio`、`HARNESS_MEETING_E2E_AUDIO_DIR`、`HARNESS_MEETING_E2E_STRICT`、`./scripts/e2e_meeting_preflight.sh`、`./scripts/e2e_meeting_validation.sh "<audio path>"`。
8. `V3.0-PhaseD-D7` Architecture / Acceptance Docs Update：实施完成后再次同步 architecture status、gap md、gap drawio、acceptance cases、test plan。

Legacy deprecation warning shape：

```json
{
  "legacy_method": "meeting.process_recording",
  "replacement": "turn.start / meeting.workflow",
  "sunset_stage": "stage_1_compat_facade",
  "message": "meeting.process_recording is deprecated; use the Meeting Pack workflow.",
  "trace_event": "legacy_facade.deprecation_warning"
}
```

Real-audio failure classification：

- FunASR fail：transcription 未完成，strict/resilience 都失败。
- `meeting_voice_mcp` fail：strict mode 失败；resilience mode 可 fallback。
- fallback fail：resilience mode 失败。
- artifact 缺失：失败。
- lineage 缺失：失败。
- scope 串数据：失败。
- `connector_result` 存在但 transcript/analysis/result/minutes 四件套缺失：失败。

当前验收状态：

- 2026-05-08 MCP 环境前检查：`HARNESS_MEETING_MCP_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio HARNESS_FUNASR_MCP_ENDPOINT=http://127.0.0.1:8001 .venv/bin/python scripts/check_real_mcp_env.py` -> `status=ok`
- 2026-05-08 real-audio Meeting lineage：`./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`，生成 `transcript / analysis / result / minutes` artifacts，并保留 `connector_result` 作为 FunASR MCP 证据节点。
- 2026-05-08 PhaseD focused regression：`.venv/bin/python -m pytest tests/test_meeting_legacy_facade_equivalence.py tests/test_meeting_strict_vs_resilience_mode.py tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py -q` -> `23 passed, 1 skipped`
- 2026-05-08 PhaseD full regression：`.venv/bin/python -m pytest tests -q` -> `193 passed, 3 skipped, 6 warnings`
- 2026-05-08 PhaseD preflight：`HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio ./scripts/e2e_meeting_preflight.sh` -> `status=ok`
- 2026-05-08 PhaseD resilience E2E：`HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio ./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`, `strict=false`, `resilience_fallback_reason=null`
- 2026-05-08 PhaseD strict E2E：`HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio HARNESS_MEETING_E2E_STRICT=1 HARNESS_MEETING_ANALYSIS_TIMEOUT=90 ./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`, `strict=true`, `resilience_fallback_reason=null`
- 2026-05-09 PhaseE focused regression：`.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py::test_gateway_pack_list_and_get tests/test_knowledge_pack_assembly.py tests/test_knowledge_connector_contract.py tests/test_knowledge_workflow_standard_path.py tests/test_knowledge_data_boundary.py tests/test_knowledge_lineage_equivalence.py tests/test_knowledge_connector_replacement.py tests/test_knowledge_scope_isolation.py -q` -> `32 passed`
- 2026-05-09 新增 PhaseE 显式入口：`HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio ./scripts/e2e_knowledge_validation.sh [document]`，用于验证 standard Gateway path 下的 `source_reference / note / brief / citation_bundle` artifacts、lineage、job binding 和 trace binding。默认未设置真实 MCP 环境变量时返回 blocked，不能作为通过结果。
- 2026-05-09 Data Service MCP 默认路径已随迁移更新为 `/Users/Zhuanz/Desktop/workspace/data_service/backend`，默认解释器优先使用 `/Users/Zhuanz/Desktop/workspace/data_service/backend/.venv/bin/python`。
- 2026-05-09 PhaseE real MCP E2E：`HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio DATA_SERVICE_WORKSPACE_ROOT=/Users/Zhuanz/Desktop/workspace/data_service/harnessos-phasee-knowledge DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS=/Users/Zhuanz/Desktop/workspace/data_service DATA_SERVICE_ALLOWED_SOURCE_ROOTS=/Users/Zhuanz/Desktop/workspace/data_service ./.venv/bin/python scripts/e2e_knowledge_validation.py --query "HarnessOS PhaseE Knowledge Pack validation"` -> `status=passed`，输出 `source_reference / note / brief / citation_bundle`，`lineage_count=4`，`workflow_job_id=job_659f10470de5`，`trace_count=27`。

### V3.0-PhaseE：Knowledge Reference Pack Validation

- `packs/knowledge` 作为 reference pack 验证状态型 connector、workflow lifecycle、data boundary 与 connector replaceability。
- 通过 Knowledge MCP connector 接入本地知识库服务。
- 支持 ingest、search、summarize、citation。
- 输出 source_reference、note、brief、citation_bundle artifacts。
- 确保 trace、artifact、job、turn 关联完整。
- 不改 Core 即可替换 knowledge connector。
- PhaseE 内容不得作为 PhaseD 完成条件；PhaseD 只同步 Knowledge 边界，不实现 Knowledge E2E。

Definition of Done：

- Knowledge reference pack 通过 `data_service_mcp` 完成 ingest/search/citation E2E。
- 输出 source_reference、note、brief、citation_bundle artifacts，connector_result 只能作为额外证据节点，不能替代四件套。
- Knowledge workflow 不直接读写 data_service 内部目录。
- trace、artifact、job、turn 关联完整。
- 替换 knowledge connector 不需要修改 Core。
- Knowledge 验证结果能够证明平台不需要为该 pack 继续保留 Core/Gateway 特判。

PR slices / implementation order：

1. `V3.0-PhaseE-E1` Knowledge pack manifest assembly 完整化。
2. `V3.0-PhaseE-E2` data_service_mcp connector registry 接入。
3. `V3.0-PhaseE-E3` ingest/search/summarize/citation workflow E2E。
4. `V3.0-PhaseE-E4` data boundary：allowlist、symlink escape、source size limit。
5. `V3.0-PhaseE-E5` connector replacement fixture：替换 data_service_mcp 实现不改 Core/Gateway 主结构。
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

当前代码状态：ConnectorRegistry 已能登记 Meeting/FunASR/Data Service/ComfyUI 等 connector，并能执行 `connector.health`；内置 connector 现已开始通过 descriptor definition 驱动注册，而不是散落在平台层的条件分支。PhaseB 收官后，剩余 descriptor 外置化工作转入后续阶段，不再阻塞 Pack / Connector 装配边界完成判定。

参考：

- MCP Intro: https://modelcontextprotocol.io/docs/getting-started/intro
- MCP Tool Annotations: https://blog.modelcontextprotocol.io/posts/2026-03-16-tool-annotations/

## 8. Job Worker MVP Boundary

V3.0-PhaseC 只实现本地最小 worker，不实现分布式调度。

包含：

- local in-process async worker
- SQLite-backed job state
- queued/running/completed/failed/cancelled
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

当前代码状态：已阻断 video、audio、image、binary、large 和 external-only artifact inline read；统一错误码已收敛为 `ARTIFACT_READ_BLOCKED`，JSON-RPC error shape 遵守 `result` 与 `error` 不同时存在。

默认阈值：`MAX_INLINE_ARTIFACT_BYTES = 1048576`。

冻结错误码：

- `ARTIFACT_READ_BLOCKED`

兼容说明：旧错误码语义仍可在 metadata / blocked reason 中表达，但调用方不应再依赖 `ARTIFACT_TOO_LARGE`、`ARTIFACT_BINARY_READ_BLOCKED` 或 `ARTIFACT_EXTERNAL_ONLY` 作为主合同。

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

当前代码已完成 V3.0-PhaseA 到 V3.0-PhaseE 的收官验收：

- `core.apps` 新增 AppProfile/AppRegistry/ScopeContext。
- Core records 与 SQLite Store 支持 `app_id/project_id/workspace_id`。
- Gateway RPC 开始接受 scope 参数。
- Artifact 支持 external registration 和 metadata-only read。
- `artifact.read` 拒绝视频、音频、图片、binary、大文件和 external-only 全量读取。
- PackAssemblyResult 已完成 assembled/blocked/degraded/stub 正式合同。
- ConnectorExecutionRuntime 已能创建 connector job 并登记结果 artifact。
- connector approval retry 会复用同一个 connector job，job / connector RPC 已纳入 scope 隔离。
- Meeting workflow 已通过 `voice_service` FunASR MCP stdio connector 完成真实音频转写和 lineage 验收。
- Meeting PhaseD 已完成 pack assembly、legacy facade equivalence、strict/resilience real-audio E2E。
- Knowledge PhaseE 已完成 pack assembly、data boundary、connector replacement、source_reference/note/brief/citation_bundle artifacts、lineage/job/trace binding 和迁移后的 `/Users/Zhuanz/Desktop/workspace/data_service/backend` stdio MCP 真实 E2E。

下一步是 V3.0 closeout 维护与 V3.x+ 扩展规划；不再新增 V3.0 平台开发，不把 Interview / Investment / Video Studio 或 Low-Code / Memory / Feedback 需求回写为 V3.0 未完成项。
