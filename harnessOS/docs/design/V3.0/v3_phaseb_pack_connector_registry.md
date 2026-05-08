# harnessOS V3.0-PhaseB Pack Assembly + Connector Registry

文档状态：COMPLETED PHASEB BASELINE（2026-05-08）。本文是 `docs/design/V3.0/v3_development_plan_multi_app_core.md` 中 `V3.0-PhaseB` 的详细实施文件与收官验收基线。

## 1. 阶段目标与意义

V3.0-PhaseA 冻结的是 multi-app scope/core 隔离边界；V3.0-PhaseB 要冻结的是 pack/connector 装配边界。

本阶段的核心目标不是新增业务，而是把系统从“已经能跑通部分 pack/connector MVP”推进到“对上层稳定可消费、可解释失败、可受控执行”的标准装配层：

- Pack 必须从“目录里有 manifest 文件”升级为“可被 Gateway/Core 稳定消费的装配单元”。
- Connector 必须从“能调用的工具入口”升级为“受 registry 管理、带安全边界和健康语义的资源”。
- Meeting / Knowledge 这两个 reference packs 的后续验证必须通过 pack + registry 标准入口完成，而不是继续依赖硬编码路径或隐式旁路。
- V3.0-PhaseC 的 Job / Artifact / Governance 只有建立在稳定的 PackAssemblyResult 和 ConnectorRegistry 合同上才有意义。

一句话总结：PhaseA 解决“隔离边界存在”，PhaseB 解决“装配边界稳定”。

## 2. 当前代码事实

以下事实已在当前仓库实现中存在，应作为 PhaseB 的起点，而不是目标愿景：

- Pack Registry 已支持 manifest、workflow template、agents、connector refs、policy bundle、artifact schemas。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded`、`blocked_reason` / `disabled_reason` 等正式合同字段，并通过 `pack.list/get` 暴露。
- PackRegistry 已显式拒绝 duplicate pack name、duplicate domain、duplicate workflow_id；external pack roots 不再 silent overwrite。
- AppProfile `pack_paths` 已开始进入默认 pack registry 装配路径，external pack 不再只能依赖环境变量注入。
- Connector descriptor 已稳定输出 `trust_level`、`execution_mode`、`allowed_commands`、`allowed_paths`、`allowed_network_hosts`、`network_policy`、`secret_ref`、`app_scope` 等安全字段。
- PackAssemblyResult 的 blocked/degraded reason 已开始按 connector missing、manifest schema、external pack target_version、policy bundle、connector capability 等类别细分，不再只返回统一模糊文案。
- ConnectorExecutionRuntime 已在执行前阻断未 allowlist 的 stdio command/path 与不满足 network policy 的 remote connector。
- Gateway / RuntimePool 的 pack assembly 输入已开始从 `app_registry + connector_registry` 推导，不再只依赖固定 connector 常量集合。
- connector 可用性现在由 ConnectorRegistry 决定，AppProfile connector refs 只负责“是否启用”；不再把“已启用但未注册”的 connector 误判成可用。
- 多个 AppProfile 共享同一 domain 时，assembly 输入现在会按 domain 合并 enabled connectors，避免 cross-app connector refs 被最后一个 profile 覆盖。
- pack assembly 现在会同时校验 “connector 已在 registry/可用集合中” 与 “connector 已被对应 AppProfile 显式启用”；未启用时返回 `app_profile_connector:*` blocked dependency。
- external pack `metadata.target_version` 已进入装配策略：缺失时返回 `target_version:missing` 并标记为 degraded；版本不兼容时返回 `target_version:*` 并标记为 blocked。
- workflow registration 已开始优先按 pack-declared entrypoint 动态加载；external/sample pack 已可通过 manifest entrypoint 被发现、注册和执行。
- ConnectorRegistry 现在已支持通过 descriptor definition 注入新的 connector 合同，默认 built-in connector 也开始使用同一注册路径。
- `local.knowledge` 已进入内置 registry 作为 legacy fallback contract stub，Knowledge pack 的 connector refs 与默认可用集合不再分叉。
- Meeting pack 现在已显式声明 `meeting_voice_mcp + funasr_mcp` 两个标准 connector，并要求对应 tool capability；meeting workflow 的最终输出也会显式标注实际走过的 connector 标准入口。
- `connector.submit(defer=True)` 已具备后台执行路径，MCP `isError=true` 也会被映射为 failed job。

PhaseB 收官后转入后续阶段的边界：

- ConnectorRegistry 虽然已经转向 definition-driven registration，但 built-in descriptor 数据仍主要在 Python 中声明；后续继续在 PhaseC / D / E 向 config/manifest 驱动推进。
- cross-app assembly conflicts 的更细粒度 severity 文案仍可在后续阶段继续收紧，但不再阻塞 PhaseB 关闭。
- Meeting / Knowledge 后续的真实业务质量、legacy facade 等价和 data boundary 验收转入 PhaseD / E，不再作为 PhaseB 平台装配边界阻塞项。
- 静态 workflow factory 已降级为兼容 fallback；后续只允许做兼容维护，不再作为平台主扩展路径。

## 3. 架构影响范围

### Plane-5 Domain Pack

这是 PhaseB 的主改动面。

- 正式化 pack manifest schema。
- 冻结 PackAssemblyResult 合同。
- 收口 conflict / missing dependency / degraded / blocked 语义。
- 支持 external pack paths。

### Plane-6 Connector / Tool / Store

这是 PhaseB 的第二主改动面。

- 正式化 ConnectorRegistry。
- 冻结 connector descriptor 输出字段。
- 冻结 connector health / capabilities / config_ref / secret_ref / app_scope 合同。
- 将 stdio command/path allowlist 与 remote network policy 前移为执行前阻断。

### Plane-3 Harness Core

这是承接层，不是本阶段的业务扩展层。

- PackAssemblyResult 必须成为 Core/Gateway 可稳定读取的装配结果合同。
- connector execution 的 blocked / failed 语义必须能稳定进入 Job/Artifact/Governance 链路。

### Plane-2 Protocol App Server

主要影响对外暴露面的稳定性。

- `pack.list/get` 输出要稳定返回装配结果与 blocked reason。
- `connector.list/get/health` 要稳定返回 descriptor 与 health。
- Meeting / Knowledge 的后续标准入口要从硬编码旁路迁移回 pack/registry。
- reference pack 的存在不得继续成为平台层保留静态业务特判的理由。

### 非主改动面

- Plane-1 Client / Gateway 不是本阶段主战场，只承接新的 pack/connector 合同。
- Plane-4 Runtime Adapter 不是本阶段主改动层，只被动承接 connector runtime 与后续治理注入的稳定输入。

## 4. PhaseB 实施切片

### V3.0-PhaseB-B1 Pack manifest schema

开发目的：

- 把 workflow、skill、connector、policy、artifact kind 的声明能力正式化。

具体实现设计：

- pack manifest 必须能稳定声明上述对象，不再依赖隐式约定或业务代码旁带。
- PackRegistry 必须能读取、校验并装配这些声明对象。

主要影响平面：

- Plane-5

完成定义：

- schema tests 通过。
- workflow、skill、connector、policy bundle、artifact kind 都能作为 pack 声明的一部分被 registry 稳定消费。

### V3.0-PhaseB-B2 PackAssemblyResult 合同

开发目的：

- 把 pack 装配结果从“是否成功”的模糊状态，升级为上层可直接消费的结构化合同。

具体实现设计：

- 固定返回 `assembled`、`blocked`、`degraded`、`stub`。
- 固定暴露 `app_id`、`missing_dependencies`、`conflicts`、`blocked_reason`、`disabled_reason`、`next_actions`。
- `pack.list/get` 必须直接返回这些字段，而不是只存在于内部 Python dataclass。

主要影响平面：

- Plane-3
- Plane-5

完成定义：

- `pack.list/get` 输出字段稳定。
- 调用方可直接依据 blocked/degraded 结果解释 pack 当前可用性与下一步动作。

### V3.0-PhaseB-B3 conflict / missing dependency handling

开发目的：

- 把 pack 装配失败从“抛异常或静默覆盖”升级为结构化、可回归、可解释的冲突与缺失依赖结果。

具体实现设计：

- duplicate pack/domain/workflow 注册必须拒绝。
- workflow / artifact kind / schema / connector / external pack 版本不兼容等情况必须转为结构化 `conflicts` 或 `missing_dependencies`。
- 缺失 connector 时不得继续装配执行，应直接返回 blocked。

主要影响平面：

- Plane-5

完成定义：

- 缺失 connector、冲突 schema、重复注册、外部 pack 不兼容等情况可稳定返回 blocked/conflicts。

### V3.0-PhaseB-B4 external pack paths

开发目的：

- 让 pack 可以脱离仓库内置目录独立演化，而不是把所有业务 pack 固定绑死在当前仓库。

具体实现设计：

- 通过 AppProfile `pack_paths` 或等效入口支持 external pack roots。
- 对外部 pack 的加载结果给出 assembled / blocked / degraded 语义，而不是“读到就算成功”。

主要影响平面：

- Plane-3
- Plane-5

完成定义：

- external pack fixture 通过。
- 版本不兼容或装配冲突时返回 blocked，而不是 silent overwrite。

### V3.0-PhaseB-B5 connector descriptor / security

开发目的：

- 把 connector 从“能调起来的工具”升级为“受 registry 管理、带安全边界与健康语义的资源”。

具体实现设计：

- descriptor 至少暴露：
  - `capabilities`
  - `health`
  - `config_ref`
  - `secret_ref`
  - `app_scope`
  - `trust_level`
  - `execution_mode`
  - `allowed_commands`
  - `allowed_paths`
  - `allowed_network_hosts`
  - `network_policy`
- 健康检查与安全阻断分离：health 不等于可执行。
- stdio connector 执行前必须检查 command/path allowlist。
- remote connector 执行前必须检查 network policy / host allowlist。

主要影响平面：

- Plane-5
- Plane-6

完成定义：

- `connector.list/get/health` 稳定输出 descriptor 与 health。
- 未 allowlist 的 command/path/network 被 blocked。
- 合法 connector 仍可通过当前主线回归。

### V3.0-PhaseB-B6 meeting / knowledge assembly

开发目的：

- 让 Meeting / Knowledge 的标准入口回到 pack + registry，而不是继续依赖硬编码路径或业务旁路。

具体实现设计：

- Meeting / Knowledge connector refs 必须通过 pack manifest、AppProfile 与 ConnectorRegistry 决定。
- `connector.health`、assembly blocked reason、connector descriptor 都必须经过标准 registry 路径暴露。

主要影响平面：

- Plane-2
- Plane-5
- Plane-6

完成定义：

- Meeting / Knowledge 的标准装配入口不再以硬编码路径为主入口。
- `connector.health` 和 assembly tests 可直接验证其标准装配链路。

### V3.0-PhaseB-B7 descriptor-driven workflow registration

开发目的：

- 把 reference packs 从“静态平台内置 workflow”升级为“由 pack descriptor 发现和注册的样板”。

具体实现设计：

- workflow registration 应逐步从静态 `meeting / knowledge / video` factory 过渡到 pack-declared entrypoint / descriptor-driven registration。
- 新增 pack 的发现、装配和 blocked/degraded 解释应依赖 AppProfile + Pack manifest + ConnectorRegistry，而不是再修改 Core/Gateway 业务逻辑。

主要影响平面：

- Plane-2
- Plane-3
- Plane-5

完成定义：

- 至少有一组 external/sample pack fixture 证明 pack 可被发现和装配，而无需新增平台业务分支。
- 文档和实现都明确静态 workflow factory 只是过渡实现，不是平台正式扩展方式。

## 5. PhaseB 退出门与收官证据

V3.0-PhaseB 完成时，至少要满足以下条件：

- PackAssemblyResult 可稳定表达 `assembled/blocked/degraded/stub`。
- 缺失 connector、冲突、外部 pack 不兼容等场景有结构化结果，而不是静默覆盖或模糊异常。
- `connector.list/get/health` 能通过 registry 暴露 descriptor 与 health。
- 未 allowlist 的 stdio command/path/network 会被 blocked。
- Meeting / Knowledge 的标准装配入口回到 pack/registry，不再以硬编码路径作为主入口。
- 新增参考 pack 的装配不应再要求修改 Core/Gateway 业务逻辑。

2026-05-08 收官结论：

- 上述 6 项退出门均已有平台回归或显式集成证据。
- `PhaseB` 现定义为已完成；后续相关工作只允许作为 `PhaseC`、`PhaseD` 或 `PhaseE` 的延续项承接。

2026-05-08 平台链路验收证据：

- `.venv/bin/python -m pytest tests/test_pack_registry.py tests/test_gateway_protocol.py tests/test_lead_orchestrator.py tests/test_v3_multi_app_core.py -q -k 'test_default_pack_registry_loads_active_and_stub_packs or test_pack_registry_resolves_pack_by_domain_and_workflow or test_pack_registry_evaluates_default_pack_assembly or test_pack_registry_marks_active_pack_blocked_when_connector_missing or test_pack_registry_marks_active_pack_blocked_when_policy_bundle_missing or test_pack_registry_marks_active_pack_blocked_when_schema_version_incompatible or test_pack_registry_marks_active_pack_blocked_when_connector_capability_missing or test_pack_registry_marks_external_pack_blocked_when_target_version_incompatible or test_gateway_pack_list_and_get_returns_phaseb_pack_contract_fields or test_gateway_pack_list_and_get_support_app_profile_pack_paths or test_gateway_can_register_and_run_external_pack_workflow_from_manifest_entrypoint or test_gateway_connector_registry_lists_meeting_mcp or test_gateway_reference_pack_standard_entry_consistency or test_connector_registry_supports_descriptor_driven_custom_connector or test_gateway_connector_submit_blocks_unallowlisted_payload_path or test_gateway_workflow_list_and_knowledge_route'` -> `15 passed`

2026-05-08 显式真实服务验收证据：

- `.venv/bin/python scripts/check_real_mcp_env.py` 在显式设置 `HARNESS_MEETING_MCP_AUDIO_DIR`、`HARNESS_FUNASR_MCP_EXECUTION=stdio`、`HARNESS_DATA_SERVICE_MCP_EXECUTION=stdio` 后返回 `status=ok`
- `.venv/bin/python scripts/e2e_funasr_mcp_validation.py --audio "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=ok`
- `.venv/bin/python scripts/e2e_data_service_mcp_validation.py` -> `status=ok`
- `.venv/bin/python scripts/e2e_meeting_to_knowledge_mcp_validation.py --audio "/Users/Zhuanz/Desktop/workspace/音频资料/TED演讲对话_My bank called in the middle of my TED Talk  Mike .mp3"` -> `status=ok`

当前外部环境备注：

- `funasr_mcp` 的显式 stdio 验收当前使用 `/Users/Zhuanz/Desktop/workspace/voice_service/.venv/bin/python` 作为 MCP 解释器基线。
- 前检查验证 `mcp + funasr_service.mcp_stdio`；真实 HTTP 服务和音频目录仍属于显式集成验收前置，不进入默认回归。
