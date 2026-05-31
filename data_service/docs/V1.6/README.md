# Data Service V1.6 文档入口

更新时间：2026-05-16

V1.6 从 V1.5 accepted baseline 出发。V1.5 已完成 MCP-first local knowledge governance microservice 的收口验收；当前 V1.6 已 accepted 到 Closure Acceptance，current target HTTP route count = 35。Closure Acceptance 只完成最终公开面冻结审计、文档一致性审计和回归验收，不新增 backend public surface。

V1.6 的核心方向是：在不破坏 V1.5 兼容入口和微服务边界的前提下，按最小能力组继续开放 target HTTP、Graph advanced、Session GraphRAG public contract 和 quality governance 能力。

V1.6-A Public Surface Guard 已完成：本阶段只新增机器可读公开面基线和自动化 guard，不新增 MCP tool、HTTP route、CLI command 或业务能力。

V1.6-B1 Workspace Target HTTP 已完成：本阶段只通过 phase overlay 新增 workspace create/list/describe/archive 4 个 target HTTP routes，不修改 V1.5 baseline，不开放 source/build/graph/session/quality target HTTP。

V1.6-B2 Source Target HTTP 已完成：本阶段只通过 phase overlay 新增 source import/list/describe/remove 4 个 target HTTP routes，不修改 V1.5 baseline，不开放 build/graph/session/quality target HTTP，不改变 V1.5 source trace target HTTP contract。

V1.6-B3 Build Target HTTP 已完成：本阶段只通过 phase overlay 新增 build start/status/cancel 3 个 target HTTP routes，不修改 V1.5 baseline，不开放 graph/session/quality target HTTP。build 可以运行既有 pipeline 阶段，但不开放新的 graph/session/quality public contract。

V1.6-C1 Graph Neighbors Target HTTP / CLI Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/graph/neighbors`，并新增 `knowledge graph neighbors` 嵌套 CLI 命令；不新增 MCP tool，不新增 CLI 顶层命令，不开放 graph community/query/session、session target HTTP 或 quality target HTTP。

V1.6-C2 Graph Community Target HTTP / CLI Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/graph/community`，并新增 `knowledge graph community` 嵌套 CLI 命令；不新增 MCP tool，不新增 CLI 顶层命令；该阶段未开放后续的 graph query 与 graph session。

V1.6-C3 Graph Query Target HTTP / CLI Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/graph/query`，并新增 `knowledge graph query` 嵌套 CLI 命令；不新增 MCP tool，不新增 CLI 顶层命令，不开放 graph session、session target HTTP 或 quality target HTTP。

V1.6-C4 Graph Session Target HTTP / CLI Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/graph/session`，并新增 `knowledge graph session` 嵌套 CLI 命令；该 route 是 graph-scoped read-only inspection surface，不是 session lifecycle target HTTP，不开放完整 Session GraphRAG public contract，不新增 MCP tool 或 CLI 顶层命令。

V1.6-D1 Session GraphRAG Public Contract Planning / Contract Hardening 已完成：本阶段只新增 contract inventory、stable projection audit、error envelope hardening tests、artifact_ref contract 与文档同步；不新增公开面，不开放 `/api/workspaces/{workspace_id}/sessions*`，不新增 quality target HTTP，不改变 C4 accepted payload 语义。

V1.6-D2 Session Lifecycle Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 session create/list/get/close/delete 5 个 target HTTP routes；不新增 MCP tool，不新增 CLI command 或 CLI subcommand，不开放 session ingest/query/build target HTTP，不新增 quality target HTTP。C4 `/graph/session` 仍是 graph-scoped read-only inspection，不是 session lifecycle。

V1.6-D3 Session Ingest / Query / Build Contract Planning 已完成：本阶段只新增 session ingest/query/build contract matrix、future phase split、零公开面 guard 和文档同步；不新增 MCP tool、CLI command 或 HTTP route。D3 accepted 时 target HTTP route count 仍为 23。

V1.6-D4 Session Ingest Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest` 1 个 target HTTP route；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session query/build target HTTP，不新增 quality target HTTP。D4 session ingest 是 session-scoped write，不等于 workspace source import、session query、session build、GraphRAG materialization 或 quality write。D4 accepted 时 target HTTP route count = 24。

V1.6-D5 Session Query Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query` 1 个 target HTTP route；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 session build target HTTP，不新增 quality target HTTP。D5 session query 是 session-scoped read-only operation，不触发 build/index/materialization/quality，不返回 raw GraphRAG payload、raw prompts、raw model messages 或 embedding vectors。D5 accepted 时 target HTTP route count = 25。

V1.6-D6 Session Build Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 session build start/status/cancel 3 个 target HTTP routes；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality target HTTP。D6 session build 是 session-scoped operation lifecycle，复用现有 session build helper 和真实 `operation_id`，不触发 workspace-level build 或 quality write。target HTTP route count = 28。

V1.6-E1 Quality Feedback Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `POST /api/workspaces/{workspace_id}/quality/feedback` 1 个 target HTTP route；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction rules/review/plan target HTTP。E1 quality feedback 是 non-destructive governance signal write，默认 response 不暴露 internal path/layout。target HTTP route count = 29。

V1.6-E2 Quality Correction Rules Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/quality/correction-rules` 和 `POST /api/workspaces/{workspace_id}/quality/correction-rules` 2 个 target HTTP routes；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction review/plan/build target HTTP。E2 correction rules 只读/写 draft correction rules stable projection，不执行 review、approve、activate、apply、plan 或 build。target HTTP route count = 31。

V1.6-E3 Quality Correction Review Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review` 1 个 target HTTP route；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality correction plan/build target HTTP。E3 只更新 review status，`approved` 不等于 active/applied，不生成或更新 correction plan，不激活 read-time governance。target HTTP route count = 32。

V1.6-E4 Quality Correction Plan Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `GET /api/workspaces/{workspace_id}/quality/correction-plan` 和 `POST /api/workspaces/{workspace_id}/quality/correction-plan` 2 个 target HTTP routes；不新增 MCP tool、CLI command 或 CLI subcommand，不开放 quality build target HTTP。E4 只读取或生成 correction plan artifact，POST 使用 plan-only/generate-only 语义，不执行 correction、不 apply plan、不激活 read-time governance。target HTTP route count = 34。

V1.6-E5 Quality Correction Rules Build Target HTTP Minimal Surface 已完成：本阶段只通过 phase overlay 新增 `POST /api/workspaces/{workspace_id}/quality/correction-rules/build` 1 个 target HTTP route；不新增 MCP tool、CLI command 或 CLI subcommand。E5 只构建 correction-rules artifact，不是 quality build、workspace build、session build、correction plan build 或 correction apply；如果 existing correction plan 可能变旧，只通过 warnings / next_actions 提示，不更新 plan、不激活 read-time governance。target HTTP route count = 35。

V1.6-F1 Console Governance Evidence Baseline Sync 已完成：本阶段不新增公开面，不新增 backend route、MCP tool、CLI command 或 CLI subcommand，不修改 frontend 或 `/knowledge` 行为。F1 新增 console governance evidence matrix、focused documentation guard、drawio 同步和阶段报告。target HTTP route count 仍为 35，MCP tool count 仍为 40，CLI diff = none。

V1.6-F2 Console Governance Polish 已完成：本阶段只修改 `/knowledge` governance evidence display 和前端静态 build 产物，不新增 backend public surface，不新增 route、MCP tool、CLI command 或 CLI subcommand。`/knowledge` 展示 V1.5 immutable baseline、accepted overlay summary、MCP 40、CLI diff none、compatibility retained、graph CLI nested additions、F2 no backend public surface 和 Closure Acceptance 边界。target HTTP route count 仍为 35。

V1.6 Closure Acceptance / Final Release Audit 已完成：本阶段只新增 closure focused test、最终验收报告和 V1.6 文档同步；不修改功能代码，不新增 backend route、target HTTP route、compatibility route、MCP tool、CLI command 或 CLI subcommand。target HTTP route count 仍为 35，MCP tool count 仍为 40，CLI diff = none。Correction apply target HTTP 仍未实现，V1.7 capabilities remain planned only。

## 文档索引

- `public-surface-baseline.md`：V1.5 冻结基线，作为 V1.6 的公开面起点。
- `public-surface-baseline.json`：V1.5 公开面机器可读基线，供 V1.6-A guard 使用。
- `target-architecture.md`：V1.6 目标架构。
- `current-vs-target-gap.md`：V1.6 当前与目标差距。
- `current-vs-target-gap.drawio`：V1.6 gap 图。
- `development-plan.md`：V1.6 分阶段开发计划。
- `acceptance-plan.md`：V1.6 验收计划。
- `interface-convergence-plan.md`：V1.6 MCP / CLI / HTTP / target HTTP 接口收敛计划。
- `target-http-routes-plan.md`：V1.6 target HTTP route 开放计划。
- `session-graphrag-contract-plan.md`：V1.6-D1 Session GraphRAG contract inventory 与 hardening plan。
- `session-ingest-query-build-contract-plan.md`：V1.6-D3 Session ingest/query/build contract planning matrix。
- `console-governance-evidence-plan.md`：V1.6-F1 Console governance evidence matrix。
- `PHASE-V1.6-A-PUBLIC-SURFACE-GUARD-REPORT-2026-05-13.md`：V1.6-A 公开面护栏验收报告。
- `PHASE-V1.6-B1-WORKSPACE-TARGET-HTTP-REPORT-2026-05-13.md`：V1.6-B1 Workspace Target HTTP 验收报告。
- `PHASE-V1.6-B2-SOURCE-TARGET-HTTP-REPORT-2026-05-13.md`：V1.6-B2 Source Target HTTP 验收报告。
- `PHASE-V1.6-B3-BUILD-TARGET-HTTP-REPORT-2026-05-13.md`：V1.6-B3 Build Target HTTP 验收报告。
- `PHASE-V1.6-C1-GRAPH-NEIGHBORS-REPORT-2026-05-14.md`：V1.6-C1 Graph Neighbors Target HTTP / CLI 验收报告。
- `PHASE-V1.6-C2-GRAPH-COMMUNITY-REPORT-2026-05-14.md`：V1.6-C2 Graph Community Target HTTP / CLI 验收报告。
- `PHASE-V1.6-C3-GRAPH-QUERY-REPORT-2026-05-14.md`：V1.6-C3 Graph Query Target HTTP / CLI 验收报告。
- `PHASE-V1.6-C4-GRAPH-SESSION-REPORT-2026-05-14.md`：V1.6-C4 Graph Session Target HTTP / CLI 验收报告。
- `PHASE-V1.6-D1-SESSION-GRAPHRAG-CONTRACT-REPORT-2026-05-14.md`：V1.6-D1 Session GraphRAG contract hardening 验收报告。
- `PHASE-V1.6-D2-SESSION-LIFECYCLE-TARGET-HTTP-REPORT-2026-05-14.md`：V1.6-D2 Session Lifecycle Target HTTP 验收报告。
- `PHASE-V1.6-D3-SESSION-INGEST-QUERY-BUILD-CONTRACT-PLAN-REPORT-2026-05-14.md`：V1.6-D3 Session ingest/query/build contract planning 验收报告。
- `PHASE-V1.6-D4-SESSION-INGEST-TARGET-HTTP-REPORT-2026-05-14.md`：V1.6-D4 Session ingest target HTTP 验收报告。
- `PHASE-V1.6-D5-SESSION-QUERY-TARGET-HTTP-REPORT-2026-05-14.md`：V1.6-D5 Session query target HTTP 验收报告。
- `PHASE-V1.6-D6-SESSION-BUILD-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-D6 Session build target HTTP 验收报告。
- `PHASE-V1.6-E1-QUALITY-FEEDBACK-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-E1 Quality feedback target HTTP 验收报告。
- `PHASE-V1.6-E2-QUALITY-CORRECTION-RULES-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-E2 Quality correction rules target HTTP 验收报告。
- `PHASE-V1.6-E3-QUALITY-CORRECTION-REVIEW-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-E3 Quality correction review target HTTP 验收报告。
- `PHASE-V1.6-E4-QUALITY-CORRECTION-PLAN-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-E4 Quality correction plan target HTTP 验收报告。
- `PHASE-V1.6-E5-QUALITY-CORRECTION-RULES-BUILD-TARGET-HTTP-REPORT-2026-05-15.md`：V1.6-E5 Quality correction rules build target HTTP 验收报告。
- `PHASE-V1.6-F1-CONSOLE-GOVERNANCE-EVIDENCE-BASELINE-REPORT-2026-05-15.md`：V1.6-F1 Console governance evidence baseline 验收报告。
- `PHASE-V1.6-F2-CONSOLE-GOVERNANCE-POLISH-REPORT-2026-05-16.md`：V1.6-F2 Console governance polish 验收报告。
- `PHASE-V1.6-CLOSURE-ACCEPTANCE-REPORT-2026-05-16.md`：V1.6 Closure Acceptance / Final Release Audit 验收报告。

## 基线

V1.5 基线已固化在 `../V1.5/`：

- V1.5 closure status：accepted。
- MCP tool count：40。
- CLI 顶层命令：`build / graph / quality / query / source / trace / workspace`。
- V1.5 target HTTP baseline 固定为 3 个 route：
  - `POST /api/workspaces/{workspace_id}/query`
  - `POST /api/workspaces/{workspace_id}/distill`
  - `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`
- `/api/v1/knowledge/*` compatibility routes retained。
- `/knowledge` 是 service governance console，不是 end-user knowledge consumption app。
- MCP graph/session tools 已属于 V1.5 baseline；V1.6-A 未新增 graph/session MCP tools。

## 当前 V1.6 Accepted Overlays

V1.6-B1 accepted overlay 新增 4 个 target HTTP routes：

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `POST /api/workspaces/{workspace_id}/archive`

V1.6-B2 accepted overlay 新增 4 个 target HTTP routes：

- `POST /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}`
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove`

V1.6-B3 accepted overlay 新增 3 个 target HTTP routes：

- `POST /api/workspaces/{workspace_id}/build/start`
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel`

V1.6-C1 accepted overlay 新增 1 个 target HTTP route：

- `GET /api/workspaces/{workspace_id}/graph/neighbors`

V1.6-C2 accepted overlay 新增 1 个 target HTTP route：

- `GET /api/workspaces/{workspace_id}/graph/community`

V1.6-C3 accepted overlay 新增 1 个 target HTTP route：

- `GET /api/workspaces/{workspace_id}/graph/query`

V1.6-C4 accepted overlay 新增 1 个 target HTTP route：

- `GET /api/workspaces/{workspace_id}/graph/session`

V1.6-D2 accepted overlay 新增 5 个 target HTTP routes：

- `POST /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`

V1.6-D4 accepted overlay 新增 1 个 target HTTP route：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`

V1.6-D5 accepted overlay 新增 1 个 target HTTP route：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`

V1.6-D6 accepted overlay 新增 3 个 target HTTP routes：

- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`

V1.6-E1 accepted overlay 新增 1 个 target HTTP route：

- `POST /api/workspaces/{workspace_id}/quality/feedback`

V1.6-E2 accepted overlay 新增 2 个 target HTTP routes：

- `GET /api/workspaces/{workspace_id}/quality/correction-rules`
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`

V1.6-E3 accepted overlay 新增 1 个 target HTTP route：

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`

V1.6-E4 accepted overlay 新增 2 个 target HTTP routes：

- `GET /api/workspaces/{workspace_id}/quality/correction-plan`
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`

V1.6-E5 accepted overlay 新增 1 个 target HTTP route：

- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`

当前 accepted target HTTP surface = V1.5 baseline 3 routes + B1 overlay 4 routes + B2 overlay 4 routes + B3 overlay 3 routes + C1 overlay 1 route + C2 overlay 1 route + C3 overlay 1 route + C4 overlay 1 route + D2 overlay 5 routes + D4 overlay 1 route + D5 overlay 1 route + D6 overlay 3 routes + E1 overlay 1 route + E2 overlay 2 routes + E3 overlay 1 route + E4 overlay 2 routes + E5 overlay 1 route = 35 routes。

压缩计数：A guard +0；B1/B2/B3 overlays +11；C1/C2/C3/C4 overlays +4；D1 planning +0；D2 overlay +5；D3 planning +0；D4/D5/D6 overlays +5；E1/E2/E3/E4/E5 overlays +7；current target HTTP route count = 35。

V1.6-F1 不新增 overlay，不新增 public surface。V1.6-F2 不新增 overlay，不新增 backend public surface，只更新 `/knowledge` governance evidence display。Closure Acceptance 不新增 overlay，不新增 public surface，只完成最终公开面冻结审计和回归验收。

V1.6-D1 未新增 overlay。V1.6-D2 只开放 session lifecycle minimal surface；D4/D5/D6 后续已分别开放 session ingest、session query、session build minimal target HTTP。D1-D6 均未开放 quality target HTTP；E1/E2/E3/E4/E5 后续已分别开放 quality feedback、correction rules、correction review、correction plan、correction rules build minimal target HTTP。

V1.6-D3 未新增 overlay，D4 以独立 overlay 开放 session ingest minimal route，D5 以独立 overlay 开放 session query minimal read-only route，D6 以独立 overlay 开放 session build start/status/cancel minimal routes。E1 只开放 quality feedback target HTTP；E2 只开放 quality correction rules list/write target HTTP；E3 只开放 quality correction review target HTTP；E4 只开放 quality correction plan read/generate target HTTP；E5 只开放 correction-rules artifact build target HTTP，不开放 correction apply。

## 同步规则

V1.6 开始后，每个子阶段完成时必须同步更新：

- `development-plan.md`
- `acceptance-plan.md`
- `target-architecture.md`
- `current-vs-target-gap.md`
- `current-vs-target-gap.drawio`
- 与该阶段直接相关的 contract / convergence plan

任何文档不得暗示未实现的 V1.6 候选能力已经开放。公开面状态以实测 MCP registry、CLI parser 和 HTTP route 扫描为准。
