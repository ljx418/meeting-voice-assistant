# harnessOS Current Status V3.0

文档状态：V3.0 FINAL CLOSEOUT STATUS。V2 当前状态文档已归档到 `docs/history/v2-phase-docs/architecture/CURRENT-STATUS_v2.md`。

2026-05-09 closeout：V3.0-PhaseA 到 V3.0-PhaseE 已完成；当前文档用于记录实际实现、验收证据和 V3.x+ 后续边界。

## 1. 当前阶段

V3.0 已完成计划是：

```text
V3.0-PhaseA Multi-App Core Readiness
V3.0-PhaseB Pack Assembly + Connector Registry
V3.0-PhaseC Job / Artifact / Governance Hardening
V3.0-PhaseD Meeting Reference Pack Validation
V3.0-PhaseE Knowledge Reference Pack Validation
```

V3.1 Interview、V3.2 Investment、V3.3 Video Studio 在 Meeting / Knowledge 两个 reference packs 完成平台化验证后再推进。
V3.0 当前把 Meeting / Knowledge 作为 reference packs / validation samples，而不是平台内置业务终局。

阶段状态：

- V3.0-PhaseA：COMPLETED / FROZEN BASELINE（2026-05-06）
- V3.0-PhaseB：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）
- V3.0-PhaseC：COMPLETED / PHASE CLOSEOUT BASELINE（2026-05-08）
- V3.0-PhaseD：VALIDATION PASSED（Meeting Pack assembly、legacy facade equivalence、strict/resilience real-audio E2E passed）
- V3.0-PhaseE：VALIDATION PASSED（Knowledge Pack + migrated data_service MCP E2E passed）

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
- `artifact.read` 已开始阻断视频、音频、图片、binary、external-only 和大文件全文读取。
- `artifact.get/read_metadata/read`、legacy `trace.list/get`、`approval.list/get/approve/reject` 现在也已纳入默认 scope 收口；approval / trace 持久化记录会保留 `app_id/project_id/workspace_id`。
- SQLite scope 补列语义已冻结为 `v3_001_add_scope_columns`，legacy import fixture 已验证默认回填到 `default`，可识别的 meeting legacy 记录回填到 `meeting`。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded`、`blocked_reason` / `disabled_reason` 等正式合同字段，并通过 `pack.list/get` 暴露。
- PackRegistry 现在会拒绝同名 pack、同 domain 和同 workflow_id 的重复注册；多根目录 external pack 加载不再 silent overwrite。
- AppProfile `pack_paths` 已进入默认 pack registry 装配路径，external pack 现在既可通过环境变量，也可通过 app profile 声明加载。
- ConnectorExecutionRuntime 已能通过 ConnectorRegistry 创建 Core Job 并记录 connector result artifact。
- `connector.submit(defer=True)` 现在会启动后台执行路径；MCP connector 若返回 `isError=true`，job 会落为 `failed` 而不是错误地记为 `completed`。
- `connector.submit` 的 approval-required 路径已冻结为正式 job 路径：第一次 submit 创建并绑定一个 queued job，approval 通过后复用同一个 job 继续执行，不再产生 orphan queued job；mismatched approval 不会先创建脏 job。
- `connector.submit` 在请求未显式带 scope 时会从 `session_id` 继承 session scope；`connector.poll/cancel/collect` 和 `job.get/events/cancel` 已纳入 scope 隔离，跨 app/workspace job id 访问会被拒绝。
- Connector descriptor 现在会稳定输出 `trust_level`、`execution_mode`、`allowed_commands`、`allowed_paths`、`network_policy`、`secret_ref`、`app_scope` 等 security fields。
- ConnectorExecutionRuntime 现在会在执行前强制校验 stdio command/path allowlist，并对 remote connector 执行 network policy 阻断。
- Gateway / RuntimePool 的 pack assembly 输入已开始从 `app_registry + connector_registry` 推导，Meeting / Knowledge 的 assembly 不再只依赖固定 connector 常量集合；connector 可用性现在由 registry 决定，AppProfile 只负责 enabled refs。
- 多个 AppProfile 共享同一 domain 时，assembly 输入现在会按 domain 合并 enabled connectors，避免 shared-domain 情况下出现错误覆盖。
- pack assembly 现在会同时校验 registry 可用性与 AppProfile enabled connectors；未启用的 connector 会返回 `app_profile_connector:*` blocked dependency。
- external pack `metadata.target_version` 已进入 assembly policy：缺失 target_version 目前记为 degraded，不兼容 target_version 记为 blocked。
- PackAssemblyResult 的 blocked/degraded reason 已开始按具体依赖类别细分；external pack target_version、policy bundle、connector capability 等情况会返回更具体的解释文本。
- workflow registration 现在优先按 pack-declared entrypoint 动态加载；external sample pack 已可通过 manifest entrypoint 被发现并执行。
- ConnectorRegistry 现在已开始通过 descriptor definition 统一注册 built-in connector，并支持注入新的 sample connector definition。
- `local.knowledge` 已进入默认 registry 作为 knowledge legacy fallback contract stub，默认 Knowledge pack 的 assembly 不再依赖“只在 AppProfile 里声明但 registry 中不存在”的 connector。
- Meeting pack 现在已显式声明 `meeting_voice_mcp` 与 `funasr_mcp` 双 connector 合同；meeting workflow 的最终文本会标注实际走过的 connector 标准入口，便于对齐 pack assembly 与 runtime path。
- Meeting workflow 真实音频路径现在优先通过 `voice_service` 的 `funasr_mcp.funasr_recognize_file` 执行转写；该路径支持 approval-required -> `approval.approve` -> `turn.retry`，并复用同一个 connector job。
- FunASR 转写成功后，若相邻 `meeting-voice-assistant` 的 Meeting MCP 分析阶段不可用或超时，HarnessOS 会使用平台内本地 fallback 生成 `transcript / analysis / result / minutes` 四类 meeting artifacts，保证 Meeting lineage 验收不被仍在开发中的外部项目阻塞。
- PhaseD 实施已按 D0-D7 完成：Documentation Sync、Meeting Pack Assembly、Meeting Connector Contracts、Meeting Workflow Standard Path、Legacy Facade Compatibility、Equivalence / Lineage Verification、Real Audio Strict + Resilience E2E、Architecture / Acceptance Docs Update。
- PhaseD strict mode 不允许 silent fallback 掩盖 connector 缺失；resilience mode 允许 `meeting_voice_mcp` 不可用时 fallback，但 trace 和 artifact metadata 必须记录 fallback reason，且不能声明 Meeting 业务质量完成。
- PhaseB 现已拆出独立实施文件 `docs/design/V3.0/v3_phaseb_pack_connector_registry.md`，后续 Pack / Connector 合同变更以该专项文件与 final closeout plan 联动维护。
- Meeting pack scaffold、connector contracts、legacy facade equivalence 和 strict/resilience real-audio E2E 已完成 PhaseD 验证；Knowledge pack 已完成标准 Pack + Connector + artifact/lineage 代码侧迁移，并已通过迁移后的 data_service MCP 真实 E2E。
- 当前仍有静态 workflow compatibility fallback 和部分内置 connector 描述数据，这说明 reference packs 尚未完全从平台层抽离。
- 2026-05-06 的 PhaseA 默认回归与真实音频显式验收已作为历史冻结证据保留；当前最新默认回归和真实音频 lineage 证据以后续 2026-05-08 记录为准。
- PhaseC 后 FunASR MCP 默认解释器基线切换到 `voice_service/.venv/bin/python`；真实音频平台验收以 `voice_service` FunASR HTTP + MCP stdio 为前置。
- 2026-05-08 已完成一轮 PhaseB 收官验收：
  - 平台链路回归 `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_v3_multi_app_core.py -q -k 'test_default_pack_registry_loads_active_and_stub_packs or test_pack_registry_resolves_pack_by_domain_and_workflow or test_pack_registry_evaluates_default_pack_assembly or test_pack_registry_marks_active_pack_blocked_when_connector_missing or test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing or test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible or test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing or test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible or test_gateway_pack_list_and_get_returns_phaseb_pack_contract_fields or test_gateway_pack_list_and_get_support_app_profile_pack_paths or test_gateway_can_register_and_run_external_pack_workflow_from_manifest_entrypoint or test_gateway_connector_registry_lists_meeting_mcp or test_gateway_reference_pack_standard_entry_consistency or test_connector_registry_supports_descriptor_driven_custom_connector or test_gateway_connector_submit_blocks_unallowlisted_payload_path or test_gateway_workflow_list_and_knowledge_route'` -> `15 passed`
  - 显式真实服务验收 `scripts/check_real_mcp_env.py`、`scripts/e2e_funasr_mcp_validation.py`、`scripts/e2e_data_service_mcp_validation.py`、`scripts/e2e_meeting_to_knowledge_mcp_validation.py` 均返回 `status=ok`
- 2026-05-08 已完成 PhaseC 平台硬化与 Meeting real-audio lineage 验证：
  - 默认全量回归 `.venv/bin/python -m pytest -q` -> `182 passed, 3 skipped, 6 warnings`
  - PhaseC / Meeting 相关切片 `.venv/bin/python -m pytest tests/test_meeting_turn_workflow.py tests/test_gateway_protocol.py::test_knowledge_workflow_connector_approval_can_retry_to_completion tests/test_gateway_protocol.py::test_job_and_connector_rpcs_enforce_scope_and_inherit_session_scope tests/test_acceptance_scripts.py -q` -> `14 passed, 1 skipped`
  - MCP 环境前检查 `HARNESS_MEETING_MCP_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio HARNESS_FUNASR_MCP_ENDPOINT=http://127.0.0.1:8001 .venv/bin/python scripts/check_real_mcp_env.py` -> `status=ok`
  - real-audio Meeting lineage `./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`，生成 `transcript / analysis / result / minutes` artifacts，并保留 `connector_result` 作为 FunASR MCP 证据节点。
- 2026-05-08 已完成 PhaseD Meeting Pack 收官验证：
  - 默认全量回归 `.venv/bin/python -m pytest tests -q` -> `193 passed, 3 skipped, 6 warnings`
  - PhaseD focused regression `.venv/bin/python -m pytest tests/test_meeting_legacy_facade_equivalence.py tests/test_meeting_strict_vs_resilience_mode.py tests/test_meeting_gateway.py tests/test_meeting_turn_workflow.py -q` -> `23 passed, 1 skipped`
  - preflight `HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio ./scripts/e2e_meeting_preflight.sh` -> `status=ok`
  - resilience real-audio E2E `HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio ./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`, `strict=false`, `resilience_fallback_reason=null`
  - strict real-audio E2E `HARNESS_MEETING_E2E_AUDIO_DIR=/Users/Zhuanz/Desktop/workspace/音频资料 HARNESS_FUNASR_MCP_EXECUTION=stdio HARNESS_MEETING_E2E_STRICT=1 HARNESS_MEETING_ANALYSIS_TIMEOUT=90 ./scripts/e2e_meeting_validation.sh "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=passed`, `strict=true`, `resilience_fallback_reason=null`
- 2026-05-09 已完成 PhaseE Knowledge reference pack 代码侧第一轮落地：
  - `packs/knowledge` 已标准化为 `source_reference / note / brief / citation_bundle` 四件套 artifact contract，并保留 `connector_result` 作为额外证据节点。
  - `data_service_mcp` connector registry 已暴露 lifecycle/source/build/query/summarize/citation 语义 capabilities。
  - Knowledge workflow 标准入口会通过 `data_service_mcp.knowledge_query_v2 / knowledge_ingest_v2` 生成 artifact、job、trace、turn 绑定；source path 增加 allowlist、symlink escape、size limit 检查。
  - 新增 `scripts/e2e_knowledge_validation.sh` 作为真实 MCP 显式验收入口；默认未设置 `HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 时返回 blocked。
  - PhaseE focused regression `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py::test_gateway_pack_list_and_get tests/test_knowledge_pack_assembly.py tests/test_knowledge_connector_contract.py tests/test_knowledge_workflow_standard_path.py tests/test_knowledge_data_boundary.py tests/test_knowledge_lineage_equivalence.py tests/test_knowledge_connector_replacement.py tests/test_knowledge_scope_isolation.py -q` -> `32 passed`
  - Data Service MCP 默认路径已随迁移更新为 `/Users/Zhuanz/Desktop/workspace/data_service/backend`，默认解释器优先使用 `/Users/Zhuanz/Desktop/workspace/data_service/backend/.venv/bin/python`。
  - PhaseE real MCP E2E：`HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio DATA_SERVICE_WORKSPACE_ROOT=/Users/Zhuanz/Desktop/workspace/data_service/harnessos-phasee-knowledge DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS=/Users/Zhuanz/Desktop/workspace/data_service DATA_SERVICE_ALLOWED_SOURCE_ROOTS=/Users/Zhuanz/Desktop/workspace/data_service ./.venv/bin/python scripts/e2e_knowledge_validation.py --query "HarnessOS PhaseE Knowledge Pack validation"` -> `status=passed`，输出 `source_reference / note / brief / citation_bundle`，`lineage_count=4`，`workflow_job_id=job_659f10470de5`，`trace_count=27`。
- 以当前证据，Pack / Connector 装配边界、PhaseC Job / Artifact / Governance 平台合同、PhaseD Meeting reference pack migration 和 PhaseE Knowledge reference pack 合同均已完成主要落地；PhaseE 真实 data_service MCP 验收已在迁移后的 `/workspace/data_service` 路径通过。

## 3. 当前缺口

- ScopeContext 主链路已贯穿常用写入和查询路径，但底层 Store 仍保留不传 scope 的兼容/管理 bypass。
- SQLite Store 已有 scope columns、indexes 和补列逻辑，但底层 `list_*` 不传 scope 时仍可全量查询；默认过滤需要由 Gateway/Core service 调用链强制传入 ScopeContext。
- default-safe query 路径已扩展到 artifact / trace / approval / job / connector job RPC；底层 Store 仍保留不传 scope 的兼容/管理 bypass，默认隔离由 Gateway/Core service 调用链强制执行。
- PackAssemblyResult 合同、external pack paths、sample-pack neutrality 和 Meeting / Knowledge 标准装配入口已完成 PhaseB 收官；更细粒度的 cross-app severity 文案优化转入后续阶段。
- ConnectorRegistry 已转向 definition-driven registration，但 descriptor 数据仍主要在 Python 中声明；manifest/config 驱动化转入 V3.x+。
- 若新增 pack 仍需要修改 Core/Gateway 业务逻辑，则应视为平台化缺口，而不是正常扩展方式。
- Protocol version 目前仍是 Gateway `v1alpha`；`v1alpha3`、method/event/error registry、SDK/Auth MVP 转入 V3.x+。
- Artifact read policy 已阻断视频、音频、图片、binary、external-only 和大文件，并冻结 `ARTIFACT_READ_BLOCKED` JSON-RPC error shape，返回 blocked reason、metadata-only artifact 和 `artifact.read_metadata` 建议。
- Background job worker、workflow runtime、connector runtime 和 Knowledge MCP runner 现在都会把 `failure_context` 同时写入 `JobRecord.failure_context` 顶层字段与 metadata。
- Job lifecycle、connector execution、artifact read/lineage 已进入 Core trace；RuntimeAdapter governance metadata 已包含 scope 三元组。
- Meeting legacy RPC 已降级为 compatibility facade，并具备 deprecation warning trace event 和 facade equivalence tests；warning shape 包含 `legacy_method`、`replacement`、`sunset_stage`、`message`、`trace_event`。
- 真实音频验收现在依赖相邻 `voice_service` 的 FunASR HTTP + MCP stdio 能力；相邻 `meeting-voice-assistant` 的分析服务可用时会被优先使用，不可用或超时时 HarnessOS 会使用本地 fallback 生成 meeting artifacts。
- FunASR MCP 显式验收现在通过 `voice_service/.venv` 前检查 `mcp + funasr_service.mcp_stdio`，不再要求旧的 `aiohttp` 检查。
- 真实音频链路在 `turn.start` 失败时已不再出现空 `final_text` 伪成功；但 `meeting.process_recording` 与 `turn.start` 的错误 envelope / code 仍未完全统一。
- 纯文本会议分析路径现在不再依赖 `meeting_voice_mcp` 健康状态；真实音频路径要求 FunASR HTTP 服务可用，Meeting MCP 分析服务可用性不再阻塞 HarnessOS lineage 验收。
- PhaseE 只在当前阶段同步 Knowledge 边界；Knowledge E2E、data boundary 和 connector replacement 不作为 PhaseD 完成条件。

## 4. 冻结原则

- Core 不承载业务逻辑。
- Gateway 不新增业务专用旁路。
- Meeting / Knowledge 只作为 reference packs 验证平台抽象，不授予平台层长期特权。
- Runtime 只能通过 RuntimeAdapter 调用。
- 高风险 tool/job/artifact persistence 必须经过 Policy / Approval / Trace。
- 大视频文件不得通过 `artifact.read` 全量读取。
- 多 app 查询默认 scope filtering。
