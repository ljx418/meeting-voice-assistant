# harnessOS V3.0 阶段验收标准与测试用例集

文档状态：ACTIVE V3.0 ACCEPTANCE。V2 阶段验收文档已归档到 `docs/history/v2-phase-docs/acceptance-test-cases_v2.md`。

## 1. 验收总原则

- 当前最高优先级是把 harnessOS Core 做稳，不新增业务旁路。
- 新业务不得写入 Core 或 Gateway，必须通过 AppProfile、Pack、Connector、RuntimeAdapter 接入。
- 每阶段必须保持默认 stub/contract 回归稳定，meeting 真实音频 E2E 作为显式外部服务验收单独维护。
- 多 app 查询默认按 `app_id/project_id/workspace_id` 过滤，禁止串数据。
- Meeting / Knowledge 在 V3.0 中是 reference packs / validation samples；其通过验收的前提之一是平台没有为它们继续固化新的业务特判。

## 2. V3.0-PhaseA Multi-App Core Readiness

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseA-AC01 | AppProfile registry | `pytest tests/test_v3_multi_app_core.py` | meeting、knowledge、interview、investment、video_studio profiles 可加载 |
| V3.0-PhaseA-AC02 | ScopeContext 写入 | Core Store unit tests | Session/Thread/Turn/Item/Job/Artifact/Approval/Trace/Retry 写入包含 scope |
| V3.0-PhaseA-AC03 | Scope 默认过滤 | Gateway/Core service namespace fixture | 普通调用链中 meeting 查询不到 knowledge 同名 records；底层 Store 全量查询只能作为受控 bypass |
| V3.0-PhaseA-AC04 | RPC scope | `/v1/rpc` session/turn/artifact/job methods | 请求可传 app/project/workspace scope |

## 3. V3.0-PhaseB Pack Assembly + Connector Registry

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseB-AC01 | Pack manifest schema | pack registry tests | workflow、skill、connector、policy bundle、artifact kind 可声明，并能通过 registry 校验 |
| V3.0-PhaseB-AC02 | PackAssemblyResult | `pack.list/get` | 返回 assembled/blocked/degraded/stub、missing_dependencies、conflicts、blocked_reason、next_actions |
| V3.0-PhaseB-AC03 | External pack paths | 环境变量或 AppProfile pack_paths | 外部 pack 可加载；版本不兼容时返回 blocked，而不是 silent overwrite |
| V3.0-PhaseB-AC04 | Connector Registry | `connector.list/get/health` | connector 从 registry 读取 capabilities、health、config_ref、secret_ref、app_scope、trust_level 等 descriptor 字段 |
| V3.0-PhaseB-AC05 | Connector security | connector security fixture | 未 allowlist 的 stdio command/path/network 被 blocked；合法 connector 维持可执行 |
| V3.0-PhaseB-AC06 | Sample-pack neutrality | external/sample pack fixture + `workflow.list` / `turn.start` | 新增 sample pack 的发现、装配、注册与执行不需要修改 Core/Gateway 业务逻辑 |
| V3.0-PhaseB-AC07 | Descriptor-driven assembly | `pack.list/get` + `connector.list/get/health` | 装配结果由 AppProfile + Pack manifest + ConnectorRegistry 推导；sample connector 可通过 descriptor definition 注入，而不是固定业务常量集合 |

2026-05-08 收官证据：

- 平台链路回归：
  - `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_v3_multi_app_core.py -q -k 'test_default_pack_registry_loads_active_and_stub_packs or test_pack_registry_resolves_pack_by_domain_and_workflow or test_pack_registry_evaluates_default_pack_assembly or test_pack_registry_marks_active_pack_blocked_when_connector_missing or test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing or test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible or test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing or test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible or test_gateway_pack_list_and_get_returns_phaseb_pack_contract_fields or test_gateway_pack_list_and_get_support_app_profile_pack_paths or test_gateway_can_register_and_run_external_pack_workflow_from_manifest_entrypoint or test_gateway_connector_registry_lists_meeting_mcp or test_gateway_reference_pack_standard_entry_consistency or test_connector_registry_supports_descriptor_driven_custom_connector or test_gateway_connector_submit_blocks_unallowlisted_payload_path or test_gateway_workflow_list_and_knowledge_route'` -> `15 passed`
- 显式真实服务验收：
  - `scripts/check_real_mcp_env.py` -> `status=ok`
  - `scripts/e2e_funasr_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_data_service_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_meeting_to_knowledge_mcp_validation.py` -> `status=ok`

## 4. V3.0-PhaseC Job / Artifact / Governance Hardening

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseC-AC01 | Job worker MVP | job service tests | queued/running/succeeded/failed/cancelled、progress、failure_context、artifact_ids 可查询 |
| V3.0-PhaseC-AC02 | External job ref | connector execution tests | external_job_ref 与 parent_job_id 持久化 |
| V3.0-PhaseC-AC03 | External artifact | `artifact.register_external` | external_asset_uri、preview_uri、thumbnail_uri、metadata 可查询 |
| V3.0-PhaseC-AC04 | Large file policy | `artifact.read` | 在现有视频/音频/图片/binary/大文件/external-only 阻断基础上，媒体与大文件拒绝全文读取并返回统一错误码 |
| V3.0-PhaseC-AC05 | Artifact lineage | `artifact.lineage` | parent_ids 可形成 brief -> script -> render_output 等链路 fixture |
| V3.0-PhaseC-AC06 | Governance injection | runtime adapter tests | policy、approval、trace、secret hygiene、scope context 默认注入 |

## 5. V3.0-PhaseD Meeting Reference Pack Validation

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseD-AC01 | Meeting pack assembly | `pack.get(app_id=meeting)` | meeting workflow、connector、skills、artifact kinds、policy 装配成功，且结果可视为 reference pack 装配 |
| V3.0-PhaseD-AC02 | Meeting MCP connector | connector registry | Meeting MCP / FunASR MCP 通过 ConnectorRegistry 接入 |
| V3.0-PhaseD-AC03 | Real audio E2E | 显式 meeting real audio acceptance | 在 Meeting MCP/FunASR 服务已启动前提下生成 transcript、analysis、result、minutes artifacts |
| V3.0-PhaseD-AC04 | Lineage completeness | artifact/job/trace queries | job、trace、turn、artifact 关联完整 |
| V3.0-PhaseD-AC05 | Legacy facade equivalence | legacy meeting RPC test | legacy RPC 与 pack workflow 产物等价 |
| V3.0-PhaseD-AC06 | No platform special-case regression | workflow/registry tests | Meeting 通过验收时不要求新增 Core/Gateway 业务旁路 |

## 6. V3.0-PhaseE Knowledge Reference Pack Validation

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseE-AC01 | Knowledge pack assembly | `pack.get(app_id=knowledge)` | ingest/search/summarize/citation workflow 装配成功，且结果可视为 reference pack 装配 |
| V3.0-PhaseE-AC02 | Knowledge MCP connector | connector registry | Knowledge MCP 通过 ConnectorRegistry 接入，可替换 connector 不改 Core |
| V3.0-PhaseE-AC03 | Knowledge data boundary | data_service_mcp tests | 只调用 lifecycle/v2 tools，不直接读写 data_service 内部目录 |
| V3.0-PhaseE-AC04 | Knowledge artifacts | workflow E2E | 输出 note、brief、citation_bundle artifacts |
| V3.0-PhaseE-AC05 | Trace completeness | trace/artifact/job queries | trace、artifact、job、turn 关联完整 |
| V3.0-PhaseE-AC06 | No platform special-case regression | workflow/registry tests | Knowledge 通过验收时不要求新增 Core/Gateway 业务旁路 |

## 7. Deferred

以下不进入 V3.0-PhaseA 到 V3.0-PhaseE 验收：

- Low-Code Workflow Runtime
- Core Memory System
- Feedback Optimization Loop
- Workflow Library
- V3.1 Interview Pack
- V3.2 Investment Pack
- V3.3 Video Studio external project integration
