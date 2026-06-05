# V2.6 Artifact Schema and Public Contract

> Scope: schema and interface contract for V2.6 large-scale architecture abstraction hardening.
> Business code must not be changed by this document.

Date: 2026-06-03

## 1. Storage Root

All V2.6 artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/
```

Required files:

```text
architecture_scale_profile.json
language_facts.jsonl
config_inventory.jsonl
deployment_inventory.jsonl
schema_inventory.jsonl
architecture_taxonomy.json
architecture_review_queue.jsonl
views/architecture_large_project_overview.html
views/architecture_key_boundaries.mmd
```

V2.6 must not silently rewrite source registry, V2.0 snapshot/inventory/symbol/trace, V2.1 DevWiki/Graph/Quality, V2.4 architecture model, or V2.5 ResearchNotebook artifacts.

## 2. Shared Fields

Every JSON artifact must include:

```json
{
  "schema_version": "v2.6",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "created_at": "iso-8601",
  "source_artifact_refs": [],
  "evidence": [],
  "warnings": [],
  "redaction": {
    "applied": true,
    "redaction_count": 0
  }
}
```

JSONL records must include `schema_version`, stable id, repo-relative `path` when applicable, `confidence`, `evidence`, and `needs_review`.

## 3. ArchitectureScaleProfile

Required shape:

```json
{
  "schema_version": "v2.6",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "file_count": 0,
  "loc_total": 0,
  "language_distribution": {},
  "artifact_sizes": {},
  "build_durations": {},
  "warning_counts": {},
  "skipped_paths": [],
  "confidence_distribution": {
    "high": 0,
    "medium": 0,
    "low": 0,
    "needs_review": 0
  },
  "needs_review_count": 0,
  "summary_mode_required": false,
  "thresholds": {
    "summary_mode_file_count": 5000,
    "summary_mode_loc_total": 100000,
    "summary_mode_artifact_bytes": 1048576
  },
  "source_artifact_refs": [],
  "created_at": "iso-8601"
}
```

`summary_mode_required` is true when any threshold is exceeded or when raw artifact payloads would exceed the public response budget.

## 4. Inventory Records

### LanguageFactItem

```json
{
  "schema_version": "v2.6",
  "fact_id": "lang:{hash}",
  "fact_type": "import | export | api_client_hint | frontend_entrypoint | route_hint",
  "language": "typescript | javascript | vue",
  "path": "repo-relative/path",
  "name": "string",
  "signals": [],
  "evidence": [],
  "confidence": 0.8,
  "needs_review": false
}
```

Language facts are lightweight extractor hints. They must not claim full TypeScript semantics, complete dependency graphs, or runtime route resolution.

### ConfigInventoryItem

```json
{
  "schema_version": "v2.6",
  "item_id": "config:{path}:{key}",
  "item_type": "package_manifest",
  "path": "repo-relative/path",
  "key": "string",
  "value_summary": "redacted or summarized value",
  "signals": [],
  "evidence": [],
  "confidence": 0.8,
  "needs_review": false,
  "redaction": {
    "applied": true,
    "redaction_count": 0
  }
}
```

Allowed `item_type` values:

```text
package_manifest
python_project_config
container_config
compose_config
kubernetes_manifest
ci_workflow
env_example
openapi_like_schema
database_schema_hint
unknown_config
```

### DeploymentInventoryItem

```json
{
  "schema_version": "v2.6",
  "deployment_id": "deployment:{path}:{name}",
  "deployment_type": "dockerfile",
  "path": "repo-relative/path",
  "name": "string",
  "runtime_hint": "string",
  "service_hint": "string",
  "ports": [],
  "dependencies": [],
  "evidence": [],
  "confidence": 0.8,
  "needs_review": false
}
```

Allowed `deployment_type` values:

```text
dockerfile
docker_compose
kubernetes
github_actions
process_script
package_script
unknown_deployment
```

### SchemaInventoryItem

```json
{
  "schema_version": "v2.6",
  "schema_id": "schema:{path}",
  "schema_type": "openapi_like_schema",
  "path": "repo-relative/path",
  "name": "string",
  "signals": [],
  "evidence": [],
  "confidence": 0.7,
  "needs_review": true
}
```

Schema inventory is a lightweight detector. It must not claim schema completeness or runtime validation behavior.

## 5. Taxonomy and Review Queue

### ArchitectureTaxonomy

```json
{
  "schema_version": "v2.6",
  "taxonomy_id": "default",
  "role_types": ["interface", "application", "domain", "infrastructure", "governance", "runtime", "artifact", "test", "docs"],
  "layer_types": [],
  "boundary_types": [],
  "pattern_types": [],
  "confidence_thresholds": {
    "accepted_min": 0.8,
    "needs_review_below": 0.8
  },
  "override_source": null,
  "created_at": "iso-8601"
}
```

### ArchitectureReviewQueueItem

```json
{
  "schema_version": "v2.6",
  "review_id": "review:{target_type}:{target_id}:{reason}",
  "target_type": "role",
  "target_id": "string",
  "reason": "low_confidence",
  "severity": "major",
  "confidence": 0.5,
  "signals": [],
  "evidence": [],
  "recommended_action": "review before using as accepted architecture fact"
}
```

Allowed reasons:

```text
low_confidence
missing_evidence
unsupported_semantic_claim
conflicting_signals
large_artifact_summary_only
redacted_sensitive_value
unknown_config_type
```

## 6. HTTP / MCP / CLI Contract

V2.6 public reads use existing V2 success/error envelopes and must expose:

```json
{
  "ok": true,
  "schema_version": "v2.6",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "needs_review_count": 0,
  "next_actions": []
}
```

### HTTP Routes

Implementation must expose these routes from the existing architecture router:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/scale/profile
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/inventory/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-facts
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/config
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/deployment
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/schema
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/taxonomy
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/review-queue
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/views/{view_id}
```

### MCP Tools

Implementation must register these tools through the existing architecture MCP module:

```text
knowledge_code_architecture_scale_build
knowledge_code_architecture_scale_profile
knowledge_code_architecture_inventory_build
knowledge_code_architecture_language_facts
knowledge_code_architecture_config_inventory
knowledge_code_architecture_deployment_inventory
knowledge_code_architecture_schema_inventory
knowledge_code_architecture_taxonomy_build
knowledge_code_architecture_taxonomy
knowledge_code_architecture_review_queue_build
knowledge_code_architecture_review_queue
knowledge_code_architecture_large_project_views_build
knowledge_code_architecture_large_project_view
```

### CLI Commands

Implementation must expose these commands through the existing `knowledge code architecture` command group:

```text
knowledge code architecture scale-build
knowledge code architecture scale-profile
knowledge code architecture inventory-build
knowledge code architecture language-facts
knowledge code architecture config
knowledge code architecture deployment
knowledge code architecture schema
knowledge code architecture taxonomy-build
knowledge code architecture taxonomy
knowledge code architecture review-queue-build
knowledge code architecture review-queue
knowledge code architecture large-view-build
knowledge code architecture large-view
```

All CLI reads must default to JSON output and must not print local absolute paths.

Error responses must include stable `error.code` values:

```text
ARCHITECTURE_SCALE_PROFILE_NOT_BUILT
ARCHITECTURE_INVENTORY_NOT_BUILT
ARCHITECTURE_LANGUAGE_FACTS_NOT_BUILT
ARCHITECTURE_CONFIG_INVENTORY_NOT_BUILT
ARCHITECTURE_DEPLOYMENT_INVENTORY_NOT_BUILT
ARCHITECTURE_SCHEMA_INVENTORY_NOT_BUILT
ARCHITECTURE_TAXONOMY_NOT_BUILT
ARCHITECTURE_REVIEW_QUEUE_NOT_BUILT
ARCHITECTURE_VIEW_NOT_BUILT
V2_ARTIFACT_HASH_GATE_FAILED
V2_6_PREREQUISITE_NOT_FOUND
V2_6_HARNESSOS_UNAVAILABLE
```

HTTP, MCP, and CLI must agree on stable ids, counts, artifact refs, warning counts, unresolved counts, and needs_review counts.

## 7. Summary-first Public Payload Rules

Large or list-heavy artifacts must return summary-first payloads:

```json
{
  "counts": {},
  "sample": [],
  "artifact_refs": [],
  "truncated": true,
  "truncation_reason": "summary_mode_required"
}
```

Defaults:

- list samples are capped at 50 items unless an endpoint explicitly accepts a lower `limit`;
- raw JSONL artifacts are never embedded in full public responses;
- HTML/Mermaid view content can be returned only for the requested view id;
- if evidence is omitted from a public sample due to size, the sampled claim must be marked `needs_review` or the item must be omitted.

## 8. Stable Id Rules

Stable ids must be deterministic from repo-relative paths and semantic keys:

```text
scale_profile_id = scale:{workspace_id}:{codebase_id}:{snapshot_id}
config item_id = config:{path}:{item_type}:{key}
deployment_id = deployment:{path}:{deployment_type}:{name}
schema_id = schema:{path}:{schema_type}:{name}
taxonomy_id = taxonomy:{workspace_id}:{codebase_id}:default
review_id = review:{target_type}:{target_id}:{reason}
view_id = architecture_large_project_overview.html | architecture_key_boundaries.mmd
```

Generated timestamps must not be part of stable ids.

## 9. Prior Artifact Hash Gate

Phase 44-48 must capture before/after hashes for these artifacts when present:

```text
workspace/assets/codebase/{codebase_id}/codebase.json
workspace/assets/codebase/{codebase_id}/snapshots/latest
workspace/assets/codebase/{codebase_id}/surfaces.jsonl
workspace/assets/codebase/{codebase_id}/capabilities.jsonl
workspace/assets/codebase/{codebase_id}/symbols.jsonl
workspace/assets/codebase/{codebase_id}/imports.jsonl
workspace/assets/codebase/{codebase_id}/evidence.jsonl
workspace/assets/codebase/{codebase_id}/mappings.jsonl
workspace/assets/codebase/{codebase_id}/overview.json
workspace/assets/codebase/{codebase_id}/devwiki/index.json
workspace/assets/codebase/{codebase_id}/graph/graph.json
workspace/assets/codebase/{codebase_id}/architecture/architecture_model.json
workspace/assets/codebase/{codebase_id}/architecture/code_derived_architecture.json
```

If an artifact is absent before V2.6, record it as `missing_before`. V2.6 must not create missing V2.0-V2.5 artifacts as a side effect unless a documented prerequisite build is explicitly invoked before the hash-gate window.

## 10. Schema Validation Rules

Acceptance must validate:

- every required artifact exists after its build phase;
- JSON artifacts parse;
- JSONL artifacts parse line by line;
- every evidence path is repo-relative;
- every view id is known;
- every Mermaid node id maps to a persisted artifact id;
- every public response uses a V2 success/error envelope;
- every `accepted` fact has evidence or source artifact reference.

## 11. Redaction and Non-Claim Rules

Public payloads must not include:

- absolute local paths;
- raw `.env` values;
- API keys, tokens, secrets, authorization headers;
- raw provider secrets from V2.5 artifacts;
- traceback bodies;
- config values that match secret-like keys.

V2.6 must never mark these as accepted claims:

- full call graph;
- full data flow;
- full control flow;
- runtime dispatch resolution;
- compiler-grade type inference;
- complete recovery of human architecture design intent.
