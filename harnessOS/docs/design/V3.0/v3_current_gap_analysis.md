# harnessOS V3.0 Current Gap Analysis

文档状态：V3.0 FINAL GAP AUDIT / V3.x+ BACKLOG。本文记录当前代码事实、V3.0 收官结果和后续真实差距，不替代 `v3_development_plan_multi_app_core.md`。

已完成阶段冻结规则：

- V3.0-PhaseA 已在 2026-05-06 完成重新验收并进入冻结基线。
- V3.0-PhaseB 和 V3.0-PhaseC 已在 2026-05-08 完成收官验收。
- V3.0-PhaseD 和 V3.0-PhaseE 已完成 reference pack 验证；后续 gap 分析只记录 V3.x+ 遗留问题，不再把新的业务 pack 需求回写成 V3.0 未完成项。

## 1. 已具备能力

- Core 已有 Session、Thread、Turn、Item、Job、Artifact、Trace、Approval、Retry、Connector records。
- SQLite Store 已是 Core 查询和持久化基础，并已有 scope columns、indexes 和兼容补列逻辑。
- Pack Registry 已支持 manifest、workflow template、agents、connector refs、policy bundle、artifact schemas。
- PackAssemblyResult 已补齐 `app_id`、`conflicts`、`degraded` 和 `blocked_reason` 合同，`pack.list/get` 现在可稳定返回这些字段。
- PackRegistry 已经开始显式拒绝 duplicate pack name / domain / workflow_id，external pack roots 不再 silent overwrite。
- AppProfile `pack_paths` 已进入默认 pack registry 装配路径，external pack 现在既可通过环境变量，也可通过 app profile 声明加载。
- ConnectorExecutionRuntime 已支持 gated MCP stdio execution。
- Meeting Pack 和 Knowledge Pack 已完成 reference pack 验证。
- V3.0-PhaseA 基础 scope 字段已经开始进入 records、Store schema 和 Gateway RPC。
- Artifact 已开始支持 external registration、metadata-only read，以及视频/大文件/external-only inline read 阻断。
- PhaseA 主链路中的 resolver、Gateway session 查询隔离、命名 migration 语义和 legacy backfill fixture 已落地。
- turn 级 scope override、memory scope、`turn.continue/retry/interrupt` 的 Gateway scope 防护已经补进主链路。
- ConnectorExecutionRuntime 现在已具备 `defer=True` 后台执行路径，并会把 MCP `isError=true` 正确映射为 failed job。
- Artifact / Trace / Approval 的 legacy RPC 默认 scope 收口已经补齐，approval / trace 写入记录也会保留 scope 三元组。
- PhaseA 的默认回归、显式真实音频验收与环境前检查已形成冻结基线，相关测试与文档只允许做兼容性维护。
- PhaseB 已有独立实施文件 `v3_phaseb_pack_connector_registry.md`，后续 PackAssemblyResult 与 ConnectorRegistry 合同变更应以该专项文件和 final closeout plan 联动维护。
- 2026-05-08 已完成一轮 PhaseB 收官验收：平台链路回归 `15 passed`，显式真实服务验收 `check_real_mcp_env / funasr_mcp / data_service_mcp / meeting_to_knowledge_mcp` 均返回 `status=ok`。
- 2026-05-08 已完成 PhaseC 收官验收：默认全量回归 `.venv/bin/python -m pytest -q` -> `182 passed, 3 skipped, 6 warnings`；PhaseC / Meeting 相关切片 -> `14 passed, 1 skipped`。
- `connector.submit` 的 approval-required 路径已冻结为正式 job 路径：首次 submit 创建并绑定 queued job，批准后 retry 复用同一个 job；mismatched approval 不会先创建脏 job。
- `connector.submit` 可从 `session_id` 继承 scope，connector poll/cancel/collect 与 job get/events/cancel 已纳入 scope 隔离。
- Meeting workflow 真实音频路径已通过 `voice_service` 的 `funasr_mcp.funasr_recognize_file` 完成转写，并通过 real-audio Meeting lineage 验收。

## 2. 主要差距

- Multi-app scope 默认安全主链路已闭合；底层 Store 不传 scope 时仍可全量查询，该行为保留为受控兼容/管理 bypass。
- AppProfile / AppRegistry、profile 示例、resolver 默认规则和 scope 传播已完成 V3.0 冻结基线；后续新增 app 只允许在该合同上扩展。
- Gateway initialize 目前仍返回 `v1alpha`；缺少 `v1alpha3` protocol version、method schema、event schema、error code registry。
- 缺少 Python / TypeScript SDK 与 external app contract。
- 缺少 auth / local capability token 最小策略。
- ConnectorRegistry 仍有默认 connector 描述数据留在 Python 中，但这已不再阻塞 PhaseB；后续继续在 PhaseC / D / E 中向 connector manifest/config 驱动推进。
- ConnectorRegistry / ConnectorExecutionRuntime 已开始执行 security descriptor：stdio connector 的 command/path allowlist 与 remote connector 的 network policy 会在执行前阻断。
- connector 可用性已开始严格以 ConnectorRegistry 为准，AppProfile refs 不再被直接视为 availability；`local.knowledge` 已补为内置 contract stub，减少 Knowledge pack 声明与运行时事实分叉。
- Pack Assembly 已完成正式结果合同与 sample-pack neutrality 收官；剩余 gap 转为 descriptor 外置化、跨域 reference pack 真实业务质量和 cross-app 解释文本持续收紧。
- Gateway / RuntimePool 的 pack assembly 输入已开始从 `app_registry + connector_registry` 推导；Meeting / Knowledge 的 assembly 不再只依赖固定 connector 常量集合。
- pack assembly 现在会同时校验 registry 可用性与 AppProfile enabled connectors；未显式启用的 connector 会返回 `app_profile_connector:*` blocked dependency。
- external pack `metadata.target_version` 已进入 assembly policy：缺失 target_version 目前记为 degraded，不兼容 target_version 记为 blocked。
- Meeting 的标准入口、legacy facade 等价和 strict/resilience real-audio E2E 已完成 PhaseD 收官；Knowledge 的 data boundary、connector replacement 和 migrated data_service MCP E2E 已完成 PhaseE 验收。
- workflow registration 已开始优先走 pack-declared entrypoint；静态 `meeting / knowledge / video` factory 仅保留兼容痕迹，后续只允许兼容维护。
- Meeting legacy RPC 已降级为 compatibility facade，并具备 deprecation warning trace event 和 pack workflow equivalence tests；后续只保留 sunset plan 维护。
- PhaseD 后续实施已拆为 D0-D7：Documentation Sync、Meeting Pack Assembly、Meeting Connector Contracts、Meeting Workflow Standard Path、Legacy Facade Compatibility、Equivalence / Lineage Verification、Real Audio Strict + Resilience E2E、Architecture / Acceptance Docs Update。
- PhaseD strict mode 不允许 silent fallback 掩盖 connector 缺失；resilience mode 允许 `meeting_voice_mcp` 不可用时 fallback，但 trace 和 artifact metadata 必须记录 fallback reason，且不能声明 Meeting 业务质量完成。
- Knowledge Pack 已完成 connector-backed 端到端真实服务验收；data boundary、artifact/citation 完整性和 connector replacement 已进入回归维护。
- Artifact 保护已冻结 PhaseC 合同；当前代码阻断视频、音频、图片、binary、external-only 和超过阈值文件的 inline read，并统一返回 `ARTIFACT_READ_BLOCKED`、blocked reason、metadata-only artifact 与 `artifact.read_metadata` 建议。
- Job 失败合同已向顶层 `failure_context` 收口；connector execution、workflow runtime 与后台 worker 均保留 metadata 兼容镜像。
- 仓库自有默认主线回归在 2026-05-09 的最新本地验证结果为 `.venv/bin/python -m pytest tests -q` -> `206 passed, 3 skipped, 6 warnings`。
- 显式真实服务集成线在 2026-05-08 的本地验证结果为：
  - `scripts/check_real_mcp_env.py` -> `status=ok`
  - `scripts/e2e_funasr_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_data_service_mcp_validation.py` -> `status=ok`
  - `scripts/e2e_meeting_to_knowledge_mcp_validation.py` -> `status=ok`
- `turn.start` 会议路径在失败时不再返回空 `final_text` 伪成功；`meeting.process_recording` 现在通过 runtime-backed `meeting.workflow` 路径执行，并共享 job/trace/turn/artifact 绑定。
- 纯文本会议分析不再依赖 `meeting_voice_mcp` 健康状态；真实音频链路现在依赖 `voice_service` FunASR HTTP + MCP stdio。Meeting MCP 分析服务不可用或超时时，resilience mode 会使用本地 fallback 生成 lineage artifacts，strict mode 会失败。
- FunASR MCP 显式验收现在以 `voice_service/.venv` 为默认解释器基线；前检查验证 `mcp + funasr_service.mcp_stdio`，不再要求旧的 `aiohttp` 依赖。

## 3. 阻塞项

- V3.0 当前无未关闭阻塞项；以下内容均为冻结合同或 V3.x+ 后续维护边界。
- Pack manifest schema、PackAssemblyResult 合同和 sample-pack neutrality 已完成 PhaseB 收官，不再列为阻塞项。
- ConnectorRegistry 的 definition-driven registration 已满足 PhaseB；built-in descriptor 数据继续外置化，但不阻塞进入 PhaseC。
- Artifact large file policy 已完成 PhaseC 冻结，后续 Video Studio 或媒体类 pack 不应通过 `artifact.read` 全量读取大媒体文件。
- RuntimeAdapter governance injection 已完成 PhaseC 主路径冻结；后续新增正式执行入口必须追溯到 adapter，不能新增治理 bypass。

## 4. 当前实施原则

- Core 只提供协议、状态、治理、作业、产物、运行时适配边界。
- 业务能力只能通过 Pack / Connector / RuntimeAdapter 接入。
- Meeting / Knowledge 是 reference packs / validation samples，不是 Core 或 Gateway 的内置业务特权。
- 旧接口保留兼容，但不能作为新业务扩展模板。
- 代码主回归应以 stub / contract mode 为默认基线；真实 MCP / 真实音频验收属于显式集成验证。
- 真实音频 E2E 仍需保持不回归；当前执行前提是相邻 `voice_service` FunASR HTTP 服务可用，且 FunASR MCP 默认解释器优先使用 `voice_service/.venv/bin/python`。

## 5. V3.x+ 后续验收边界

- Namespace isolation：meeting 与 knowledge 同名 session/job/artifact 不互相可见，该项已进入默认回归，后续继续防回归。
- Protocol compatibility：JSON-RPC `result` 与 `error` 不同时存在，错误码来自 registry；协议版本冻结转入 V3.x+。
- Connector security：untrusted stdio connector 未在 allowlist 内时 blocked；remote connector 的 network policy 也要保持显式可解释，后续继续防回归。
- Artifact read：视频、音频、图片、binary、external-only 和超过阈值文件返回 metadata-only error，并使用统一错误码；该项已进入 PhaseC 冻结基线，后续只做回归维护。
- Legacy meeting RPC：legacy facade 与 pack workflow 产出等价 artifacts/job/trace/lineage，并输出 deprecation warning。
- Meeting strict/resilience E2E：`funasr_mcp` 负责 audio.transcribe，`meeting_voice_mcp` 负责 meeting.analyze/minutes.generate；真实音频 strict/resilience E2E 已通过，connector 缺失、stdio 路径不可用、tool 不存在时返回 explainable blocked/degraded。
- Knowledge MCP E2E：迁移后的 `/Users/Zhuanz/Desktop/workspace/data_service/backend` stdio MCP 已通过 PhaseE 验收，后续作为显式集成回归维护。
- Knowledge boundary：PhaseE 内容不得作为 PhaseD 完成条件；PhaseD 只同步 Knowledge 边界，不实现 Knowledge E2E。
