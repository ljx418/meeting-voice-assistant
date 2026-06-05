# V2.6 Gap Analysis: Large-Scale Architecture Abstraction Hardening

> Scope: gap from current V2.4 code-derived architecture inference to V2.6 large-project architecture abstraction hardening.
> Business code was not modified by this document.

Date: 2026-06-03

## 1. Summary

Current V2.4 can infer code-derived architecture roles, layers, boundaries, pattern candidates, and drift. That is enough for architecture abstraction MVPs, but not enough for reliable large-project audit and Agent consumption.

The V2.6 gap is engineering maturity:

- large outputs need scale profiling and summary-first reads;
- multi-language/config/deployment facts need first-class lightweight artifacts;
- taxonomy and confidence handling need a stable review queue;
- large-project views need to show key relationships without inventing architecture facts;
- Agent Context Pack needs safe architecture summaries that preserve evidence.

## 2. Current Capability Baseline

Confirmed capabilities before V2.6:

- codebase registry, snapshot, inventory, symbols, trace, overview, context pack;
- DevWiki, Code Graph, Quality Governance;
- code-derived architecture roles/layers/boundaries/patterns;
- architecture source parsing and design-code drift;
- HTML/Mermaid architecture views.

## 3. Gap Matrix

| Gap | Current State | V2.6 Target |
| --- | --- | --- |
| Large-project scale profile | No first-class scale profile | `architecture_scale_profile.json` |
| Artifact size governance | Large artifacts can be read directly | summary-first reads and artifact size stats |
| Lightweight TS/JS/Vue facts | Python facts are strongest | deterministic file/import/export/frontend hints |
| Config/deployment facts | Not first-class architecture inputs | config/deployment/schema inventory artifacts |
| Taxonomy governance | Role taxonomy exists in implementation docs | persisted default/override taxonomy |
| Review queue | Low-confidence items exist but are not a standalone workflow | `architecture_review_queue.jsonl` |
| Large-project view | Existing views can be too detailed | compact HTML/Mermaid views focused on key nodes |
| Context integration | Architecture can inform context indirectly | explicit architecture summary in Agent Context Pack |
| Large repo E2E | data_service E2E is primary | data_service + HarnessOS required |

## 4. Why V2.6 Is Needed

V2.4 can answer "what architecture can be inferred from code?".

V2.6 must answer:

- "Is this repo too large for raw artifact consumption?"
- "Which facts are reliable enough for Agent decisions?"
- "Which architecture claims need human review?"
- "Which config/deployment facts materially change the architecture view?"
- "Can the service summarize architecture safely for a large repo?"

## 5. Risks

| Risk | Severity | Mitigation |
| --- | --- | --- |
| Large-project view overclaims architecture | high | Render only persisted facts and mark confidence |
| Multi-language extractor becomes pseudo-static-analysis | high | Restrict to lightweight deterministic facts |
| Config inventory leaks secrets | high | Redact values and expose summaries only |
| HarnessOS validation becomes mock-only | high | Require real repo E2E |
| Context pack drops evidence under token pressure | high | Omit advice or mark `needs_review` when evidence is trimmed |
| Prior artifacts are mutated | medium | Hash gate V2.0-V2.5 artifacts |

## 6. Locked Product Decisions

These decisions are locked for V2.6 implementation. They should not be reopened during Phase 44-48 unless a fatal implementation blocker is found.

| Decision | V2.6 Default | Reason |
| --- | --- | --- |
| External large-repo validation target | HarnessOS is the only required external large project | Keeps V2.6 scope bounded while still testing a materially larger, non-self repo |
| Taxonomy override channel | Persisted artifact only | Avoids UI-only or request-only rules that cannot be audited |
| Low-confidence Agent Context Pack behavior | Exclude from actionable guidance by default; include only under `needs_review` | Prevents false architecture advice while preserving review visibility |
| Full static analysis semantics | Explicit non-claim | V2.6 is architecture abstraction hardening, not compiler/static-analysis replacement |
| HarnessOS unavailable | Stop for human review | Mock substitution would invalidate the large-project acceptance claim |

## 7. Remaining Questions for Implementation Time

These are operational checks, not product decisions:

- Confirm HarnessOS path is readable before Phase 44 implementation acceptance.
- Lock the exact hash-gate file list in the implementation PR.
- Record actual artifact ids and test commands in Phase 48 closure evidence.
