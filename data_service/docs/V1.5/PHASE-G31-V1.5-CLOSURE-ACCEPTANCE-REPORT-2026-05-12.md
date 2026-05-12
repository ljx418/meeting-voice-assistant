# PhaseG31 V1.5 Closure Acceptance Report

日期：2026-05-12

## 1. Scope

PhaseG31 是 V1.5 的 closure and acceptance phase，只做验收、审计、文档一致性检查和总结报告。

本阶段不引入新的 capability surface：

- 不新增 MCP tool。
- 不新增 HTTP route。
- 不新增 CLI command。
- 不新增 graph neighbors/community/query/session 能力。
- 不新增 workspace/source/build 写入型 target HTTP route。
- 不新增 graph advanced / quality write / session target HTTP route。
- 不删除或破坏旧 `/api/v1/knowledge/*` 兼容入口。

目标口号：Freeze the surface, prove the contracts, close V1.5.

## 2. Project Positioning

`data_service` 仍然是 MCP-first local knowledge governance microservice，不是 end-user knowledge consumption app。

服务边界保持不变：

- MCP 是默认主入口。
- CLI 使用 `knowledge ...` 作为面向人的操作入口。
- HTTP 保留旧 `/api/v1/knowledge/*` 兼容入口，并已开放首批 `/api/workspaces/{workspace_id}/...` target HTTP。
- `data_service` 负责 workspace/source/build lifecycle、query/distill/trace/quality shared contracts、operation/envelope/error contract。
- `app.llmwiki` 负责 readable wiki artifacts。
- `app.graphrag.service` 负责 GraphRAG、session graph 和 relation extraction。
- `/knowledge` 仍是 service governance console，不是终端用户知识消费 App。

## 3. Public Surface Audit

### MCP

- PhaseG31 前 MCP tool count：`40`。
- PhaseG31 后 MCP tool count：`40`。
- New tools：none。
- 结论：PhaseG31 未新增 MCP tool。

### CLI

- PhaseG31 前 CLI top-level commands：`build / graph / quality / query / source / trace / workspace`。
- PhaseG31 后 CLI top-level commands：`build / graph / quality / query / source / trace / workspace`。
- New commands：none。
- 结论：PhaseG31 未新增 CLI command。

### HTTP

`/api/v1/knowledge/*` compatibility routes retained。

target HTTP 当前只开放：

- `POST /api/workspaces/{workspace_id}/query`
- `POST /api/workspaces/{workspace_id}/distill`
- `GET /api/workspaces/{workspace_id}/sources/{source_id}/trace`

New target routes in PhaseG31：none。

未开放能力保持未开放：

- `knowledge graph neighbors/community/query/session`
- workspace/source/build 写入型 target HTTP route
- graph advanced target HTTP route
- quality 写入型 target HTTP route
- session target HTTP route

## 4. Contract Consistency Audit

- Query contract：`knowledge_query` / `data_service query` / `knowledge query` / `/api/v1/knowledge/query` / `/api/workspaces/{workspace_id}/query` 复用 `run_query_contract`，payload contract 一致。
- Distill contract：`knowledge_distill_preview` / `data_service distill` / `/api/v1/knowledge/distill` / `/api/workspaces/{workspace_id}/distill` 复用 `run_distill_contract`，payload contract 一致。
- Trace contract：`knowledge_source_trace` / `knowledge trace source` / `/api/v1/knowledge/source/trace` / `/api/workspaces/{workspace_id}/sources/{source_id}/trace` 复用 `source_trace_payload`，payload contract 一致。
- Envelope/error contract：MCP 和 HTTP lifecycle envelope 继续复用 `data_service.mcp_common` 的 sanitizer 与 error normalization。
- `artifact_ref` consistency：外部 lifecycle payload 使用 `artifact_ref` / `artifact_refs` 表达稳定 artifact 引用。
- Stable ID contract：外部 contract 依赖 `workspace_id`、`source_id`、`session_id`、`operation_id`、`artifact_ref` 等稳定字段。
- Internal path contract：内部 workspace path/layout 仅作为 debug / console / compat 信息；`debug_path`、`debug_paths` 和兼容 `workspace` path 不是稳定外部 contract。

## 5. Regression Results

- API regression：`34 passed`。
- MCP regression：`32 passed`。
- Combined data_service/API/MCP regression：`137 passed`。
- Frontend build：`npm run build` passed。
- Drawio XML validation：`docs/V1.5/current-vs-target-gap.drawio` 与 `docs/V1.5/data-service-v1.5-roadmap.drawio` parsed successfully。
- Frontend screenshot acceptance：
  - `docs/V1.5/frontend-acceptance/data_service_phaseg31_default.png`
  - `docs/V1.5/frontend-acceptance/data_service_phaseg31_mcp.png`
  - `docs/V1.5/frontend-acceptance/data_service_phaseg31_graph.png`

## 6. Documentation Consistency

Checked documents:

- `docs/V1.5/current-vs-target-gap.md`
- `docs/V1.5/current-vs-target-gap.drawio`
- `docs/V1.5/data-service-v1.5-roadmap.drawio`
- `docs/V1.5/interface-convergence-matrix.md`
- `docs/V1.5/target-http-routes-contract.md`
- `docs/V1.5/source-trace-contract.md`
- `docs/V1.5/trace-cli-contract.md`
- `docs/V1.5/quality-contract.md`
- `docs/V1.5/graph-cli-contract.md`
- `docs/V1.5/README.md`
- `docs/V1.5/PHASE-G24-G31-REMAINING-DEVELOPMENT-PLAN-2026-05-12.md`
- `docs/V1.5/PHASE-G30-TARGET-HTTP-ROUTES-REPORT-2026-05-12.md`

Consistency conclusions:

- Phase status is consistent：PhaseG30 completed；PhaseG31 is V1.5 closure acceptance。
- Target HTTP scope is consistent：currently exposes exactly 3 routes, query / distill / source trace。
- Compatibility route status is consistent：old `/api/v1/knowledge/*` remains retained。
- MCP tool count is consistent：PhaseG31 remains at `40` tools。
- CLI top-level command surface is consistent：no PhaseG31 CLI expansion。
- V1.6 candidate scope is documented only, not implemented in PhaseG31。

## 7. Boundary Audit

- No new dependency on upper-layer application modules：no production dependency was added for meeting, ASR, interview, learning, IDE plugin, or upper-layer Agent workflow modules.
- Meeting transcripts and code analysis artifacts remain accepted input shapes only; they are not production dependencies on upper-layer apps.
- External contracts rely on stable IDs and artifact references.
- Internal paths remain debug/console-only or legacy compatibility fields, not stable contract identity.
- `/knowledge` remains a service governance console.
- `data_service` remains the minimum separable unit for local knowledge governance service.

## 8. V1.6 Candidates

V1.6 candidates are documented only. They are not implemented in PhaseG31.

Candidates:

- graph neighbors/community/query/session
- workspace/source/build target HTTP write routes
- graph advanced target HTTP routes
- quality write target HTTP routes
- session target HTTP routes
- session GraphRAG public contract
- artifact_ref normalization hardening
- operation lifecycle consistency hardening
- console governance polish

## 9. Final Decision

V1.5 closure status：accepted。

Blocking issues：none.

V1.5 已完成收口，下一步进入 V1.6 planning。

Final principle:

- 不加能力。
- 不扩公开面。
- 不破兼容入口。
- 不改微服务边界。
- 不让 `/knowledge` 重新变成终端 App。
- 只做验收、审计、文档一致性和总结报告。
