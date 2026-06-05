# V2.9 Phase 65 Package: Ranking Calibration v2

> Phase-specific development, acceptance, and pre-implementation audit package.

Date: 2026-06-05

## 1. Goal

Phase 65 reduces review queue noise while preserving visibility of major and fatal findings. Ranking changes must never convert weak evidence into accepted evidence.

## 2. Required Inputs

- Phase 63 evidence.
- Phase 64 relationships and clusters.
- V2.7 quality/alignment/reconstruction findings.
- V2.8 ranking, review queue, intent, and dashboard artifacts.

## 3. Output Artifacts

```text
workspace/assets/codebase/{codebase_id}/architecture/v2_9/
  architecture_signal_ranking_v2.json
  architecture_review_queue_v3.json
```

## 4. Score Components

Each ranking item must expose these components:

```text
severity
evidence_strength
relationship_depth
doc_code_drift
duplicate_group_size
staleness
human_priority
blocked_by_major_findings
```

The final score must include reason codes. A high score does not imply accepted evidence.

## 5. Grouping Policy

Findings may be grouped only when they share:

- finding type or close category;
- same capability or artifact family;
- overlapping evidence refs or same source artifact;
- same severity class or a safe severity rollup.

Grouping must preserve all evidence refs and source finding ids.

## 6. Pinning Invariant

```text
fatal and major findings must remain visible in the review queue.
Grouping cannot remove the last visible representative of a fatal or major finding.
Calibration cannot downgrade fatal/major severity.
```

## 7. Required Development Work

- Build v2 ranking from evidence, relationships, and prior quality/ranking artifacts.
- Emit grouping metrics:
  - input item count;
  - output group count;
  - duplicate reduction ratio;
  - major/fatal visible count;
  - input top-N major count;
  - output top-N major count;
  - hidden major count;
  - hidden fatal count;
  - low-confidence item count;
  - blocked item count.
- Emit review queue v3 with reason codes and score breakdown.
- Expose read/build via HTTP/MCP/CLI parity.

## 8. Acceptance Tests

- Duplicate grouping reduces top-N noise or explains why no reduction is possible.
- Every visible item has score components and reason codes.
- Fatal/major findings remain pinned and visible.
- `hidden_major_count = 0`.
- `hidden_fatal_count = 0`.
- No weak evidence item is promoted to accepted status.
- Grouped items retain all evidence refs.
- data_service and HarnessOS both produce ranking and review queue artifacts.
- Major/fatal items remain visible in Phase 66 report and Phase 67 context risk summaries.

## 9. False-Green Rejection

Reject Phase 65 if:

- ranking hides a major/fatal item;
- duplicate grouping removes evidence refs;
- weak/heuristic item becomes accepted evidence;
- score is opaque or lacks reason codes;
- HarnessOS noisy findings are suppressed without explanation;
- output cannot be compared with V2.8 baseline.

## 10. Phase 65 Audit Opinion

Planning status: ready after Phase 64 acceptance.

Open fatal findings: none.

Open major findings: none.

Required closure output:

```text
docs/V2.x/V2_9_PHASE_65_ACCEPTANCE_AUDIT_REPORT.md
```
