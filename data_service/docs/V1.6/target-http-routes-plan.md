# V1.6 Target HTTP Routes Plan

更新时间：2026-05-16

## Baseline

V1.5 target HTTP currently exposes exactly 3 routes:

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

These routes are the V1.6 starting point. No other target HTTP route should be treated as open until a V1.6 phase implements and accepts it.

V1.6-A Public Surface Guard 已完成，自动化 allowlist guard 会阻断任何未声明的 `/api/workspaces/*` route。V1.6-A 未新增 target HTTP route。

V1.6-B1 Workspace Target HTTP 已完成。V1.5 baseline 不变；B1 通过 phase overlay 新增 4 个 workspace routes。

V1.6-B2 Source Target HTTP 已完成。V1.5 baseline 不变；B2 通过 phase overlay 新增 4 个 source routes。V1.5 source trace route 保持 baseline route，不计为 B2 新增。

V1.6-B3 Build Target HTTP 已完成。V1.5 baseline 不变；B3 通过 phase overlay 新增 3 个 build routes。Build target HTTP 使用既有 operation lifecycle，不开放 graph/session/quality target HTTP public contract。

V1.6-C1 Graph Neighbors Target HTTP / CLI Minimal Surface 已完成。V1.5 baseline 不变；C1 通过 phase overlay 新增 1 个 graph neighbors target HTTP route，并新增 `knowledge graph neighbors` nested CLI command。C1 不新增 MCP tool，不开放 graph community/query/session、session target HTTP 或 quality target HTTP。

V1.6-C2 Graph Community Target HTTP / CLI Minimal Surface 已完成。V1.5 baseline 不变；C2 通过 phase overlay 新增 1 个 graph community target HTTP route，并新增 `knowledge graph community` nested CLI command。C2 不新增 MCP tool；该阶段未开放后续 graph query 或 graph session。

V1.6-C3 Graph Query Target HTTP / CLI Minimal Surface 已完成。V1.5 baseline 不变；C3 通过 phase overlay 新增 1 个 graph query target HTTP route，并新增 `knowledge graph query` nested CLI command。C3 不新增 MCP tool，不开放 graph session、session target HTTP 或 quality target HTTP。

V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface 已完成。V1.5 baseline 不变；C4 通过 phase overlay 新增 1 个 graph-scoped session graph artifact inspection target HTTP route，并新增 `knowledge graph session` nested CLI command。C4 不新增 MCP tool，不开放 session lifecycle target HTTP、完整 Session GraphRAG public contract 或 quality target HTTP。

V1.6-D1 Session GraphRAG Public Contract Planning / Contract Hardening 已完成。D1 不新增 target HTTP route，不新增 phase overlay；current target HTTP surface 仍为 18 routes。

V1.6-D2 Session Lifecycle Target HTTP Minimal Surface 已完成。V1.5 baseline 不变；D2 通过 phase overlay 新增 5 个 session lifecycle target HTTP routes。D2 只开放 create/list/get/close/delete，不开放 session ingest/query/build，不开放 quality target HTTP。Current target HTTP surface = 23 routes。

V1.6-D3 Session Ingest / Query / Build Contract Planning 已完成。D3 不新增 target HTTP route，不新增 phase overlay；D3 accepted 时 current target HTTP surface 仍为 23 routes。D3 只做 planning；D4 后续已单独开放 session ingest，D5 后续已单独开放 session query，D6 后续已单独开放 session build。Quality target HTTP 仍为 planned / not opened。

V1.6-D4 Session Ingest Target HTTP Minimal Surface 已完成。D4 通过 phase overlay 新增 1 个 session ingest target HTTP route；D4 accepted 时 current target HTTP surface = 24 routes。D5 后续已单独开放 session query；D6 后续已单独开放 session build；quality target HTTP 仍为 planned / not opened。

V1.6-D5 Session Query Target HTTP Minimal Surface 已完成。D5 通过 phase overlay 新增 1 个 session query target HTTP route；D5 accepted 时 current target HTTP surface = 25 routes。D6 后续已单独开放 session build；quality target HTTP remains planned / not opened。

V1.6-D6 Session Build Target HTTP Minimal Surface 已完成。D6 通过 phase overlay 新增 3 个 session build start/status/cancel target HTTP routes；current target HTTP surface = 28 routes。D6 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality target HTTP。

V1.6-E1 Quality Feedback Target HTTP Minimal Surface 已完成。E1 通过 phase overlay 新增 1 个 quality feedback target HTTP route；current target HTTP surface = 29 routes。E1 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction rules/review/plan target HTTP。

V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface 已完成。E2 通过 phase overlay 新增 2 个 quality correction rules target HTTP routes；current target HTTP surface = 31 routes。E2 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction review/plan/build target HTTP。

V1.6-E3 Quality Correction Review Target HTTP Minimal Surface 已完成。E3 通过 phase overlay 新增 1 个 quality correction review target HTTP route；current target HTTP surface = 32 routes。E3 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction plan/build target HTTP。

V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface 已完成。E4 通过 phase overlay 新增 2 个 quality correction plan target HTTP routes；current target HTTP surface = 34 routes。E4 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality build target HTTP。

V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface 已完成。E5 通过 phase overlay 新增 1 个 correction-rules artifact build target HTTP route；current target HTTP surface = 35 routes。E5 不新增 MCP tool、CLI command 或 CLI subcommand；该 build 不是 quality build、workspace build、session build、correction plan build 或 correction apply。

Current accepted target HTTP route count = 35. This is V1.5 baseline 3 + B1 4 + B2 4 + B3 3 + C1 1 + C2 1 + C3 1 + C4 1 + D2 5 + D4 1 + D5 1 + D6 3 + E1 1 + E2 2 + E3 1 + E4 2 + E5 1. D1 and D3 are planning / hardening phases with zero route additions. Correction apply target HTTP remains planned / not opened.

V1.6-F1 Console Governance Evidence Baseline Sync 已完成。F1 不新增 target HTTP route，不新增 phase overlay，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不修改 frontend 或 `/knowledge` 行为。F1 accepted 后 current target HTTP route count 仍为 35，MCP tool count 仍为 40。

V1.6-F2 Console Governance Polish 已完成。F2 不新增 target HTTP route，不新增 phase overlay，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不新增 backend route。F2 只更新 `/knowledge` governance evidence display 和前端静态 build 产物。F2 accepted 后 current target HTTP route count 仍为 35，MCP tool count 仍为 40。

## Accepted Phase Overlays

### V1.6-B1 Workspace Target HTTP

Allowed additions：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

Current accepted target HTTP surface after B1：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- total：7 routes

B1 does not open source/build/graph/session/quality target HTTP routes.

### V1.6-B2 Source Target HTTP

Allowed additions：

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

Current accepted target HTTP surface after B2：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- total：11 routes

B2 does not open build/graph/session/quality target HTTP routes. Source import does not trigger build, GraphRAG, session graph or quality write.

### V1.6-B3 Build Target HTTP

Allowed additions：

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

Current accepted target HTTP surface after B3：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- total：14 routes

B3 does not open graph/session/quality target HTTP routes. Build may run existing internal pipeline stages, but no graph/session/quality public contract is opened.

### V1.6-C1 Graph Neighbors Target HTTP

Allowed additions：

- `GET /api/workspaces/{workspace_id}/graph/neighbors`

Current accepted target HTTP surface after C1：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- total：15 routes

C1 does not open graph community/query/session, session target HTTP or quality target HTTP routes. Graph neighbors is read-only and does not trigger build, GraphRAG index, session graph, quality write, operation creation or source registry mutation.

### V1.6-C2 Graph Community Target HTTP

Allowed additions：

- `GET /api/workspaces/{workspace_id}/graph/community`

Current accepted target HTTP surface after C2：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- total：16 routes

C2 did not open later graph query or graph session routes. Graph community is read-only and does not trigger build, GraphRAG index/materialization, session graph, quality write, operation creation, source registry mutation or graph snapshot writes.

### V1.6-C3 Graph Query Target HTTP

Allowed additions：

- `GET /api/workspaces/{workspace_id}/graph/query`

Current accepted target HTTP surface after C3：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- total：17 routes

C3 does not open graph session, session target HTTP or quality target HTTP routes. Graph query is read-only and does not trigger build, GraphRAG index/materialization, session graph, quality write, operation creation, source registry mutation or graph snapshot writes.

### V1.6-C4 Graph Session Target HTTP

Allowed additions：

- `GET /api/workspaces/{workspace_id}/graph/session`

Current accepted target HTTP surface after C4：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- total：18 routes

C4 opens only graph-scoped session graph artifact inspection. It does not open session lifecycle target HTTP, quality target HTTP or full Session GraphRAG public contract. Graph session inspection is read-only and does not trigger build, GraphRAG index/materialization, quality write, operation creation, source registry mutation, graph snapshot writes or session lifecycle state changes.

### V1.6-D2 Session Lifecycle Target HTTP

Allowed additions：

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

Current accepted target HTTP surface after D2：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- total：23 routes

D2 opens only session lifecycle create/list/get/close/delete. It does not open session ingest/query/build target HTTP, quality target HTTP, new MCP tools, CLI commands or CLI subcommands. C4 `/graph/session` remains graph-scoped read-only inspection and is not redefined as session lifecycle.

### V1.6-D3 Session Ingest / Query / Build Contract Planning

D3 opens no route.

Current accepted target HTTP surface after D3 remains：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- total：23 routes

At D4 acceptance time, session query/build target HTTP routes remained planned / not opened. Later D5 and D6 opened their own minimal surfaces separately:

- D4 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`
- D5 accepted: `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`
- D6 accepted: session build start/status/cancel routes

D3 does not open quality target HTTP. D5 and D6 do not open quality target HTTP.

### V1.6-D4 Session Ingest Target HTTP Minimal Surface

D4 opens exactly one route:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

Current accepted target HTTP surface after D4：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- total：24 routes

D4 does not open session query/build target HTTP and does not open quality target HTTP. Session ingest is session-scoped write only; it is not workspace source import, session query, session build, GraphRAG materialization or quality write.

### V1.6-D5 Session Query Target HTTP Minimal Surface

D5 opens exactly one route:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

Current accepted target HTTP surface after D5：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- total：25 routes

D5 does not open session build target HTTP and does not open quality target HTTP. Session query is session-scoped and read-only; it must not trigger build, GraphRAG index, materialization, quality write, source registry mutation, or session ingest storage mutation. D5 response projection must not expose raw GraphRAG rows, raw prompts, raw model messages, embedding vectors, provider raw responses or internal path/layout.

### V1.6-D6 Session Build Target HTTP Minimal Surface

D6 opens exactly three routes:

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

Current accepted target HTTP surface after D6：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- total：28 routes

D6 does not open quality target HTTP and does not add MCP/CLI public surface. Session build is session-scoped, uses real lifecycle `operation_id`, and must not trigger workspace-level build or quality write. Operation artifacts, diagnostics, logs and details are projected to stable refs and do not expose internal path/layout.

### V1.6-E1 Quality Feedback Target HTTP Minimal Surface

E1 opens exactly one route:

- `POST /api/workspaces/{workspace_id}/quality/feedback`

Current accepted target HTTP surface after E1：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- plus E1 overlay 1 route
- total：29 routes

E1 does not open quality feedback list, correction rules, correction review, correction plan, MCP tools, CLI commands or CLI subcommands. Quality feedback is a non-destructive governance signal write with stable projection and no default internal path/layout exposure.

### V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface

E2 opens exactly two routes:

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

Current accepted target HTTP surface after E2：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- plus E1 overlay 1 route
- plus E2 overlay 2 routes
- total：31 routes

E2 does not open correction review, correction plan, quality build, MCP tools, CLI commands or CLI subcommands. Correction rules writes remain draft/proposal storage only and do not review, approve, activate, apply, generate plans, trigger build, or activate read-time governance.

### V1.6-E3 Quality Correction Review Target HTTP Minimal Surface

E3 opens exactly one route:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

Current accepted target HTTP surface after E3：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- plus E1 overlay 1 route
- plus E2 overlay 2 routes
- plus E3 overlay 1 route
- total：32 routes

E3 does not open correction plan, quality build, MCP tools, CLI commands or CLI subcommands. Correction review only updates review status; `approved` does not mean active/applied, no correction plan is generated or updated, no read-time governance is activated, and no correction is executed.

### V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface

E4 opens exactly two routes:

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

Current accepted target HTTP surface after E4：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- plus E1 overlay 1 route
- plus E2 overlay 2 routes
- plus E3 overlay 1 route
- plus E4 overlay 2 routes
- total：34 routes

E4 does not open quality build, MCP tools, CLI commands or CLI subcommands. Correction plan target HTTP only reads or generates a correction plan artifact; it does not execute corrections, apply plans, activate read-time governance, create operations, or mutate source/wiki/graph/session artifacts.

### V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface

E5 opens exactly one route:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

Current accepted target HTTP surface after E5：

- V1.5 baseline 3 routes
- plus B1 overlay 4 routes
- plus B2 overlay 4 routes
- plus B3 overlay 3 routes
- plus C1 overlay 1 route
- plus C2 overlay 1 route
- plus C3 overlay 1 route
- plus C4 overlay 1 route
- plus D2 overlay 5 routes
- plus D4 overlay 1 route
- plus D5 overlay 1 route
- plus D6 overlay 3 routes
- plus E1 overlay 1 route
- plus E2 overlay 2 routes
- plus E3 overlay 1 route
- plus E4 overlay 2 routes
- plus E5 overlay 1 route
- total：35 routes

E5 does not open correction apply, MCP tools, CLI commands or CLI subcommands. Correction rules build only refreshes the correction-rules artifact from feedback; it preserves existing review statuses, does not update correction plan, and reports stale correction plan risk through warnings / next_actions only.

### V1.6-F1 Console Governance Evidence Baseline Sync

F1 opens no route and adds no overlay.

Current accepted target HTTP after F1 remains:

- V1.5 baseline 3 routes
- A guard +0
- B1/B2/B3 overlays +11 routes
- C1/C2/C3/C4 overlays +4 routes
- D1 planning +0
- D2 overlay +5 routes
- D3 planning +0
- D4/D5/D6 overlays +5 routes
- E1/E2/E3/E4/E5 overlays +7 routes
- total：35 routes

F1 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes, frontend behavior changes, or `/knowledge` behavior changes.

### V1.6-F2 Console Governance Polish

F2 opens no route and adds no overlay.

Current accepted target HTTP after F2 remains 35 routes:

- V1.5 baseline 3 routes
- A guard +0
- B1/B2/B3 overlays +11 routes
- C1/C2/C3/C4 overlays +4 routes
- D1 planning +0
- D2 overlay +5 routes
- D3 planning +0
- D4/D5/D6 overlays +5 routes
- E1/E2/E3/E4/E5 overlays +7 routes
- F1/F2 +0 backend surface

F2 only updates `/knowledge` governance evidence display and frontend static build output. It does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes, target HTTP routes, or correction apply.

### V1.6 Closure Acceptance / Final Release Audit

Closure Acceptance opens no route and adds no overlay.

Current accepted target HTTP after Closure remains 35 routes:

- V1.5 baseline 3 routes
- A guard +0
- B1/B2/B3 overlays +11 routes
- C1/C2/C3/C4 overlays +4 routes
- D1 planning +0
- D2 overlay +5 routes
- D3 planning +0
- D4/D5/D6 overlays +5 routes
- E1/E2/E3/E4/E5 overlays +7 routes
- F1/F2/Closure +0 backend surface

Closure only performs the final public surface freeze audit, focused closure tests, regression validation and documentation sync. It does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes, target HTTP routes, or correction apply. V1.7 capabilities remain planned only.

## Route Opening Policy

- Open routes by capability group.
- Define contract before implementation.
- Reuse shared helpers or existing MCP handlers.
- Preserve `/api/v1/knowledge/*` compatibility routes.
- Use stable IDs, never internal paths, as external contract.

## Candidate Route Groups

| group | status | acceptance requirement |
| --- | --- | --- |
| workspace lifecycle write | completed：B1 workspace create/list/describe/archive target HTTP accepted | keep stable workspace target HTTP contract |
| source lifecycle write | completed：B2 source import/list/describe/remove target HTTP accepted | keep stable `source_id`, artifact refs and no path leakage |
| build lifecycle write | completed：B3 build start/status/cancel target HTTP accepted | keep stable `operation_id` lifecycle and no path leakage |
| graph advanced | C1 completed for neighbors；C2 completed for community；C3 completed for query；C4 completed for graph session inspection | keep read-only graph advanced surfaces stable; V1.6 does not add existing MCP graph tools |
| quality write | E1 completed for feedback；E2 completed for correction rules；E3 completed for correction review；E4 completed for correction plan；E5 completed for correction-rules artifact build | non-destructive governance contract and shared helper reuse |
| session | D1 contract planning / hardening completed；D2 session lifecycle target HTTP create/list/get/close/delete completed；D3 session ingest/query/build planning completed；D4 session ingest target HTTP completed；D5 session query target HTTP completed；D6 session build target HTTP completed | target HTTP routes and cross-surface Session GraphRAG public contract; V1.6 does not add existing MCP session tools |

V1.6 route opening is closed at Closure Acceptance. 下一阶段建议进入 V1.7 planning 或 post-V1.6 backlog triage，不要在没有新 baseline/overlay plan 的情况下新增 backend public surface。

## Non Goals

- Do not expose raw workspace directory layout.
- Do not make target HTTP a mirror of every internal method.
- Do not remove compatibility HTTP during V1.6 route opening.
- Do not open graph advanced, quality write and session routes in the same uncontrolled slice.
