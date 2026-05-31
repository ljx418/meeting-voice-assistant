# V1.6 Interface Convergence Plan

更新时间：2026-05-16

## Baseline

V1.5 已完成 query、distill、source trace 的 shared contract 收敛，并开放首批 target HTTP route。V1.6 的接口收敛从这些 accepted contracts 出发。

V1.6-A 已完成 Public Surface Guard：机器可读基线和自动化测试会在后续每个阶段检查 MCP registry、CLI parser、HTTP route inventory、target HTTP allowlist 和 compatibility retention。

V1.6-B1 已完成 workspace create/list/describe/archive target HTTP 收敛。V1.5 baseline 不变，B1 以 phase overlay 记录 4 个 workspace target HTTP additions。

V1.6-B2 已完成 source import/list/describe/remove target HTTP 收敛。V1.5 baseline 不变，B2 以 phase overlay 记录 4 个 source target HTTP additions；V1.5 source trace target HTTP route 保持 baseline route，不是 B2 新增。

V1.6-B3 已完成 build start/status/cancel target HTTP 收敛。V1.5 baseline 不变，B3 以 phase overlay 记录 3 个 build target HTTP additions；graph/session/quality target HTTP 仍未开放。Build target HTTP 使用既有 operation lifecycle 和 stable `operation_id`。

V1.6-C1 已完成 graph neighbors target HTTP / CLI minimal surface。V1.5 baseline 不变，C1 以 phase overlay 记录 1 个 graph neighbors target HTTP addition，并允许 `knowledge graph neighbors` nested CLI addition；graph community/query/session、session target HTTP 和 quality target HTTP 仍未开放。

V1.6-C2 已完成 graph community target HTTP / CLI minimal read-only surface。V1.5 baseline 不变，C2 以 phase overlay 记录 1 个 graph community target HTTP addition，并允许 `knowledge graph community` nested CLI addition；该阶段未开放后续 graph query 或 graph session。

V1.6-C3 已完成 graph query target HTTP / CLI minimal read-only surface。V1.5 baseline 不变，C3 以 phase overlay 记录 1 个 graph query target HTTP addition，并允许 `knowledge graph query` nested CLI addition；graph session、session target HTTP 和 quality target HTTP 仍未开放。

V1.6-C4 已完成 graph session target HTTP / CLI minimal read-only inspection surface。V1.5 baseline 不变，C4 以 phase overlay 记录 1 个 graph-scoped session graph artifact inspection target HTTP addition，并允许 `knowledge graph session` nested CLI addition；session lifecycle target HTTP、完整 Session GraphRAG public contract 和 quality target HTTP 仍未开放。

V1.6-D1 已完成 Session GraphRAG contract planning / hardening。D1 不新增公开面，不新增 phase overlay；current target HTTP surface 仍为 18 routes。D1 固化 session contract inventory、stable projection、error envelope、artifact_ref non-path rules 和 no `/sessions*` route guard。

V1.6-D2 已完成 Session Lifecycle Target HTTP Minimal Surface。V1.5 baseline 不变，D2 以 phase overlay 记录 5 个 session lifecycle target HTTP additions：create/list/get/close/delete。D2 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session ingest/query/build target HTTP，不开放 quality target HTTP；current target HTTP surface = 23 routes。

V1.6-D3 已完成 Session Ingest / Query / Build Contract Planning。D3 不新增公开面，不新增 phase overlay；current target HTTP surface 仍为 23 routes。D3 只固化 future contract matrix 和 guard，明确 D4 ingest、D5 query、D6 build 必须拆开执行。

V1.6-D4 已完成 Session Ingest Target HTTP Minimal Surface。D4 通过 phase overlay 新增 1 个 session ingest target HTTP route，current target HTTP surface = 24 routes。D4 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session query/build target HTTP，不开放 quality target HTTP。

V1.6-D5 已完成 Session Query Target HTTP Minimal Surface。D5 通过 phase overlay 新增 1 个 session query target HTTP route，current target HTTP surface = 25 routes。D5 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session build target HTTP，不开放 quality target HTTP；session query 是 session-scoped read-only operation。

V1.6-D6 已完成 Session Build Target HTTP Minimal Surface。D6 通过 phase overlay 新增 3 个 session build target HTTP routes，current target HTTP surface = 28 routes。D6 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality target HTTP；session build 是 session-scoped operation lifecycle。

V1.6-E1 已完成 Quality Feedback Target HTTP Minimal Surface。E1 通过 phase overlay 新增 1 个 quality feedback target HTTP route，current target HTTP surface = 29 routes。E1 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction rules/review/plan target HTTP。

V1.6-E2 已完成 Quality Correction Rules Target HTTP Minimal Surface。E2 通过 phase overlay 新增 2 个 quality correction rules target HTTP routes，current target HTTP surface = 31 routes。E2 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction review/plan/build target HTTP。

V1.6-E3 已完成 Quality Correction Review Target HTTP Minimal Surface。E3 通过 phase overlay 新增 1 个 quality correction review target HTTP route，current target HTTP surface = 32 routes。E3 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction plan/build target HTTP。

V1.6-E4 已完成 Quality Correction Plan Target HTTP Minimal Surface。E4 通过 phase overlay 新增 2 个 quality correction plan target HTTP routes，current target HTTP surface = 34 routes。E4 不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality build target HTTP。

V1.6-E5 已完成 Quality Correction Rules Build Target HTTP Minimal Surface。E5 通过 phase overlay 新增 1 个 correction-rules artifact build target HTTP route，current target HTTP surface = 35 routes。E5 不新增 MCP tool、CLI command 或 CLI subcommand；该 build 不是 quality build、workspace build、session build、correction plan build 或 correction apply。

V1.6-F1 已完成 Console Governance Evidence Baseline Sync。F1 不新增公开面，不新增 backend route、MCP tool、CLI command 或 CLI subcommand，不修改 frontend 或 `/knowledge` 行为；current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI diff = none。

V1.6-F2 已完成 Console Governance Polish。F2 只更新 `/knowledge` governance evidence display 和前端静态 build 产物，不新增 backend route、target HTTP route、compatibility HTTP route、MCP tool、CLI command 或 CLI subcommand；current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI diff = none。

V1.6 Closure Acceptance 已完成。Closure 只做最终公开面冻结审计、focused closure test、回归验收、drawio XML validation 和文档同步；不修改功能代码，不新增 backend route、target HTTP route、compatibility HTTP route、MCP tool、CLI command 或 CLI subcommand。Current target HTTP surface 仍为 35 routes，MCP tool count 仍为 40，CLI diff = none。Correction apply target HTTP 仍未实现；V1.7 capabilities remain planned only。

## Convergence Rules

- MCP remains primary.
- CLI `knowledge ...` is the human operator entrypoint.
- target HTTP uses workspace-scoped URLs.
- compatibility HTTP `/api/v1/knowledge/*` remains retained.
- new surfaces must reuse existing shared helpers or MCP handlers.
- payloads must converge before public routes are opened.

## Capability Plan

| capability | V1.5 state | V1.6 convergence target |
| --- | --- | --- |
| workspace | MCP + CLI + compatibility HTTP + B1 target HTTP create/list/describe/archive | maintain stable workspace target HTTP contract |
| source | MCP + CLI + compatibility HTTP + B2 target HTTP import/list/describe/remove | maintain stable `source_id`, artifact refs, no path leakage and no build/graph/session/quality side effects |
| build | MCP + CLI + compatibility HTTP + B3 target HTTP start/status/cancel | maintain stable `operation_id`, operation envelope and no path leakage |
| query | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| distill | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| trace | MCP + CLI + compatibility HTTP + target HTTP | harden existing contract |
| graph | MCP graph tools already exist；CLI exposes snapshot + neighbors + community + query + session；target HTTP exposes C1 neighbors, C2 community, C3 query and C4 graph session inspection | keep read-only graph surfaces behind stable projection |
| session | MCP session tools already exist；C4 opens only graph-scoped artifact inspection；D1 contract inventory/hardening completed；D2 opens minimal session lifecycle target HTTP create/list/get/close/delete；D3 contract planning completed with no public surface；D4 opens session ingest target HTTP only；D5 opens session query target HTTP only；D6 opens session build start/status/cancel target HTTP only | full Session GraphRAG public contract convergence remains staged; quality remains separate |
| quality | MCP + CLI + compatibility HTTP；E1 quality feedback target HTTP accepted；E2 correction rules target HTTP accepted；E3 correction review target HTTP accepted；E4 correction plan target HTTP accepted；E5 correction rules build target HTTP accepted | keep quality target HTTP split by governance action; no correction apply route is open |
| console governance | `/knowledge` governance console exists；F1 evidence baseline accepted；F2 evidence display accepted；Closure Acceptance accepted | no new backend public surface after F2; V1.7 planning remains separate |

## Drift Guards

Each convergence slice must include tests that prevent:

- duplicate payload assembly across surfaces。
- route opening without documented contract。
- CLI command opening without public surface audit。
- MCP tool addition without registry count update。
- stable contract dependence on internal filesystem layout。

MCP graph/session tools already exist in the V1.5 baseline. V1.6-C/D 不把这些 MCP tools 重新计为新增能力；只收敛尚未开放的 target HTTP / CLI minimal surfaces 和跨入口 Session GraphRAG public contract。
