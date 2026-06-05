# V2.8 Phase 59-60 Ranking and Intent Specification

> Development, acceptance, and pre-implementation audit specification for Phase 59 and Phase 60.

## 1. Phase 59 Goal

Rank architecture signals and generate review queue v2 so large project reports emphasize high-value risks and evidence.

## 2. Phase 59 Required Implementation

- Build `architecture_signal_ranking.json`.
- Build `architecture_review_queue_v2.json`.
- Use default score weights from `V2_8_CODE_FACT_RANKING_INTENT_SPEC.md`.
- Pin major/fatal findings independent of score.

## 3. Phase 59 Acceptance

- top-N results are deterministic;
- score components and reason codes are visible;
- major/fatal findings appear in high-priority queue;
- weak evidence does not become accepted through high score.

## 4. Phase 60 Goal

Represent design intent as evidence-backed documented/code/audit/mismatch states, not as pure code-derived human intent.

## 5. Phase 60 Required Implementation

- Build `architecture_intent_evidence.jsonl`.
- Extend quality checks for:
  - target/current mixing;
  - missing acceptance gates;
  - superseded docs;
  - drawio without text support;
  - PRD vs target architecture conflict;
  - target architecture vs gap analysis conflict;
  - acceptance report vs actual artifact conflict.

## 6. Phase 60 Acceptance

- every intent row has evidence refs or `needs_review`;
- drawio-only intent remains reviewable unless supported by text/code evidence;
- conflicts are persisted and shown in report;
- no output claims pure code recovery of human design intent.

## 7. Pre-Implementation Audit

Before Phase 59:

- confirm severity enum;
- confirm reason code enum;
- confirm score formula.

Before Phase 60:

- confirm authority ordering for document types;
- confirm supersession/staleness fields;
- confirm conflict state schema.

## 8. False-Green Rejection

Reject acceptance if:

- ranking hides a major/fatal finding;
- score lacks reason codes;
- intent model merges documented target with code-observed implementation;
- drawio-only statement becomes accepted intent without supporting evidence.
