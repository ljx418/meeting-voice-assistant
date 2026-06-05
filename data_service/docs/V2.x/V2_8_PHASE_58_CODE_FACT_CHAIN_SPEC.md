# V2.8 Phase 58 Code Fact Chain Specification

> Development, acceptance, and pre-implementation audit specification for Phase 58.

## 1. Goal

Add deeper deterministic code facts and guarded runtime boundary hints without claiming full static analysis.

## 2. Required Implementation

- Build `architecture_code_fact_chains.jsonl`.
- Build `architecture_runtime_boundaries.jsonl`.
- Extract:
  - HTTP route -> handler -> service/module chain;
  - MCP tool -> registry/dispatcher -> handler chain;
  - CLI command -> parser branch -> handler/service chain;
  - config/runtime/deployment boundary hints;
  - import dependency clusters;
  - test reference chains.

## 3. Deterministic Rules

Accepted chain requires:

- source file path;
- line range;
- source evidence snippet or evidence ref;
- deterministic relation type.

Deterministic relation types:

```text
registered_route
registered_mcp_tool
registered_cli_command
calls_local_service_direct
declared_config_boundary
test_references_symbol
```

Inferred relation types:

```text
imports_module
name_similarity
folder_proximity
doc_claim_similarity
```

Inferred relations must be `needs_review`.

## 4. Acceptance Gates

- sampled HTTP/MCP/CLI chains include valid line ranges;
- import edge alone is not labeled runtime call;
- runtime boundary hints have confidence and status;
- tests cover missing handler, dynamic registration, and unresolved chain paths.

## 5. Pre-Implementation Audit

Before implementation:

- confirm source symbol/surface artifacts exist;
- choose maximum traversal depth: default 2 service hops;
- confirm unresolved chain schema;
- confirm no full call graph claim.

## 6. False-Green Rejection

Reject Phase 58 if:

- import dependencies are presented as call graph;
- chain step lacks evidence;
- dynamic runtime behavior is accepted without evidence;
- line ranges are invalid.
