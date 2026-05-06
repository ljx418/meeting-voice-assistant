# harnessOS V3.0 阶段验收标准与测试用例集

文档状态：ACTIVE V3.0 ACCEPTANCE。V2 阶段验收文档已归档到 `docs/history/v2-phase-docs/acceptance-test-cases_v2.md`。

## 1. 验收总原则

- 当前最高优先级是把 harnessOS Core 做稳，不新增业务旁路。
- 新业务不得写入 Core 或 Gateway，必须通过 AppProfile、Pack、Connector、RuntimeAdapter 接入。
- 每阶段必须保持默认 stub/contract 回归稳定，meeting 真实音频 E2E 作为显式外部服务验收单独维护。
- 多 app 查询默认按 `app_id/project_id/workspace_id` 过滤，禁止串数据。

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
| V3.0-PhaseB-AC01 | Pack manifest schema | pack registry tests | workflow、skill、connector、policy bundle、artifact kind 可声明 |
| V3.0-PhaseB-AC02 | PackAssemblyResult | `pack.list/get` | 返回 assembled/blocked/degraded/stub、missing_dependencies、conflicts、next_actions |
| V3.0-PhaseB-AC03 | External pack paths | 环境变量或 AppProfile pack_paths | 外部 pack 可加载，版本不兼容时 blocked |
| V3.0-PhaseB-AC04 | Connector Registry | `connector.list/get/health` | connector 从 registry 读取 capabilities、health、config_ref、secret_ref、app_scope |
| V3.0-PhaseB-AC05 | Connector security | connector security fixture | 未 allowlist 的 stdio command/path/network 被 blocked |

## 4. V3.0-PhaseC Job / Artifact / Governance Hardening

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseC-AC01 | Job worker MVP | job service tests | queued/running/succeeded/failed/cancelled、progress、failure_context、artifact_ids 可查询 |
| V3.0-PhaseC-AC02 | External job ref | connector execution tests | external_job_ref 与 parent_job_id 持久化 |
| V3.0-PhaseC-AC03 | External artifact | `artifact.register_external` | external_asset_uri、preview_uri、thumbnail_uri、metadata 可查询 |
| V3.0-PhaseC-AC04 | Large file policy | `artifact.read` | 在现有视频/大文件/external-only 阻断基础上，音频/图片/binary/大文件拒绝全文读取并返回统一错误码 |
| V3.0-PhaseC-AC05 | Artifact lineage | `artifact.lineage` | parent_ids 可形成 brief -> script -> render_output 等链路 fixture |
| V3.0-PhaseC-AC06 | Governance injection | runtime adapter tests | policy、approval、trace、secret hygiene、scope context 默认注入 |

## 5. V3.0-PhaseD Meeting Pack E2E Migration

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseD-AC01 | Meeting pack assembly | `pack.get(app_id=meeting)` | meeting workflow、connector、skills、artifact kinds、policy 装配成功 |
| V3.0-PhaseD-AC02 | Meeting MCP connector | connector registry | Meeting MCP / FunASR MCP 通过 ConnectorRegistry 接入 |
| V3.0-PhaseD-AC03 | Real audio E2E | 显式 meeting real audio acceptance | 在 Meeting MCP/FunASR 服务已启动前提下生成 transcript、analysis、result、minutes artifacts |
| V3.0-PhaseD-AC04 | Lineage completeness | artifact/job/trace queries | job、trace、turn、artifact 关联完整 |
| V3.0-PhaseD-AC05 | Legacy facade equivalence | legacy meeting RPC test | legacy RPC 与 pack workflow 产物等价 |

## 6. V3.0-PhaseE Knowledge Pack E2E Migration

| ID | 用例 | 命令/入口 | 预期 |
| --- | --- | --- | --- |
| V3.0-PhaseE-AC01 | Knowledge pack assembly | `pack.get(app_id=knowledge)` | ingest/search/summarize/citation workflow 装配成功 |
| V3.0-PhaseE-AC02 | Knowledge MCP connector | connector registry | Knowledge MCP 通过 ConnectorRegistry 接入，可替换 connector 不改 Core |
| V3.0-PhaseE-AC03 | Knowledge data boundary | data_service_mcp tests | 只调用 lifecycle/v2 tools，不直接读写 data_service 内部目录 |
| V3.0-PhaseE-AC04 | Knowledge artifacts | workflow E2E | 输出 note、brief、citation_bundle artifacts |
| V3.0-PhaseE-AC05 | Trace completeness | trace/artifact/job queries | trace、artifact、job、turn 关联完整 |

## 7. Deferred

以下不进入 V3.0-PhaseA 到 V3.0-PhaseE 验收：

- Low-Code Workflow Runtime
- Core Memory System
- Feedback Optimization Loop
- Workflow Library
- V3.1 Interview Pack
- V3.2 Investment Pack
- V3.3 Video Studio external project integration
