# V1.6 Public Surface Baseline

更新时间：2026-05-16

本文件固化 V1.5 accepted 状态，作为 V1.6 规划和实现的公开面基线。

机器可读基线见 `public-surface-baseline.json`。V1.6-A Public Surface Guard 已使用该 JSON 作为自动化 guard 输入；Markdown 只作为说明文档。

## Project Positioning

`data_service` 是 MCP-first local knowledge governance microservice。它不是 personal knowledge app，也不是 end-user knowledge consumption app。上层 meeting、ASR、interview、learning、IDE plugin 或 agent workflow 只能通过 MCP / CLI / HTTP 调用服务，不应成为 `data_service` 的生产依赖。

## V1.5 Accepted Baseline

| surface | V1.5 baseline |
| --- | --- |
| MCP | 40 tools |
| CLI | top-level commands remain `build / graph / quality / query / source / trace / workspace` |
| compatibility HTTP | `/api/v1/knowledge/*` retained |
| target HTTP | exactly 3 routes |
| console | `/knowledge` service governance console |

MCP graph/session tools already exist in the V1.5 baseline. V1.6-A does not add graph/session MCP tools. V1.6-C focuses on graph advanced target HTTP / CLI minimal surfaces where not yet open. V1.6-D focuses on cross-surface Session GraphRAG public contract convergence.

## Target HTTP Baseline

V1.5 immutable baseline 只开放：

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

V1.5 baseline 尚未开放：

- source/build write target HTTP routes
- graph advanced target HTTP routes
- quality write target HTTP routes
- session target HTTP routes

V1.6-B1 已通过 phase overlay 新增 workspace target HTTP routes；V1.6-B2 已通过 phase overlay 新增 source target HTTP routes；V1.6-B3 已通过 phase overlay 新增 build target HTTP routes；V1.6-C1 已通过 phase overlay 新增 graph neighbors target HTTP route 和 `knowledge graph neighbors` nested CLI command；V1.6-C2 已通过 phase overlay 新增 graph community target HTTP route 和 `knowledge graph community` nested CLI command；V1.6-C3 已通过 phase overlay 新增 graph query target HTTP route 和 `knowledge graph query` nested CLI command；V1.6-C4 已通过 phase overlay 新增 graph session inspection target HTTP route 和 `knowledge graph session` nested CLI command；V1.6-D2 已通过 phase overlay 新增 session lifecycle create/list/get/close/delete target HTTP routes；V1.6-D4/D5/D6 已分别通过 phase overlay 新增 session ingest、session query、session build target HTTP minimal surfaces；V1.6-E1 已通过 phase overlay 新增 quality feedback target HTTP minimal surface；V1.6-E2 已通过 phase overlay 新增 quality correction rules target HTTP minimal surface；V1.6-E3 已通过 phase overlay 新增 quality correction review target HTTP minimal surface；V1.6-E4 已通过 phase overlay 新增 quality correction plan target HTTP minimal surface；V1.6-E5 已通过 phase overlay 新增 quality correction-rules artifact build target HTTP minimal surface。当前 accepted target HTTP route count = 35。本节的 V1.5 baseline 不因此改写。

V1.6-F1 Console Governance Evidence Baseline Sync 不新增 overlay，不新增 target HTTP route，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不修改 frontend 或 `/knowledge` 行为。F1 accepted 后 current target HTTP route count 仍为 35，MCP tool count 仍为 40，CLI diff = none。

V1.6-F2 Console Governance Polish 不新增 overlay，不新增 target HTTP route，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不新增 backend route。F2 只更新 `/knowledge` governance evidence display 和前端静态 build 产物。F2 accepted 后 current target HTTP route count 仍为 35，MCP tool count 仍为 40，CLI diff = none。

V1.6 Closure Acceptance 不新增 overlay，不新增 target HTTP route，不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不新增 backend route。Closure 只完成最终公开面冻结审计、focused closure test、回归验收和文档同步。Closure accepted 后 current target HTTP route count 仍为 35，MCP tool count 仍为 40，CLI diff = none。

## Contract Baseline

外部 contract 只能稳定依赖：

- `workspace_id`
- `source_id`
- `session_id`
- `operation_id`
- `artifact_ref`
- request / response envelope
- normalized error code / message / retryable

内部 filesystem path、workspace layout、artifact layout 只能作为 debug 或 console-only 字段出现，不属于稳定外部 contract。

## Guardrail

V1.6 的每个实现阶段都必须证明：

- 没有隐藏性新增 MCP tool。
- 没有隐藏性新增 HTTP route。
- 没有隐藏性新增 CLI command。
- 旧 `/api/v1/knowledge/*` 兼容入口没有被破坏。
- `/knowledge` 没有被重新定义为终端用户知识消费 App。

## V1.6-A Guard Status

V1.6-A completed 后，公开面 guard 覆盖：

- MCP registry tool count / tool set。
- CLI top-level / nested command inventory。
- data_service HTTP route inventory。
- target HTTP allowlist。
- `/api/v1/knowledge/*` compatibility route retention。
- upper-layer production dependency import scan。

V1.6-A 只新增 guard、测试、报告和文档同步，不新增业务能力。

## V1.6 Accepted Overlays

Accepted overlays are additive records on top of the immutable V1.5 baseline.

### V1.6-B1 Workspace Target HTTP

Overlay file：`public-surface-overlays/v1_6_b1.json`

Allowed target HTTP additions：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

Current accepted target HTTP after B1：V1.5 baseline 3 routes + B1 overlay 4 routes = 7 routes.

B1 does not add MCP tools, CLI commands, CLI subcommands, compatibility HTTP routes, source target HTTP, build target HTTP, graph target HTTP, session target HTTP or quality target HTTP.

### V1.6-B2 Source Target HTTP

Overlay file：`public-surface-overlays/v1_6_b2.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

Current accepted target HTTP after B2：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes = 11 routes.

B2 does not add MCP tools, CLI commands, CLI subcommands, compatibility HTTP routes, build target HTTP, graph target HTTP, session target HTTP or quality target HTTP. Source trace remains a V1.5 baseline route, not a B2 addition.

### V1.6-B3 Build Target HTTP

Overlay file：`public-surface-overlays/v1_6_b3.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

Current accepted target HTTP after B3：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes = 14 routes.

B3 does not add MCP tools, CLI commands, CLI subcommands, compatibility HTTP routes, graph target HTTP, session target HTTP or quality target HTTP. Build target HTTP uses the existing operation lifecycle and stable `operation_id`.

### V1.6-C1 Graph Neighbors Target HTTP / CLI

Overlay file：`public-surface-overlays/v1_6_c1.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/neighbors`

Allowed CLI nested additions：

- `knowledge graph neighbors`

Current accepted target HTTP after C1：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route = 15 routes.

C1 does not add MCP tools, CLI top-level commands, compatibility HTTP routes, graph community/query/session target HTTP, session target HTTP or quality target HTTP. Graph neighbors is read-only and uses stable graph node/edge projection without default internal path/layout exposure.

### V1.6-C2 Graph Community Target HTTP / CLI

Overlay file：`public-surface-overlays/v1_6_c2.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/community`

Allowed CLI nested additions：

- `knowledge graph community`

Current accepted target HTTP after C2：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route = 16 routes.

C2 does not add MCP tools, CLI top-level commands, compatibility HTTP routes or later graph query/session surfaces. Graph community is read-only and uses stable community/member projection without default internal path/layout exposure.

### V1.6-C3 Graph Query Target HTTP / CLI

Overlay file：`public-surface-overlays/v1_6_c3.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/query`

Allowed CLI nested additions：

- `knowledge graph query`

Current accepted target HTTP after C3：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route = 17 routes.

C3 does not add MCP tools, CLI top-level commands, compatibility HTTP routes, graph session target HTTP, session target HTTP or quality target HTTP. Graph query is read-only and uses stable query/node/edge/community projection without default internal path/layout exposure.

### V1.6-C4 Graph Session Target HTTP / CLI

Overlay file：`public-surface-overlays/v1_6_c4.json`

Allowed target HTTP additions：

- `GET /api/workspaces/{workspace_id}/graph/session`

Allowed CLI nested additions：

- `knowledge graph session`

Current accepted target HTTP after C4：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route = 18 routes.

C4 does not add MCP tools, CLI top-level commands, compatibility HTTP routes, session lifecycle target HTTP or quality target HTTP. Graph session is graph-scoped read-only artifact inspection, not full Session GraphRAG public contract, and uses stable session/node/edge projection without default internal path/layout exposure.

### V1.6-D1 Session GraphRAG Contract Hardening

D1 does not add an overlay.

Current accepted target HTTP after D1 remains：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route = 18 routes.

D1 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, session lifecycle target HTTP or quality target HTTP. D1 only adds contract inventory, focused regression guard, artifact_ref rules and documentation sync.

### V1.6-D2 Session Lifecycle Target HTTP

Overlay file：`public-surface-overlays/v1_6_d2.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

Current accepted target HTTP after D2：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes = 23 routes.

D2 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, session ingest/query/build target HTTP or quality target HTTP. C4 graph session remains graph-scoped read-only inspection and is not redefined as session lifecycle.

### V1.6-D3 Session Ingest / Query / Build Contract Planning

D3 does not add an overlay.

Current accepted target HTTP after D3 remains：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes = 23 routes.

D3 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes or target HTTP routes. At D3 acceptance time, session ingest/query/build target HTTP and quality target HTTP remained planned / not opened; D4/D5/D6 later opened ingest/query/build minimal target HTTP in separate overlays, while quality target HTTP remains planned / not opened.

### V1.6-D4 Session Ingest Target HTTP

Overlay file：`public-surface-overlays/v1_6_d4.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

Current accepted target HTTP after D4：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route = 24 routes.

D4 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, session query/build target HTTP or quality target HTTP. D4 session ingest is a session-scoped write surface and does not redefine workspace source import, session query, session build, GraphRAG materialization or quality write.

### V1.6-D5 Session Query Target HTTP

Overlay file：`public-surface-overlays/v1_6_d5.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

Current accepted target HTTP after D5：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route = 25 routes.

D5 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, session build target HTTP or quality target HTTP. D5 session query is a session-scoped read-only surface and does not trigger build, GraphRAG index, materialization or quality write.

### V1.6-D6 Session Build Target HTTP

Overlay file：`public-surface-overlays/v1_6_d6.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

Current accepted target HTTP after D6：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes = 28 routes.

D6 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes or quality target HTTP. D6 session build is session-scoped, uses real operation lifecycle ids, and does not open workspace-level build or quality write as public contract.

### V1.6-E1 Quality Feedback Target HTTP

Overlay file：`public-surface-overlays/v1_6_e1.json`

Allowed target HTTP additions：

- `POST /api/workspaces/{workspace_id}/quality/feedback`

Current accepted target HTTP after E1：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route = 29 routes.

E1 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, quality feedback list, correction rules, correction review or correction plan target HTTP. E1 quality feedback is a non-destructive governance signal write and does not expose internal path/layout as stable contract.

### V1.6-E2 Quality Correction Rules Target HTTP

Allowed additions:

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

Current accepted target HTTP after E2：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route + E2 overlay 2 routes = 31 routes.

E2 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, quality correction review, quality correction plan or quality build target HTTP. E2 correction rules writes are draft/proposal storage only and do not review, approve, activate, apply, generate plans, trigger build or activate read-time governance.

### V1.6-E3 Quality Correction Review Target HTTP

Allowed additions:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

Current accepted target HTTP after E3：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route + E2 overlay 2 routes + E3 overlay 1 route = 32 routes.

E3 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, quality correction plan or quality build target HTTP. E3 review only updates correction rule review status; `approved` is not active/applied, correction plan is not generated or updated, read-time governance is not activated, and correction is not executed.

### V1.6-E4 Quality Correction Plan Target HTTP

Allowed additions:

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

Current accepted target HTTP after E4：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route + E2 overlay 2 routes + E3 overlay 1 route + E4 overlay 2 routes = 34 routes.

E4 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes or quality build target HTTP. E4 only reads or generates the correction plan artifact; it does not execute corrections, apply plans, activate read-time governance, create build/session operations, or mutate source/wiki/graph/session artifacts.

### V1.6-E5 Quality Correction Rules Build Target HTTP

Allowed additions:

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

Current accepted target HTTP after E5：V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route + E2 overlay 2 routes + E3 overlay 1 route + E4 overlay 2 routes + E5 overlay 1 route = 35 routes.

E5 does not add MCP tools, CLI top-level commands, CLI nested commands or compatibility HTTP routes. E5 only builds the correction-rules artifact; it is not quality build, workspace build, session build, correction plan build or correction apply. It preserves existing review statuses, does not update correction plan, and only emits stale-plan warnings / next_actions when a pre-existing correction plan may need regeneration.

### V1.6-F1 Console Governance Evidence Baseline Sync

F1 does not add an overlay.

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

F1 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes, frontend behavior changes or `/knowledge` behavior changes.

### V1.6-F2 Console Governance Polish

F2 does not add an overlay.

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

F2 does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes or target HTTP routes. It only updates `/knowledge` governance evidence display and frontend static build output.

### V1.6 Closure Acceptance / Final Release Audit

Closure Acceptance does not add an overlay.

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

Closure does not add MCP tools, CLI top-level commands, CLI nested commands, compatibility HTTP routes, backend routes or target HTTP routes. It only finalizes public surface freeze audit, focused closure tests, regression validation and documentation sync. V1.5 baseline remains immutable and is not rewritten as current surface.
