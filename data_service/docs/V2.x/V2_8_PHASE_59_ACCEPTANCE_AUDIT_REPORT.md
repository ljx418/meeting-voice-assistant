# V2.8 Phase 59 Acceptance Audit Report: Signal Ranking and Review Queue v2

> Generated from repository analysis and real-data validation.
> Business code was modified for V2.8 Phase 59 implementation.
> This report is an acceptance/audit record, not a PRD replacement.

## 1. Phase Scope

Phase 59 adds large-project architecture signal ranking and review queue v2.

Implemented artifacts:

- `architecture_signal_ranking.json`
- `architecture_review_queue_v2.json`

The phase ranks signals from document quality findings, doc-code drift, non-accepted alignments, graph clusters, code fact chains, and document authority review hints. It does not change the underlying V2.0-V2.7 facts and does not convert weak evidence into accepted evidence.

## 2. Public Surface

### HTTP

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/v2_8/ranking`

### MCP

- `knowledge_code_architecture_ranking_build`
- `knowledge_code_architecture_ranking`

### CLI

- `knowledge code architecture ranking-build`
- `knowledge code architecture ranking`

## 3. Acceptance Evidence

| Command | Result |
| --- | --- |
| `pytest backend/tests/test_v2_8_reading_dashboard.py -q` | Passed as part of 9 focused tests |
| `pytest backend/tests/test_v2_8_reading_dashboard.py backend/tests/test_public_surface_guard.py -q` | Passed: 14 tests |
| `pytest backend/tests/test_public_surface_guard.py -q` | Passed: 5 tests |
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
  "ranking_items": 300,
  "queue_items": 200,
  "pinned": 300,
  "weak_evidence_promoted": false
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
  "ranking_items": 300,
  "queue_items": 200,
  "pinned": 300,
  "weak_evidence_promoted": false
}
```

HarnessOS ranking is accepted as a prioritized review queue, not as proof that all HarnessOS architecture relationships are code-verified. Phase 58 line-evidence gaps remain visible through review items.

## 5. PRD / Spec Review

Confirmed:

- Top-N ranking is deterministic.
- Score components are exposed.
- Reason codes are exposed.
- Major/fatal findings are pinned independent of score.
- Weak evidence does not become accepted through high score.
- Public responses do not expose local absolute paths.

Not claimed:

- Full architecture correctness.
- Runtime call graph.
- Design intent recovery from code.
- Accepted evidence for unresolved HarnessOS chains.

## 6. False-Green Review

Rejected false-green patterns:

- Ranking hides major/fatal findings.
- Ranking items lack reason codes.
- Weak evidence is promoted to accepted state.
- HarnessOS unresolved code facts are treated as accepted architecture evidence.
- Public payload leaks `/Users/Zhuanz` or `/private/tmp`.

No fatal or major false-acceptance risk remains for Phase 59.

## 7. Open Findings

| Severity | Finding | Status |
| --- | --- | --- |
| Minor | Real data generated many pinned findings because current V2.7 quality/drift artifacts classify many items as major. | Accepted for ranking behavior; tuning can be addressed in future ranking calibration without blocking Phase 59. |

## 8. Phase 59 Decision

Phase 59 is accepted.
