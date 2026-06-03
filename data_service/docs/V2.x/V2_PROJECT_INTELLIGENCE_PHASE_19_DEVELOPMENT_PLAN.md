# V2.4 Phase 19 Development Plan: Code Role and Layer Inference

> Scope: V2.4 Phase 19 only.
> Business code may be modified after this plan and its audit gate are accepted.
> Phase 19 must not implement boundary inference, pattern detection, design-code drift, or new public routes beyond read/build support needed for roles and layers.

Date: 2026-06-02

## 1. Goal

Phase 19 adds the first code-derived architecture inference capability:

- classify code artifacts into architecture roles;
- infer coarse architecture layers from those roles;
- persist `code_roles.jsonl` and `code_layers.jsonl`;
- expose the result through existing architecture service surfaces if minimal and non-invasive;
- validate with the real `data_service` repository.

## 2. Inputs

Required inputs:

- V2.0 snapshot metadata and file manifest.
- V2.0 public surface inventory.
- V2.0 Python symbols and imports.
- V2.1 code graph when available.
- V2.3 architecture artifacts when available, but Phase 19 must work without design sources.

## 3. Implementation Design

Add focused modules under `backend/data_service/code_assets/architecture/`:

- `code_model.py`: V2.4 schema constants and factory helpers for roles/layers.
- `role_classifier.py`: deterministic role classifier for files, surfaces, and symbols.
- `layer_inferer.py`: layer inference from role records.

Extend existing helpers:

- `backend/data_service/code_assets/artifacts.py`: add paths for `code_roles.jsonl` and `code_layers.jsonl`.
- `backend/data_service/code_assets/architecture/persistence.py`: write/read V2.4 role/layer artifacts.
- `backend/data_service/code_assets/architecture/service.py`: add `build_code_architecture` and `read_code_architecture_roles_layers`.

Allowed role types:

```text
api_router
mcp_tooling
cli_tooling
frontend
service
domain
runtime
provider
storage
policy
governance
build_pipeline
artifact_store
test
script
docs
unknown
```

Allowed layer types:

```text
interface
application
domain
infrastructure
governance
runtime
artifact
test
docs
unknown
```

Role inference signals:

- HTTP surfaces imply `api_router`.
- MCP surfaces or MCP registry/tool modules imply `mcp_tooling`.
- CLI surfaces or CLI helper modules imply `cli_tooling`.
- frontend files imply `frontend`.
- persistence/artifact path modules imply `artifact_store` or `storage`.
- quality modules imply `governance`.
- graph/devwiki/context/overview/inventory/symbol/trace modules imply service roles.
- tests imply `test`.
- docs/Markdown imply `docs`.
- scripts imply `script`.

High-confidence role records require evidence. Unknown and low-confidence records must be explicit and must not count as successful architecture recognition.

## 4. Out of Scope

Phase 19 must not:

- infer bounded contexts or architecture boundaries;
- detect architecture patterns;
- compare design model and code-derived model;
- claim full call graph, data flow, control flow, runtime dispatch, or type inference;
- mutate V2.0/V2.1/V2.3 artifacts;
- add V2.4 core logic to `backend/data_service/service.py`;
- add V2.4 routes to `backend/app/api/v1/data_service.py`.

## 5. Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/code_roles.jsonl
workspace/assets/codebase/{codebase_id}/architecture/code_layers.jsonl
```

Each role/layer record must include:

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- stable ID
- type
- evidence
- signals
- confidence
- `needs_review`
- `source_artifact_refs`

## 6. Implementation Gate

Phase 19 implementation may start only if:

- this development plan exists;
- the Phase 19 acceptance plan exists;
- the Phase 19 audit report has no open fatal or major finding;
- no high-risk architecture expansion is required.
