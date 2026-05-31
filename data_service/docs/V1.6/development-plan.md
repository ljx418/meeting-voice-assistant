# Data Service V1.6 Development Plan

更新时间：2026-05-16

## Summary

V1.6 从 V1.5 accepted baseline 出发，按最小能力组推进。每个阶段完成后必须做端到端出门验证、公开面扫描和文档同步。

## Phase V1.6-A: Public Surface Guard

状态：completed。

目标：把 V1.5 closure audit 转成可重复的阶段护栏。本阶段只新增 guard，不新增业务能力。

交付：

- machine-readable V1.5 public surface baseline。
- MCP registry count guard。
- CLI top-level / nested command guard。
- HTTP route inventory guard。
- target HTTP route allowlist guard。
- `/api/v1/knowledge/*` compatibility retention check。
- upper-layer production dependency guard。

验收：

- MCP baseline/current/diff = 40 / 40 / none。
- CLI top-level and nested command diff = none。
- target HTTP baseline/current/diff = exactly 3 routes / exactly 3 routes / none。
- no hidden route/tool/command expansion。
- V1.6-A completed with zero public surface additions. Since then, B1/B2/B3, C1/C2/C3/C4, D1/D2/D3/D4/D5/D6, E1/E2/E3/E4/E5, F1, F2 and Closure Acceptance have been accepted.

## Phase V1.6-B: Lifecycle Target HTTP

目标：为 workspace/source/build lifecycle 设计并分阶段开放 target HTTP write routes。

### Phase V1.6-B1: Workspace Target HTTP

状态：completed。

目标：只开放 workspace lifecycle 的最小 target HTTP 面，不进入 source/build/graph/session/quality。

交付：

- B1 phase overlay：`public-surface-overlays/v1_6_b1.json`。
- `POST /api/workspaces` workspace create。
- `GET /api/workspaces` workspace list。
- `GET /api/workspaces/{workspace_id}` workspace describe。
- `POST /api/workspaces/{workspace_id}/archive` workspace archive。
- target HTTP 默认 response 不暴露内部 filesystem path/layout。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1 overlay 精确新增 4 个 workspace target HTTP routes。
- target HTTP current surface = 7 routes。
- MCP tool count 仍为 40，CLI inventory 不变。
- source/build/graph/session/quality target HTTP 仍未开放。
- compatibility HTTP remains retained。

### Phase V1.6-B2: Source Target HTTP

状态：completed。

目标：只开放 source lifecycle 的最小 target HTTP 面，不进入 build/graph/session/quality。

交付：

- B2 phase overlay：`public-surface-overlays/v1_6_b2.json`。
- `POST /api/workspaces/{workspace_id}/sources` source import。
- `GET /api/workspaces/{workspace_id}/sources` source list。
- `GET /api/workspaces/{workspace_id}/sources/{source_id}` source describe。
- `POST /api/workspaces/{workspace_id}/sources/{source_id}/remove` source soft remove。
- target HTTP 默认 response 不暴露 source physical path、workspace layout 或 artifact physical path。
- source import 不触发 build、GraphRAG、session graph 或 quality write。
- V1.5 source trace target HTTP route 保持不变。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1 overlay 精确新增 4 个 workspace target HTTP routes。
- B2 overlay 精确新增 4 个 source target HTTP routes。
- target HTTP current surface = 11 routes。
- MCP tool count 仍为 40，CLI inventory 不变。
- build/graph/session/quality target HTTP 仍未开放。
- compatibility HTTP remains retained。

### Phase V1.6-B3: Build Target HTTP

状态：completed。

目标：只开放 build lifecycle 的最小 target HTTP 面，不进入 graph/session/quality。

交付：

- B3 phase overlay：`public-surface-overlays/v1_6_b3.json`。
- `POST /api/workspaces/{workspace_id}/build/start` build start。
- `GET /api/workspaces/{workspace_id}/build/operations/{operation_id}` build status。
- `POST /api/workspaces/{workspace_id}/build/operations/{operation_id}/cancel` build cancel。
- build target HTTP 使用真实 `operation_id` 与既有 operation lifecycle。
- target HTTP 默认 response 不暴露 workspace/source/artifact physical path 或 internal layout。
- build pipeline 可运行既有 llmwiki/GraphRAG/summary/diagnostics 阶段，但不开放 graph/session/quality target HTTP public contract。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1/B2/B3 overlays 分别精确新增 workspace/source/build target HTTP routes。
- target HTTP current surface = 14 routes。
- MCP tool count 仍为 40，CLI inventory 不变。
- graph/session/quality target HTTP 仍未开放。
- new routes use `workspace_id` / `operation_id`。
- no internal path/layout as stable contract。
- compatibility HTTP remains retained。

## Phase V1.6-C: Graph Advanced Minimal Surface

目标：不新增 V1.5 已存在的 MCP graph tools；按最小子能力开放尚未开放的 graph advanced target HTTP / CLI surfaces。

说明：MCP graph tools already exist in the V1.5 baseline. V1.6-C does not add them as new MCP tools; it focuses on graph advanced target HTTP / CLI minimal surfaces where not yet open.

候选顺序：

- graph neighbors target HTTP / CLI surface：completed in V1.6-C1
- graph community target HTTP / CLI surface：completed in V1.6-C2
- graph query target HTTP / CLI surface：completed in V1.6-C3
- graph session target HTTP / CLI surface：completed in V1.6-C4

### Phase V1.6-C1: Graph Neighbors Target HTTP / CLI Minimal Surface

状态：completed。

目标：只开放 graph neighbors 的最小公开面，不进入 graph community/query/session，不处理 session/quality，不新增 MCP tool 或 CLI 顶层命令。

交付：

- C1 phase overlay：`public-surface-overlays/v1_6_c1.json`。
- `GET /api/workspaces/{workspace_id}/graph/neighbors`。
- `knowledge graph neighbors` 嵌套 CLI 命令。
- shared graph neighbors stable projection。
- `node_id` / `entity_id` one-of 校验。
- `depth` 范围 1-3，`max_nodes` 范围 1-500。
- 默认 response 不暴露 GraphRAG cache path、workspace path、artifact physical path 或 raw artifact path。
- read-only 语义：不触发 build/index/session graph/quality write，不创建 operation，不修改 source registry。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1/B2/B3 overlays 保持 accepted。
- C1 overlay 精确新增 1 个 graph neighbors target HTTP route。
- target HTTP current surface = 15 routes。
- MCP tool count 仍为 40。
- CLI top-level commands 不变。
- CLI nested addition 仅为 `graph.neighbors`。
- graph community/query/session、session target HTTP、quality target HTTP 仍未开放。
- API/MCP/combined regression 通过。

### Phase V1.6-C2: Graph Community Target HTTP / CLI Minimal Surface

状态：completed。

目标：只开放 graph community 的最小 read-only 公开面，不进入后续 graph query 或 graph session，不处理 session/quality，不新增 MCP tool 或 CLI 顶层命令。

交付：

- C2 phase overlay：`public-surface-overlays/v1_6_c2.json`。
- `GET /api/workspaces/{workspace_id}/graph/community`。
- `knowledge graph community` 嵌套 CLI 命令。
- shared graph community stable projection。
- list/detail 固定语义：无 `community_id` 返回列表，有 `community_id` 返回单个 community。
- `limit` 范围 1-100；detail 请求中的 `limit` 被忽略。
- `include_members=false` 默认不返回 members；`include_members=true` 返回 stable member projection。
- 默认 response 不暴露 GraphRAG cache path、workspace path、artifact physical path 或 raw artifact path。
- read-only 语义：不触发 build/index/materialization/session graph/quality write，不创建 operation，不修改 source registry，不写入 graph snapshot。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1/B2/B3/C1 overlays 保持 accepted。
- C2 overlay 精确新增 1 个 graph community target HTTP route。
- target HTTP current surface = 16 routes。
- MCP tool count 仍为 40。
- CLI top-level commands 不变。
- CLI nested addition 仅为 `graph.community`。
- C2 当时未开放后续 graph query 与 graph session；C3 已在后续阶段完成 graph query，C4 已在后续阶段完成 graph session inspection。
- API/MCP/combined regression 通过。

### Phase V1.6-C3: Graph Query Target HTTP / CLI Minimal Surface

状态：completed。

目标：只开放 graph query 的最小 read-only 公开面，不进入 graph session，不处理 session/quality，不新增 MCP tool 或 CLI 顶层命令。

交付：

- C3 phase overlay：`public-surface-overlays/v1_6_c3.json`。
- `GET /api/workspaces/{workspace_id}/graph/query`。
- `knowledge graph query` 嵌套 CLI 命令。
- shared graph query stable projection。
- `q` 必填；`top_k` 范围 1-50。
- `include_nodes` / `include_edges` 默认 true；`include_communities` 默认 false。
- graph artifacts 不存在时返回 normalized blocked，不自动 build。
- 默认 response 不暴露 GraphRAG cache path、workspace path、artifact physical path、DB path 或 raw artifact path。
- read-only 语义：不触发 build/index/materialization/session graph/quality write，不创建 operation，不修改 source registry，不写入 graph snapshot。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1/B2/B3/C1/C2 overlays 保持 accepted。
- C3 overlay 精确新增 1 个 graph query target HTTP route。
- target HTTP current surface = 17 routes。
- MCP tool count 仍为 40。
- CLI top-level commands 不变。
- CLI nested addition 仅为 `graph.query`。
- C3 accepted 时 graph session、session target HTTP、quality target HTTP 仍未开放；C4 后 graph session inspection 已开放，D2/D4/D5/D6 后 session lifecycle/ingest/query/build minimal target HTTP 已分阶段开放；quality target HTTP 仍未开放。
- API/MCP/combined regression 通过。

### Phase V1.6-C4: Graph Session Target HTTP / CLI Minimal Surface

状态：completed。

目标：只开放 graph-scoped session graph artifact inspection 的最小 read-only surface，不开放 session lifecycle，不进入完整 Session GraphRAG public contract，不处理 quality，不新增 MCP tool 或 CLI 顶层命令。

交付：

- C4 phase overlay：`public-surface-overlays/v1_6_c4.json`。
- `GET /api/workspaces/{workspace_id}/graph/session`。
- `knowledge graph session` 嵌套 CLI 命令。
- shared graph session stable projection。
- list/detail 固定语义：无 `session_id` 只列出已有 session graph artifact summaries；有 `session_id` 只描述已有 session graph artifact summary。
- `limit` 范围 1-100；`node_limit` 范围 1-200；`edge_limit` 范围 1-500。
- `include_nodes=false` 与 `include_edges=false` 默认不返回 nodes / edges；开启时返回 capped stable projection。
- 默认 response 不暴露 workspace path、GraphRAG cache path、artifact physical path、raw parquet/json path 或 session storage layout。
- read-only 语义：不触发 build/index/materialization/quality write，不创建 operation，不修改 source registry，不写入 graph snapshot，不更新 session lifecycle state。

验收：

- V1.5 baseline 仍保持 3 个 target HTTP routes。
- B1/B2/B3/C1/C2/C3 overlays 保持 accepted。
- C4 overlay 精确新增 1 个 graph session target HTTP route。
- target HTTP current surface = 18 routes。
- MCP tool count 仍为 40。
- CLI top-level commands 不变。
- CLI nested addition 仅为 `graph.session`。
- session lifecycle target HTTP、quality target HTTP 仍未开放。
- C4 不等于完整 Session GraphRAG public contract。
- API/MCP/combined regression 通过。

验收：

- each subcommand or route has its own contract test。
- `snapshot` behavior remains compatible。
- GraphRAG internals stay behind `app.graphrag.service`。

## Phase V1.6-D: Session GraphRAG Public Contract

目标：不新增 V1.5 已存在的 MCP session tools；固化 Session GraphRAG 跨 MCP / CLI / HTTP / target HTTP 的稳定外部 contract。

说明：MCP session tools already exist in the V1.5 baseline. V1.6-D does not add them as new MCP tools; it focuses on cross-surface Session GraphRAG public contract convergence.

### Phase V1.6-D1: Session GraphRAG Public Contract Planning / Contract Hardening

状态：completed。

目标：只做 Session GraphRAG contract inventory、stable projection audit、error envelope hardening、artifact_ref contract、regression guard 和文档同步，不新增公开面，不开放完整 session lifecycle target HTTP。

交付：

- `session-graphrag-contract-plan.md` surface matrix。
- `test_session_graphrag_contract.py` focused regression guard。
- artifact_ref non-path rules。
- unknown session / missing artifact / cross-workspace isolation error contract 固化。
- C4 `/graph/session` 仍被限定为 graph-scoped read-only inspection。

验收：

- target HTTP current surface = 18 routes。
- MCP tool count = 40。
- CLI top-level and nested inventory unchanged from C4。
- no `/api/workspaces/{workspace_id}/sessions*` target HTTP。
- no quality target HTTP。
- API/MCP/combined regression 通过。
- current-vs-target-gap.md 与 drawio 同步。

### Phase V1.6-D2: Session Lifecycle Target HTTP Minimal Surface

状态：completed。

目标：在 D1 contract hardening 之后，只开放 session create/list/get/close/delete 的最小 target HTTP lifecycle surface。D2 不处理 session ingest/query/build，不处理 quality target HTTP，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- D2 phase overlay：`public-surface-overlays/v1_6_d2.json`。
- `POST /api/workspaces/{workspace_id}/sessions`。
- `GET /api/workspaces/{workspace_id}/sessions`。
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/close`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/delete`。
- `session_lifecycle_contract.py` stable projection。
- `test_target_http_session_lifecycle.py` focused regression guard。

验收：

- target HTTP current surface = 23 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no session ingest/query/build target HTTP。
- no quality target HTTP。
- uses `session_id` and `artifact_ref` as stable external IDs。
- no dependency on upper-layer meeting or ASR modules。
- internal session storage paths remain debug-only。
- current-vs-target-gap.md 与 drawio 同步。

### Phase V1.6-D3: Session Ingest / Query / Build Contract Planning

状态：completed。

目标：在 D2 lifecycle target HTTP accepted 后，只做 session ingest/query/build 的 contract inventory、future target HTTP contract planning、零公开面 guard 和文档同步。D3 is a planning and contract hardening phase only. It opens no public surface.

交付：

- `session-ingest-query-build-contract-plan.md` contract matrix。
- `test_session_ingest_query_build_contract_plan.py` focused guard。
- 明确 D4/D5/D6 拆分：ingest、query、build 不能一次性实现。
- 明确 D2 lifecycle 与 ingest/query/build 的边界。

验收：

- target HTTP current surface = 23 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no new HTTP route。
- no session ingest/query/build target HTTP。
- no quality target HTTP。
- D2 lifecycle、D1 contract、C4 graph session tests 仍通过。

### Phase V1.6-D4: Session Ingest Target HTTP Minimal Surface

状态：completed。

目标：在 D3 planning accepted 后，只开放 session ingest target HTTP minimal surface。D4 不同时开放 session query/build 或 quality target HTTP。

交付：

- D4 phase overlay：`public-surface-overlays/v1_6_d4.json`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/ingest`。
- `session_ingest_contract.py` stable projection / request guard。
- `test_target_http_session_ingest.py` focused tests。
- D4 phase report。

验收：

- target HTTP current surface = 24 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no session query/build target HTTP。
- no quality target HTTP。
- session ingest 不触发 build / GraphRAG index / materialization / query / quality write。

### Phase V1.6-D5: Session Query Target HTTP Minimal Surface

状态：completed。

目标：在 D4 accepted 后，只开放 session query target HTTP minimal read-only surface。D5 不同时开放 session build 或 quality target HTTP。

交付：

- D5 phase overlay：`public-surface-overlays/v1_6_d5.json`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/query`。
- `session_query_contract.py` stable projection / request guard。
- `test_target_http_session_query.py` focused tests。
- D5 phase report。

验收：

- target HTTP current surface = 25 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no session build target HTTP。
- no quality target HTTP。
- session query 不触发 build / GraphRAG index / materialization / quality write，不外泄 raw GraphRAG payload。

### Phase V1.6-D6: Session Build Target HTTP Minimal Surface

状态：completed。

目标：在 D5 accepted 后，只开放 session build start/status/cancel target HTTP minimal surface。D6 不同时开放 quality target HTTP。

交付：

- D6 phase overlay：`public-surface-overlays/v1_6_d6.json`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/start`。
- `GET /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}`。
- `POST /api/workspaces/{workspace_id}/sessions/{session_id}/build/operations/{operation_id}/cancel`。
- `session_build_contract.py` stable operation projection / path sanitization。
- `test_target_http_session_build.py` focused tests。
- D6 phase report。

验收：

- target HTTP current surface = 28 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no quality target HTTP。
- session build 使用真实 operation lifecycle id。
- session build 不触发 workspace-level build 或 quality write，不外泄 artifact/log/diagnostics path。

## Phase V1.6-E: Quality Target HTTP Write Routes

目标：把 quality write 能力迁移到 target HTTP，而不是扩大旧 compatibility route。

### Phase V1.6-E1: Quality Feedback Target HTTP Minimal Surface

状态：completed。

目标：只开放 quality feedback 的最小 target HTTP write surface，不开放 correction rules/review/plan，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- E1 phase overlay：`public-surface-overlays/v1_6_e1.json`。
- `POST /api/workspaces/{workspace_id}/quality/feedback`。
- quality feedback stable projection。
- `test_target_http_quality_feedback.py` focused tests。
- E1 phase report。

验收：

- target HTTP current surface = 29 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no quality correction rules/review/plan target HTTP。
- no internal path/layout leakage。
- feedback write is non-destructive and does not mutate source registry, build operations or correction plan。

### Phase V1.6-E2: Quality Correction Rules Target HTTP Minimal Surface

状态：completed。

目标：只开放 correction rules 的最小 target HTTP surface，不开放 correction review、correction plan 或 quality build，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- E2 phase overlay：`public-surface-overlays/v1_6_e2.json`。
- `GET /api/workspaces/{workspace_id}/quality/correction-rules`。
- `POST /api/workspaces/{workspace_id}/quality/correction-rules`。
- quality correction rules stable projection。
- `test_target_http_quality_correction_rules.py` focused tests。
- E2 phase report。

验收：

- target HTTP current surface = 31 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no quality correction review/plan/build target HTTP。
- correction rules write remains draft/proposal storage only。
- no review/approve/activate/apply/read-time governance side effects。
- no correction plan/build side effects。
- no internal path/layout leakage。

### Phase V1.6-E3: Quality Correction Review Target HTTP Minimal Surface

状态：completed。

目标：只开放 correction review 的最小 target HTTP surface，不开放 correction plan 或 quality build，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- E3 phase overlay：`public-surface-overlays/v1_6_e3.json`。
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/{rule_id}/review`。
- review-only helper，不生成或更新 correction plan。
- `test_target_http_quality_correction_review.py` focused tests。
- E3 phase report。

验收：

- target HTTP current surface = 32 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no quality correction plan/build target HTTP。
- review only updates correction rule review status。
- approved does not mean active/applied。
- no correction plan generation/update。
- no read-time governance activation。
- no correction execution。

### Phase V1.6-E4: Quality Correction Plan Target HTTP Minimal Surface

状态：completed。

目标：只开放 correction plan 的最小 target HTTP surface，不开放 quality build，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- E4 phase overlay：`public-surface-overlays/v1_6_e4.json`。
- `GET /api/workspaces/{workspace_id}/quality/correction-plan`。
- `POST /api/workspaces/{workspace_id}/quality/correction-plan`。
- plan-only/generate-only helper，只读或写 `correction_plan` artifact。
- `test_target_http_quality_correction_plan.py` focused tests。
- E4 phase report。

验收：

- target HTTP current surface = 34 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- no quality build target HTTP。
- correction plan artifact changes as expected。
- correction rules、review artifacts、source/wiki/graph/session artifacts unchanged。
- no read-time governance activation。
- no correction execution or apply。

### Phase V1.6-E5: Quality Correction Rules Build Target HTTP Minimal Surface

状态：completed。

目标：只开放 correction-rules artifact build 的最小 target HTTP surface，不开放 correction apply，不新增 MCP tool、CLI command 或 CLI subcommand。

交付：

- E5 phase overlay：`public-surface-overlays/v1_6_e5.json`。
- `POST /api/workspaces/{workspace_id}/quality/correction-rules/build`。
- correction-rules artifact build stable projection。
- `test_target_http_quality_correction_rules_build.py` focused tests。
- E5 phase report。

验收：

- target HTTP current surface = 35 routes。
- MCP tool count = 40。
- CLI top-level / nested inventory unchanged。
- build is correction-rules artifact build, not quality build、workspace build、session build、correction plan build or correction apply。
- existing review statuses are preserved。
- correction plan unchanged; stale plan warning / next_action is returned when relevant。
- source/wiki/graph/session artifacts and operations unchanged。
- compatibility HTTP remains retained。

## Phase V1.6-F: Console Governance Evidence / Polish

目标：先完成 no-public-surface console governance evidence baseline，再让 `/knowledge` 更清楚地呈现服务治理状态和 V1.6 contract evidence。

### Phase V1.6-F1: Console Governance Evidence Baseline Sync

状态：completed。

交付：

- `console-governance-evidence-plan.md` matrix。
- `test_console_governance_evidence_plan.py` focused documentation guard。
- `current-vs-target-gap.md` and drawio route count / F1-F2 state sync。
- F1 phase report。

验收：

- V1.6-E5 accepted。
- target HTTP route count remains 35。
- MCP tool count remains 40。
- CLI top-level / nested diff = none。
- no new backend route。
- no frontend behavior change。
- `/knowledge` remains service governance console。
- F2 completed without backend public surface addition。

### Phase V1.6-F2: Console Governance Polish

状态：completed。

交付：

- public surface baseline view。
- target HTTP migration state view。
- graph/session/quality contract evidence view。
- accepted overlay summary。
- capability evidence table。
- service governance console wording。

验收：

- frontend build passes。
- page remains governance console, not end-user knowledge app。
- no backend public surface addition unless separately scoped and accepted。
- target HTTP route count remains 35。
- MCP tool count remains 40。
- CLI top-level / nested diff = none。

## Phase V1.6 Closure Acceptance / Final Release Audit

状态：completed。

目标：不新增能力，只做全量 public surface audit、API/MCP/CLI/frontend regression、文档一致性审计、drawio XML validation 和最终 V1.6 acceptance report。

边界：

- 不新增 backend public surface。
- 不新增 MCP tool。
- 不新增 CLI command 或 CLI subcommand。
- Closure 不新增 backend public surface，不修改功能代码，只完成最终公开面冻结审计、回归验收和文档同步。
