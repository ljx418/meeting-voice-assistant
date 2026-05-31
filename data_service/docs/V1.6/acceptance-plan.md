# Data Service V1.6 Acceptance Plan

更新时间：2026-05-16

## Acceptance Standard

每个 V1.6 子阶段必须同时通过功能验收、公开面验收、契约验收、回归验收和文档一致性验收。

## Public Surface Acceptance

每个阶段都必须记录：

- MCP tool count baseline / current / diff。
- CLI top-level and nested commands baseline / current / diff。
- HTTP routes baseline / current / diff。
- target HTTP route allowlist baseline / current / diff。
- new public surface, if any, must match the phase scope。

任何未在阶段计划中声明的 MCP tool、HTTP route 或 CLI command 都是 blocking issue。

V1.6-A 已将上述要求固化为 `public-surface-baseline.json` 和 `test_public_surface_guard.py`。后续 V1.6-B/C/D/E/F 开始前必须先运行 public surface guard。

V1.6-B1 已验证 phase overlay 机制：V1.5 baseline 不变，B1 overlay 精确允许 4 个 workspace target HTTP additions。后续阶段必须继续使用 immutable baseline + accepted overlays 的方式记录公开面。

V1.6-B2 已继续使用 phase overlay 机制：V1.5 baseline 不变，B2 overlay 精确允许 4 个 source target HTTP additions。B2 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 = 11 routes。

V1.6-B3 已继续使用 phase overlay 机制：V1.5 baseline 不变，B3 overlay 精确允许 3 个 build target HTTP additions。B3 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 = 14 routes。

V1.6-C1 已继续使用 phase overlay 机制：V1.5 baseline 不变，C1 overlay 精确允许 1 个 graph neighbors target HTTP addition，并允许 `knowledge graph neighbors` nested CLI addition。C1 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 = 15 routes。

V1.6-C2 已继续使用 phase overlay 机制：V1.5 baseline 不变，C2 overlay 精确允许 1 个 graph community target HTTP addition，并允许 `knowledge graph community` nested CLI addition。C2 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 = 16 routes。

V1.6-C3 已继续使用 phase overlay 机制：V1.5 baseline 不变，C3 overlay 精确允许 1 个 graph query target HTTP addition，并允许 `knowledge graph query` nested CLI addition。C3 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 = 17 routes。

V1.6-C4 已继续使用 phase overlay 机制：V1.5 baseline 不变，C4 overlay 精确允许 1 个 graph session target HTTP addition，并允许 `knowledge graph session` nested CLI addition。C4 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 = 18 routes。

V1.6-D1 不新增 phase overlay。D1 accepted 后 current target HTTP surface 仍为 18 routes，MCP tool count 仍为 40，CLI top-level 与 nested inventory 均与 C4 accepted baseline 一致。

V1.6-D2 已继续使用 phase overlay 机制：V1.5 baseline 不变，D2 overlay 精确允许 5 个 session lifecycle target HTTP additions。D2 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 = 23 routes。D2 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session ingest/query/build target HTTP，不开放 quality target HTTP。

V1.6-D3 不新增 phase overlay。D3 accepted 后 current target HTTP surface 仍为 23 routes，MCP tool count 仍为 40，CLI top-level 与 nested inventory 不变，HTTP diff from D2 accepted surface = none。D3 只做 planning / contract hardening，不开放 session ingest/query/build target HTTP，不开放 quality target HTTP。

V1.6-D4 已继续使用 phase overlay 机制：V1.5 baseline 不变，D4 overlay 精确允许 1 个 session ingest target HTTP addition。D4 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 = 24 routes。D4 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session query/build target HTTP，不开放 quality target HTTP。

V1.6-D5 已继续使用 phase overlay 机制：V1.5 baseline 不变，D5 overlay 精确允许 1 个 session query target HTTP addition。D5 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 = 25 routes。D5 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session build target HTTP，不开放 quality target HTTP。

V1.6-D6 已继续使用 phase overlay 机制：V1.5 baseline 不变，D6 overlay 精确允许 3 个 session build target HTTP additions。D6 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 = 28 routes。D6 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality target HTTP。

V1.6-E1 已继续使用 phase overlay 机制：V1.5 baseline 不变，E1 overlay 精确允许 1 个 quality feedback target HTTP addition。E1 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 + E1 overlay 1 = 29 routes。E1 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction rules/review/plan target HTTP。

V1.6-E2 已继续使用 phase overlay 机制：V1.5 baseline 不变，E2 overlay 精确允许 2 个 quality correction rules target HTTP additions。E2 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 + E1 overlay 1 + E2 overlay 2 = 31 routes。E2 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction review/plan/build target HTTP。

V1.6-E3 已继续使用 phase overlay 机制：V1.5 baseline 不变，E3 overlay 精确允许 1 个 quality correction review target HTTP addition。E3 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 + E1 overlay 1 + E2 overlay 2 + E3 overlay 1 = 32 routes。E3 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction plan/build target HTTP。

V1.6-E4 已继续使用 phase overlay 机制：V1.5 baseline 不变，E4 overlay 精确允许 2 个 quality correction plan target HTTP additions。E4 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 + E1 overlay 1 + E2 overlay 2 + E3 overlay 1 + E4 overlay 2 = 34 routes。E4 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality build target HTTP。

V1.6-E5 已继续使用 phase overlay 机制：V1.5 baseline 不变，E5 overlay 精确允许 1 个 quality correction-rules artifact build target HTTP addition。E5 accepted 后 current target HTTP surface = V1.5 baseline 3 + B1 overlay 4 + B2 overlay 4 + B3 overlay 3 + C1 overlay 1 + C2 overlay 1 + C3 overlay 1 + C4 overlay 1 + D2 overlay 5 + D4 overlay 1 + D5 overlay 1 + D6 overlay 3 + E1 overlay 1 + E2 overlay 2 + E3 overlay 1 + E4 overlay 2 + E5 overlay 1 = 35 routes。E5 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 correction apply target HTTP。

V1.6-F1 不新增 phase overlay。F1 accepted 后 current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI top-level / nested diff = none，HTTP diff from E5 accepted surface = none。F1 只做 console governance evidence baseline、文档同步、drawio 同步和 focused documentation guard；不新增 backend route，不修改 frontend 或 `/knowledge` 行为。

V1.6-F2 不新增 phase overlay。F2 accepted 后 current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI top-level / nested diff = none，HTTP diff from F1/E5 accepted surface = none。F2 只修改 `/knowledge` governance evidence display 和前端静态 build 产物；不新增 backend route、MCP tool、CLI command 或 CLI subcommand，不改变 accepted API behavior，不把 `/knowledge` 改成 end-user knowledge consumption app。

V1.6 Closure Acceptance 不新增 phase overlay。Closure accepted 后 current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI top-level / nested diff = none，HTTP diff from F2/E5 accepted surface = none。Closure 只做最终公开面冻结审计、focused closure test、文档同步和最终报告；不修改功能代码，不新增 backend route、MCP tool、CLI command 或 CLI subcommand，不把 `/knowledge` 改成 end-user knowledge consumption app。

## Contract Acceptance

检查项：

- MCP / CLI / HTTP / target HTTP payload consistency。
- envelope / error contract consistency。
- `artifact_ref` consistency。
- operation lifecycle consistency。
- source lifecycle no-side-effect checks：source import/list/describe/remove 不触发 build、GraphRAG、session graph 或 quality write。
- build lifecycle operation checks：build start/status/cancel 使用真实 `operation_id`，默认 response 不暴露内部 path/layout；build pipeline 可运行既有内部阶段，但不开放 graph/session/quality public contract。
- graph neighbors checks：target HTTP / CLI 使用 stable projection；`node_id` / `entity_id` one-of；`depth` / `max_nodes` bounded；read-only，不触发 build/index/session/quality，不创建 operation，不修改 source registry。
- graph community checks：target HTTP / CLI 使用 stable projection；list/detail 语义固定；`limit` bounded；`include_members` stable projection；read-only，不触发 build/index/materialization/session/quality，不创建 operation，不修改 source registry，不写入 graph snapshot。
- graph query checks：target HTTP / CLI 使用 stable projection；`q` required；`top_k` bounded；`include_nodes` / `include_edges` / `include_communities` policy fixed；read-only，不触发 build/index/materialization/session/quality，不创建 operation，不修改 source registry，不写入 graph snapshot。
- graph session checks：target HTTP / CLI 使用 stable projection；list/detail 只检查已有 session graph artifacts；`limit`、`node_limit`、`edge_limit` bounded；`include_nodes` / `include_edges` capped；read-only，不触发 build/index/materialization/quality，不创建 operation，不修改 source registry，不写入 graph snapshot，不开放 session lifecycle public contract。
- Session GraphRAG D1 checks：surface matrix 完整；C4 `/graph/session` 不被描述为 session lifecycle；unknown session / missing artifact / cross-workspace isolation 使用现有 normalized envelope；artifact_ref 是 non-path stable ref；no `/sessions*` target HTTP；no quality target HTTP。
- Session lifecycle D2 checks：create/list/get/close/delete target HTTP 使用 stable `session_id` 与 `session://...` artifact_ref；list 默认不包含 disposed session；include_deleted 可显式返回 disposed session；close/delete repeated behavior 固定；cross-workspace session 不泄露；默认 response 与 metadata 不暴露 internal path/layout；no session ingest/query/build target HTTP；no quality target HTTP。
- Session ingest/query/build D3 checks：contract matrix 完整；D4/D5/D6 拆分明确；D3 route count remains 23；D2 lifecycle 与 C4 graph session 边界清晰。
- Session ingest D4 checks：only `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` added；target HTTP route count = 24；HTTP diff is exactly D4 overlay；MCP/CLI diff = none；no session query/build target HTTP；no quality target HTTP；artifact_ref non-path；metadata sanitized；no build/index/materialization/query/quality side effects。
- Session query D5 checks：only `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` added；target HTTP route count = 25；HTTP diff is exactly D5 overlay；MCP/CLI diff = none；no session build target HTTP；no quality target HTTP；query is session-scoped read-only；no build/index/materialization/quality side effects；no raw GraphRAG payload、raw prompts、raw model messages or embedding vectors。
- Session build D6 checks：only session build start/status/cancel routes added；target HTTP route count = 28；HTTP diff is exactly D6 overlay；MCP/CLI diff = none；no quality target HTTP；operation_id is real lifecycle id；cancel semantics fixed；session build is session-scoped；no workspace-level build or quality write side effects；operation artifacts/logs/diagnostics do not expose internal path/layout。
- Quality feedback E1 checks：only `POST /api/workspaces/{workspace_id}/quality/feedback` added；target HTTP route count = 29；HTTP diff is exactly E1 overlay；MCP/CLI diff = none；no quality correction rules/review/plan target HTTP；feedback projection uses non-path `quality-feedback://...` artifact_ref；metadata is sanitized；compatibility HTTP retained。
- Quality correction rules E2 checks：only `GET /api/workspaces/{workspace_id}/quality/correction-rules` and `POST /api/workspaces/{workspace_id}/quality/correction-rules` added；target HTTP route count = 31；HTTP diff is exactly E2 overlay；MCP/CLI diff = none；no quality correction review/plan/build target HTTP；rule_id is the primary stable identifier；artifact_ref is optional and non-path if present；rule writes do not review、approve、activate、apply、generate plan or trigger read-time governance。
- Quality correction review E3 checks：only `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review` added；target HTTP route count = 32；HTTP diff is exactly E3 overlay；MCP/CLI diff = none；no quality correction plan/build target HTTP；review-only helper does not generate/update correction plan；approved does not mean active/applied；review does not activate read-time governance or execute correction。
- Quality correction plan E4 checks：only `GET /api/workspaces/{workspace_id}/quality/correction-plan` and `POST /api/workspaces/{workspace_id}/quality/correction-plan` added；target HTTP route count = 34；HTTP diff is exactly E4 overlay；MCP/CLI diff = none；no quality build target HTTP；GET does not generate plan；POST uses plan-only/generate-only semantics；approved rules snapshot is bound；repeated POST semantics fixed；no correction execution、apply、read-time governance activation or build/session operation。
- Quality correction rules build E5 checks：only `POST /api/workspaces/{workspace_id}/quality/correction-rules/build` added；target HTTP route count = 35；HTTP diff is exactly E5 overlay；MCP/CLI diff = none；build is correction-rules artifact build only, not quality/workspace/session/correction-plan build or correction apply；request body is `{}` only；existing review statuses are preserved；correction plan is not generated or updated；stale correction plan is reported through warnings / next_actions only。
- Console governance evidence F1 checks：no public surface addition；target HTTP route count remains 35；MCP tool count remains 40；CLI top-level / nested diff = none；no new backend route；no frontend behavior change；`/knowledge` remains service governance console；A / D1 / D3 are documented as +0 guard/planning phases, not route overlays。
- Console governance polish F2 checks：only `/knowledge` governance evidence display changed；frontend build passes；target HTTP route count remains 35；MCP tool count remains 40；CLI top-level / nested diff = none；no new backend route；accepted graph CLI nested additions remain graph neighbors/community/query/session；`/knowledge` remains service governance console；console does not present raw internal path/layout as stable contract。
- Closure Acceptance checks：no functional code changes；changed files limited to docs/tests/reports/drawio；target HTTP route count remains 35；MCP tool count remains 40；CLI top-level / nested diff = none relative to accepted current baseline；E5 focused test file exists and passes；C graph CLI focused tests pass；no correction apply / execution route；drawio XML validates；V1.7 remains planned only。
- stable external IDs only。
- debug/console-only internal path fields clearly marked non-contract。

## Regression Acceptance

每个实现阶段至少需要：

- focused tests for the changed capability group。
- API regression where HTTP is touched。
- MCP regression where MCP registry, handler or shared contract is touched。
- CLI parser regression where CLI is touched。
- combined data_service/API/MCP regression before phase acceptance。
- frontend `npm run build` and screenshot acceptance when `/knowledge` changes。
- drawio XML validation when diagrams change。

## Documentation Acceptance

每个阶段完成后必须同步：

- `README.md`
- `development-plan.md`
- `acceptance-plan.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- related contract / convergence plan

文档不得将 planned 能力描述为 implemented。文档必须持续使用 MCP-first local knowledge governance microservice 定位。
MCP graph/session tools already exist in the V1.5 baseline；V1.6 文档不得把它们重新描述为 V1.6 新增 MCP tools。

## Final V1.6 Acceptance

V1.6 最终验收必须确认：

- V1.5 compatibility routes retained。
- V1.6 newly opened surfaces match accepted phase reports。
- no hidden upper-layer application dependency。
- `/knowledge` remains service governance console。
- V1.6 docs and diagrams match actual implementation。
