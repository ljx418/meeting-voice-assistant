# V2 Phase 7 Acceptance Plan: Project Overview + Agent Context Pack

> Phase: 7 / Project Overview + Agent Context Pack.
> Status: pre-development acceptance plan.

## 1. Required E2E Flow

Use real repository data:

1. Create managed workspace in a temp root.
2. Import `/Users/Zhuanz/Desktop/workspace/data_service` as codebase.
3. Create Phase 2 snapshot.
4. Build Phase 3 inventory.
5. Build Phase 4 symbol index.
6. Build Phase 5 trace artifacts.
7. Read Phase 6 convergence envelopes.
8. Generate Project Overview.
9. Generate Agent Context Pack in `project_brief` mode.
10. Generate Agent Context Pack in `task_context` mode.
11. Read context pack by `pack_id`.
12. Inspect artifacts on disk.
13. Run V1/V2 regression tests.
14. Complete PRD/spec/audit review.

## 2. Required Artifacts

```text
workspace/assets/codebase/{codebase_id}/overview.json
workspace/assets/codebase/{codebase_id}/agent_context/{pack_id}.json
```

## 3. Project Overview Assertions

- contains `project_one_liner`
- contains entrypoints from snapshot/inventory
- contains public surface summary from inventory
- contains language stats and important paths from snapshot
- contains core modules from symbol/import evidence
- contains known risks or `needs_review`
- every important claim has evidence or `needs_review`
- public output does not leak absolute repo/workspace paths
- HTTP/MCP/CLI overview outputs agree on snapshot ID and major counts

## 4. Context Pack Assertions

Required modes:

- `project_brief`
- `task_context`

Required formats:

- `json`
- `markdown`

Required content:

- task interpretation for `task_context`
- relevant capabilities
- relevant public surface
- relevant files
- relevant symbols
- similar implementation patterns where evidence exists
- risks
- suggested tests
- recommended next steps
- evidence
- omitted items when budget or evidence rules remove content

Hard rules:

- every implementation guidance item has evidence or `needs_review`
- every risk has evidence or `needs_review`
- every suggested test has evidence or `needs_review`
- small token budget cannot retain guidance while dropping its evidence
- `pack_id` can be read back

## 5. Golden Tasks

Project reading task:

```text
请阅读并汇总当前项目的定位、入口、公开能力、核心模块、存储结构和证据。
```

Development task:

```text
新增一个 codebase MCP tool，并同步 HTTP API、CLI 和测试。
```

Both tasks must produce evidence-backed outputs.

## 6. HTTP Acceptance

Required routes:

```text
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/overview
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-pack
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent/context-packs/{pack_id}
```

Assertions:

- routes return V2 read envelope
- missing trace or symbol artifacts return controlled error with next actions
- no absolute path leaks

## 7. MCP Acceptance

Required tools:

```text
knowledge_project_overview
knowledge_agent_context_pack
```

Assertions:

- tools exist in `all_tool_specs()`
- outputs match HTTP/CLI stable fields
- `knowledge_agent_context_pack` supports `project_brief` and `task_context`

## 8. CLI Acceptance

Required commands:

```text
knowledge code overview
knowledge code context-pack
```

Assertions:

- stdout is valid JSON
- markdown output can be requested for context pack
- outputs match HTTP/MCP stable fields

## 9. Regression Suite

Minimum:

```bash
python3 -m pytest backend/tests/test_v2_project_overview.py
python3 -m pytest backend/tests/test_v2_agent_context_pack.py
python3 -m pytest backend/tests/test_v2_codebase_interface_convergence.py
python3 -m pytest backend/tests/test_v2_codebase_trace.py backend/tests/test_v2_codebase_symbols.py backend/tests/test_v2_codebase_inventory.py backend/tests/test_v2_codebase_snapshot.py
python3 -m pytest backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py backend/tests/test_session_ingest_query_build_contract_plan.py backend/tests/test_session_graphrag_contract.py backend/tests/test_target_http_session_query.py backend/tests/test_v16_closure_acceptance.py backend/tests/test_console_governance_evidence_plan.py
npm run build --prefix frontend
python3 -m pytest backend/tests
```

## 10. False Acceptance Checks

Fatal if any are true:

- overview is generated from prose without deterministic artifacts
- context pack guidance lacks evidence and is not marked `needs_review`
- small token budget drops evidence but keeps linked guidance
- project_brief and task_context are effectively identical
- pack cannot be read by `pack_id`
- output leaks absolute paths
- only mock repo is used
- V1 regression fails
