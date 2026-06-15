# V2.40 Phase 117 Language Provider Development Plan

## 1. Scope

Phase 117 implements the multi-language AST/LSP provider contract required by V2.39-V2.45. It extends existing lightweight language inventory into provider-backed code facts while preserving evidence-first semantics.

This phase covers:

- `language_provider_status.jsonl`
- `symbol_facts.jsonl`
- `reference_facts.jsonl`
- Python AST provider as mandatory baseline
- TS/JS baseline extractor for fixture and real repo files
- tree-sitter / LSP as optional providers that return `provider_unavailable` unless configured

This phase does not implement full call graph, data flow, control flow, runtime topology, type inference, or production runtime tracing.

## 2. Inputs

- V2.39 scale profile and shard readback artifacts.
- Repo snapshot and `files.jsonl`.
- Existing Python symbol index where available.
- Existing V2.6 `language_facts.jsonl` as supporting input, not as replacement for provider facts.

## 3. Outputs

Artifacts are written under:

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_40/
```

Required files:

```text
language_provider_status.jsonl
symbol_facts.jsonl
reference_facts.jsonl
```

## 4. Provider Rules

Python AST:

- mandatory;
- must parse real Python files from data_service;
- syntax errors must be isolated per file;
- accepted symbol facts require repo-relative path and line range.

TS/JS baseline:

- must support a deterministic fixture;
- may use lexical/export/import extraction;
- accepted reference facts require repo-relative path and line range or clear source span.

tree-sitter / LSP:

- optional;
- if not configured, status must be `provider_unavailable`;
- provider health or name awareness must not be treated as executable support.

## 5. Public Contract

Planned read surfaces:

```text
HTTP:
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/language-providers

MCP:
knowledge_code_architecture_language_providers_build
knowledge_code_architecture_language_providers

CLI:
knowledge code architecture language-providers-build
knowledge code architecture language-providers
```

The public payload must use V2 envelope semantics and include stable counts, warnings, unresolved items, and artifact refs.

## 6. Implementation Steps

1. Add a focused provider module under `backend/data_service/code_assets/architecture/`.
2. Add artifact path helpers and read/write helpers.
3. Implement Python AST provider using stdlib `ast`.
4. Implement TS/JS baseline extractor without external runtime dependency.
5. Add optional provider status rows for tree-sitter and LSP.
6. Add service build/read methods.
7. Add HTTP/MCP/CLI read and build surfaces.
8. Add contract guard updates.
9. Add focused tests and real repo E2E.

## 7. Architecture Gates

- Do not add provider implementation into `backend/app/api/v1/data_service.py`.
- Do not add core provider logic into `backend/data_service/service.py`.
- Do not mark unavailable provider as accepted.
- Do not write HarnessOS-specific names into generic extractor code.
- Do not claim full call graph or runtime topology.
