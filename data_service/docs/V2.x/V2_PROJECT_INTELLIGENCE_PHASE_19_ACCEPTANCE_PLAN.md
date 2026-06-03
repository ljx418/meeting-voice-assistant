# V2.4 Phase 19 Acceptance Plan: Code Role and Layer Inference

> Scope: acceptance for V2.4 Phase 19.
> Real repository validation is mandatory.

Date: 2026-06-02

## 1. Entry Criteria

- V2.4 target documents exist and define code-derived architecture inference.
- Phase 19 development plan exists.
- Phase 19 pre-development audit has no open fatal or major findings.
- V2.0/V2.1/V2.3 artifacts can be built or read for the current repo as needed.

## 2. Required Verification

Run focused tests:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_code_architecture_inference.py -q
```

Run regression tests:

```bash
PYTHONPATH=backend python3 -m pytest backend/tests/test_v2_architecture_abstraction.py backend/tests/test_data_service_mcp.py backend/tests/test_public_surface_guard.py -q
```

Run whitespace check:

```bash
git diff --check -- backend/data_service/code_assets backend/tests docs/V2.x
```

## 3. Real Repo E2E

Using `/Users/Zhuanz/Desktop/workspace/data_service`:

1. Import or reuse a codebase asset.
2. Build or reuse snapshot, inventory, symbols, and graph artifacts as required.
3. Build Phase 19 role/layer artifacts.
4. Read artifacts from disk.
5. Validate public payloads use repo-relative paths.
6. Validate prior V2 artifacts are not mutated unless explicitly rebuilt by the test setup.

## 4. Hard Assertions

The current `data_service` repo output must include:

- at least one `api_router` role;
- at least one `mcp_tooling` role;
- at least one `cli_tooling` role;
- at least one `frontend` role when frontend files are present;
- at least one `artifact_store` or `storage` role;
- at least one `governance` role when quality modules are present;
- at least one `test` role when tests are present;
- at least one `docs` role when docs are present;
- interface layer containing HTTP/MCP/CLI/frontend role members where present;
- governance layer containing governance role members where present;
- artifact or infrastructure layer containing artifact/storage role members where present.

Evidence assertions:

- Every role with `confidence >= 0.8` has at least one evidence item.
- At least 10 sampled evidence entries resolve to real repo-relative files and valid line ranges when line ranges are provided.
- Unknown roles include `needs_review`.
- Low-confidence roles do not count toward the hard role coverage assertions.

Artifact assertions:

- `code_roles.jsonl` exists and is non-empty.
- `code_layers.jsonl` exists and is non-empty.
- All records have `schema_version = v2.4`.
- All records include `workspace_id`, `codebase_id`, `snapshot_id`, stable IDs, evidence, signals, confidence, and `source_artifact_refs`.
- Public payloads do not contain absolute paths.

## 5. False Acceptance Rejection

Reject Phase 19 if:

- output is non-empty but misses all public interface roles;
- high-confidence roles lack evidence;
- `unknown` roles are counted as successful inference;
- implementation claims boundary inference, pattern detection, drift analysis, full call graph, data flow, control flow, runtime dispatch, or type inference;
- HTML/UI-only output is used as evidence;
- V2.0/V2.1/V2.3 artifacts are silently mutated;
- tests pass only on mock fixtures and not the real repo.

## 6. Exit Criteria

Phase 19 is accepted only when:

- focused tests pass;
- regression tests pass;
- real repo E2E passes;
- artifact inspection passes;
- PRD/spec review passes;
- false-acceptance review has no open fatal or major risk;
- Phase 19 audit report is updated with implementation evidence.
