# V2 Phase 3 Development Plan: Public Surface Inventory

> Phase: 3 / Public Surface Inventory.
> Goal: extract deterministic HTTP / MCP / CLI / frontend / storage public surfaces from a codebase snapshot.
> Implementation must not start until `docs/V2.x/V2_PROJECT_INTELLIGENCE_PHASE_3_AUDIT_REPORT.md` has no open fatal or major findings.

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

## 8. Concrete Design

Phase 3 starts with a single module implementation to minimize moving parts. If the module grows beyond a maintainable boundary, split it into an `inventory/` package with the same responsibilities.

### 8.1 Service Boundary

Primary service:

```text
CodebaseInventoryService
```

Responsibilities:

- resolve codebase and snapshot artifacts
- load Phase 2 `snapshot.json` and `files.jsonl`
- run deterministic extractors
- normalize capabilities
- build alignment matrix
- persist inventory artifacts atomically
- read inventory artifacts for HTTP/MCP/CLI

The service must not rescan the filesystem outside the Phase 2 manifest except when reading source files already listed in `files.jsonl` for line evidence.

### 8.2 Data Models

`PublicSurface` fields:

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
- `extractor`
- `confidence`
- `unresolved_reason`

`CapabilityRecord` fields:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `capability_id`
- `name`
- `surface_ids`
- `surface_counts`
- `interfaces`
- `missing_interfaces`
- `unresolved_surface_ids`
- `confidence`

`InventorySummary` fields:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- `surface_counts`
- `capability_count`
- `unresolved_count`
- `unresolved_ratio`
- `golden_checks`
- `artifact_refs`

### 8.3 Extractor Strategy

HTTP extractor:

- Use runtime FastAPI route metadata for method/path/handler where available.
- Use source text scanning or AST to find route decorator lines and handler definition lines.
- Generate `surface_id = "http:{method}:{path}"`.
- Classify `/api/v1/knowledge/*` as `legacy`.
- Classify `/api/workspaces/...` and `/api/workspaces` as `target`.
- Mark framework/static/docs routes as `internal` or `best_effort` unless they are part of the data service public API.

MCP extractor:

- Use current MCP tool specs as the source of truth.
- Generate `surface_id = "mcp:{tool_name}"`.
- Count must equal `len(all_tool_specs())`.
- Source evidence should point to the module that defines the tool spec or handler if deterministic; otherwise record unresolved reason.

CLI extractor:

- Use parser construction helpers where possible.
- Include both package entry names when discoverable:
  - `data-service`
  - `knowledge`
- Generate `surface_id = "cli:{command path}"`.
- Include nested command paths such as `knowledge code import`.

Frontend extractor:

- Best effort only for V2.0.
- Record Vue pages and obvious API client references.
- Incomplete frontend extraction must not block Phase 3 if HTTP/MCP/CLI inventory passes.

### 8.4 Capability Normalization

Normalization must be deterministic. Initial golden mappings:

| Pattern | Capability |
| --- | --- |
| `codebase import`, `codebases`, `knowledge_codebase_import` | `codebase_import` |
| `codebase snapshot`, `snapshots`, `knowledge_codebase_snapshot` | `codebase_snapshot` |
| `source import`, `sources`, `knowledge_source_import` | `source_import` |
| `query`, `knowledge_query`, `knowledge_query_v2` | `query` |
| `build start/status/cancel`, `knowledge_build_*` | `build` |
| `quality`, `correction`, `low-signal` | `quality` |
| `graph`, `graphrag`, `neighbors`, `community` | `graph` |
| `source trace`, `trace source`, `knowledge_source_trace` | `source_trace` |
| `session` | `session` |

Ambiguous matches must remain unresolved rather than being forced into a capability.

### 8.5 HTTP/MCP/CLI Read Behavior

Inventory build and read behavior:

- If no explicit `snapshot_id` is provided, use latest snapshot from Phase 2.
- If artifacts do not exist, return a controlled error or `next_actions` instructing build.
- Reads must return stable `schema_version`, IDs, artifact refs, warnings, and unresolved summaries.
- Filters may include `surface_type` and `capability_id`; invalid filters must fail predictably.

### 8.6 Golden Check Output

`inventory_summary.json` must include `golden_checks`:

```json
{
  "http": {"passed": true, "missing": []},
  "mcp": {"passed": true, "missing": []},
  "cli": {"passed": true, "missing": []},
  "capabilities": {"passed": true, "missing": []}
}
```

Any missing golden sample fails Phase 3 acceptance.
