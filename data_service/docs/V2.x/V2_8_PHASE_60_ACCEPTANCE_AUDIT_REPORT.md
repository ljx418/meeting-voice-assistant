# V2.8 Phase 60 Acceptance Audit Report: Intent Evidence

> Generated from repository analysis and real-data validation.
> Business code was modified for V2.8 Phase 60 implementation.
> This report is an acceptance/audit record, not a PRD replacement.

## 1. Phase Scope

Phase 60 adds evidence-backed architecture intent states.

Implemented artifact:

- `architecture_intent_evidence.jsonl`

Intent state types:

- `documented_intent`
- `code_observed`
- `audit_accepted`
- `mismatch`
- `needs_review`

The phase explicitly avoids claiming that human design intent can be recovered from code alone.

## 2. Public Surface

### HTTP

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/intent`

### MCP

- `knowledge_code_architecture_intent_evidence_build`
- `knowledge_code_architecture_intent_evidence`

### CLI

- `knowledge code architecture intent-build`
- `knowledge code architecture intent`

## 3. Acceptance Evidence

| Command | Result |
| --- | --- |
| `pytest backend/tests/test_v2_8_reading_dashboard.py -q` | Passed as part of 9 focused tests |
| `pytest backend/tests/test_v2_8_reading_dashboard.py backend/tests/test_public_surface_guard.py -q` | Passed: 14 tests |
| `python3 -m py_compile ...` | Passed |
| `git diff --check -- ...` | Passed |

## 4. Real Repo E2E

### data_service

Input:

- Workspace root: `/private/tmp/data_service_v28_real_e2e/ws`
- Workspace id: `v28_real`
- Codebase id: `data_service_v28_real`

Observed:

```json
{
  "intent_count": 1440,
  "intent_types": {
    "audit_accepted": 240,
    "code_observed": 300,
    "documented_intent": 500,
    "mismatch": 400
  },
  "needs_review_intents": 400,
  "pure_code_human_intent_claimed": false
}
```

### HarnessOS

Input:

- Workspace root: `/private/tmp/harnessos_v28_real_e2e/ws`
- Workspace id: `harnessos_v28_real`
- Codebase id: `harnessos_v28_real`

Observed:

```json
{
  "intent_count": 1275,
  "intent_types": {
    "audit_accepted": 197,
    "documented_intent": 500,
    "mismatch": 400,
    "needs_review": 178
  },
  "needs_review_intents": 578,
  "pure_code_human_intent_claimed": false
}
```

HarnessOS lacks accepted code-observed intent rows in this run because its Phase 58 code fact chains lack deterministic line evidence. Those rows remain `needs_review`.

## 5. PRD / Spec Review

Confirmed:

- Every intent row has evidence refs, claim refs, code refs, audit refs, or `needs_review`.
- Documented intent, code-observed implementation, audit-accepted state, mismatch, and needs-review states remain separate.
- Drawio-only claims remain reviewable unless supported by other evidence.
- Public payloads do not leak local absolute paths.
- Output explicitly records `pure_code_human_intent_claimed = false`.

Not claimed:

- Complete design-intent recovery.
- Accepted code intent for targets without deterministic line evidence.
- Full runtime topology.

## 6. False-Green Review

Rejected false-green patterns:

- Code-observed implementation rows described as human design intent.
- Drawio-only statement promoted to accepted intent without supporting evidence.
- Intent rows with no supporting refs and no `needs_review`.
- HarnessOS unresolved chains hidden from output.
- Public payload leaks `/Users/Zhuanz` or `/private/tmp`.

No fatal or major false-acceptance risk remains for Phase 60.

## 7. Open Findings

| Severity | Finding | Status |
| --- | --- | --- |
| Minor | HarnessOS produces `needs_review` intent rows rather than accepted `code_observed` rows due missing line-level surface evidence. | Correct behavior; not a blocker. |

## 8. Phase 60 Decision

Phase 60 is accepted.
