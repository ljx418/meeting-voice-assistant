# V2 Phase 3 Development Plan: Public Surface Inventory

> Phase: 3 / Public Surface Inventory.
> Goal: extract deterministic HTTP / MCP / CLI / frontend / storage public surfaces from a codebase snapshot.
> Implementation must not start until `docs/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md` has no open fatal or major findings.

## 1. Scope

Phase 3 builds on Phase 2 snapshot artifacts and generates project public surface inventory artifacts.

In scope:

- read latest or explicit `snapshot_id`
- extract FastAPI / HTTP routes from source files and app route metadata
- extract MCP tools from `all_tool_specs()` and source tool specs
- extract CLI commands from the `knowledge` parser
- best-effort frontend page and API-call inventory
- storage/generated artifact inventory based on V2 artifact layout and existing storage modules
- deterministic `surface_id`
- capability taxonomy normalization
- alignment matrix for HTTP / MCP / CLI coverage
- unresolved records with reason and confidence
- golden surface assertions for V1 core and V2 codebase capabilities

Out of scope:

- Python symbol index
- surface-to-symbol mapping
- evidence trace beyond file/line source evidence for the extracted surface definition
- LLM summarization
- DevWiki
- Code Graph

## 2. Artifact Outputs

Required artifacts under the snapshot directory:

```text
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/capabilities.jsonl
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/alignment_matrix.json
workspace/assets/codebase/{codebase_id}/snapshots/{snapshot_id}/inventory_summary.json
```

Each artifact must include `schema_version`, `workspace_id`, `codebase_id`, and `snapshot_id`.

## 3. Public Surface Schema

Minimum `surfaces.jsonl` fields:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `surface_id`
- `surface_type`
- `name`
- `capability_id`
- `stability`
- `source_file`
- `line_range`
- `handler`
- `method`
- `route_path`
- `tool_name`
- `command`
- `input_schema`
- `output_schema`
- `confidence`
- `unresolved_reason`

`source_file` must be repo-relative. `line_range` must be present when deterministically available; otherwise `unresolved_reason` is required.

## 4. Capability Taxonomy

Capability IDs must be deterministic and normalized.

Golden capability IDs:

- `codebase_import`
- `codebase_snapshot`
- `source_import`
- `query`
- `build`
- `quality`
- `graph`
- `source_trace`
- `session`

Normalization rules:

- strip `knowledge_` prefix from MCP names before mapping
- collapse `*_v2` aliases to their underlying capability where applicable
- map route/action synonyms such as `sources/import`, `source_import`, and `knowledge_source_import` to `source_import`
- map `codebases/*/snapshots` and `knowledge_codebase_snapshot` to `codebase_snapshot`
- unresolved or ambiguous surfaces must not be silently merged

## 5. HTTP / MCP / CLI Exposure

Required HTTP:

```text
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/inventory
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/surfaces
GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/capabilities
```

Required MCP:

```text
knowledge_project_inventory
```

Required CLI:

```text
knowledge code inventory
```

## 6. Implementation Boundaries

- Implement extractors under `backend/data_service/code_assets/`.
- Extend `backend/app/api/v1/code_assets.py`; do not add Phase 3 routes to `backend/app/api/v1/data_service.py`.
- Extend `backend/data_service/mcp_code_tools.py`; do not create legacy wrappers.
- Extend `backend/data_service/cli_code.py`; do not move inventory logic into `backend/data_service/__main__.py`.
- Do not write to `lifecycle/sources.json`.
- Do not depend on LLM calls.

## 7. Expected Files To Add Or Touch

Expected new or modified areas:

- `backend/data_service/code_assets/inventory.py`
- `backend/data_service/code_assets/artifacts.py`
- `backend/app/api/v1/code_assets.py`
- `backend/data_service/mcp_code_tools.py`
- `backend/data_service/cli_code.py`
- `backend/tests/test_v2_codebase_inventory.py`
- contract tests that count MCP tools, target routes, CLI commands, and frontend contract entries
- `frontend/src/data/mcpContract.ts` if MCP contract is surfaced in the console

Any change to `backend/app/api/v1/data_service.py` or `backend/data_service/service.py` is a major audit finding unless explicitly approved.
