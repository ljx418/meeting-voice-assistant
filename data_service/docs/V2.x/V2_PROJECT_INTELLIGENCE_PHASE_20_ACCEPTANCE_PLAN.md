# V2.4 Phase 20 Acceptance Plan: Boundary and Pattern Candidate Detection

> Scope: acceptance for V2.4 Phase 20.
> Real repository validation is mandatory.

Date: 2026-06-02

## 1. Required Verification

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

## 2. Hard Assertions

For the real `data_service` repo:

- `code_boundaries.jsonl` exists and is non-empty.
- `pattern_candidates.jsonl` exists and is non-empty.
- package boundaries exist for major project-intelligence packages.
- public-surface boundary exists when HTTP/MCP/CLI/frontend roles exist.
- governance boundary exists when quality roles exist.
- storage/artifact boundary exists when artifact roles exist.
- pattern candidates include FastAPI router, MCP registry, CLI command group, artifact store, quality gate, DevWiki, Code Graph, Context Pack, and architecture alignment where present.
- Every high-confidence boundary/pattern has evidence.
- Unsupported runtime claims are absent.
- HTTP/MCP/CLI pattern reads agree on stable IDs and counts.

## 3. False Acceptance Rejection

Reject Phase 20 if:

- patterns are inferred only from names without evidence;
- boundary output is empty but accepted;
- low-confidence candidates count as hard success;
- implementation claims full call graph/data flow/control flow/type inference;
- design-code drift is implemented before Phase 21;
- public payloads leak absolute paths.

## 4. Exit Criteria

Phase 20 is accepted only when focused tests, regression tests, real repo E2E, artifact inspection, PRD/spec review, and false-acceptance review pass with no open fatal or major finding.
