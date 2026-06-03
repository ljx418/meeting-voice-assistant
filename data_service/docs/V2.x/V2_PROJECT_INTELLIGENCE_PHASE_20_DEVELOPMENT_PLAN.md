# V2.4 Phase 20 Development Plan: Boundary and Pattern Candidate Detection

> Scope: V2.4 Phase 20 only.
> Baseline: Phase 19 code roles and layers are implemented and accepted.
> Phase 20 must not implement design-code drift or claim full call graph/data flow/control flow/type inference.

Date: 2026-06-02

## 1. Goal

Phase 20 adds deterministic architecture boundary and pattern candidate detection:

- infer coarse code boundaries from role clusters and paths;
- detect architecture pattern candidates from deterministic signals;
- persist `code_boundaries.jsonl` and `pattern_candidates.jsonl`;
- expose pattern reads through the architecture service with minimal public interface expansion.

## 2. Inputs

- Phase 19 roles and layers.
- V2.0 snapshot files.
- V2.0 public surface inventory.
- V2.0 symbols/imports.
- V2.1 Code Graph when present.

## 3. Implementation Design

Add focused modules:

- `boundary_inferer.py`: package, adapter, storage, governance, and public-surface boundary inference.
- `pattern_detector.py`: deterministic pattern candidate detection.

Extend:

- `artifacts.py`: add `code_boundaries.jsonl` and `pattern_candidates.jsonl` paths.
- `persistence.py`: write/read boundaries and patterns.
- `service.py`: include boundaries/patterns in V2.4 code architecture build/read.
- HTTP/MCP/CLI: add minimal `patterns` read endpoint/tool/command.

Allowed boundary types:

```text
package
bounded_context_candidate
adapter_boundary
governance_boundary
storage_boundary
public_surface_boundary
```

Allowed pattern types:

```text
fastapi_router
mcp_registry
cli_command_group
provider_adapter
artifact_store
pipeline
quality_gate
context_pack
devwiki
code_graph
architecture_alignment
```

## 4. Out of Scope

Phase 20 must not:

- compare design-side and code-derived models;
- generate design-code drift;
- implement full architecture HTML/Mermaid views;
- claim runtime behavior or complete static analysis;
- mutate V2.0/V2.1/V2.3 artifacts.

## 5. Expected Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/code_boundaries.jsonl
workspace/assets/codebase/{codebase_id}/architecture/pattern_candidates.jsonl
```

## 6. Implementation Gate

Phase 20 may enter implementation only if this plan, the Phase 20 acceptance plan, and the Phase 20 audit report exist and the audit report has no open fatal or major finding.
