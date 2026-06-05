# V2.7 Phase 49-55 Detailed Development and Acceptance Plan

> Detailed execution baseline for V2.7 implementation.
> Phase 49-55 are accepted; V2.7 closure is accepted for the current worktree.
> Each phase must use real `data_service` and HarnessOS inputs before acceptance.

Date: 2026-06-04

## 0. Phase Progress

| Phase | Status | Evidence |
| --- | --- | --- |
| Phase 49 Document Asset Registry | accepted | `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 50 Architecture Claim Extractor | accepted | `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 51 Document Quality Evaluation | accepted | `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 52 Doc-Code Alignment v2 | accepted | `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 53 Architecture Reconstruction Report | accepted | `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 54 Governance Integration | accepted | `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md` |
| Phase 55 Closure Acceptance | accepted | `V2_7_CLOSURE_AUDIT_REPORT.md` |

Do not claim full V2.7 completion until Phase 55 is accepted.

## 1. Execution Policy

V2.7 implementation must follow this sequence:

```text
Phase 49 Document Asset Registry
-> Phase 50 Architecture Claim Extractor
-> Phase 51 Document Quality Evaluation
-> Phase 52 Doc-Code Alignment v2
-> Phase 53 Architecture Reconstruction Report
-> Phase 54 Governance Integration
-> Phase 55 Closure Acceptance
```

No phase may start implementation until its pre-implementation audit closes all fatal and major findings. If a phase fails real-data E2E, it must return to planning and fix the implementation plan before continuing.

## 2. Phase 49 Pre-Gate

Before Phase 49 implementation starts:

- `docs/V2.x/V2_6_CLOSURE_AUDIT_REPORT.md` must exist.
- V2.6 scale, taxonomy, review queue, and view artifacts must be readable or a structured missing-artifact status must be documented.
- V2.7 must not rebuild V2.6 artifacts as a silent fallback.
- HarnessOS repo path must resolve exactly to `/Users/Zhuanz/Desktop/workspace/harnessOS`; if it is missing or case-mismatched, HarnessOS E2E cannot be accepted.
- V4/V6 HarnessOS document samples and drawio samples must be confirmed or marked `fixture_unavailable`.

## 3. Shared Implementation Boundaries

Implementation must extend focused architecture modules and keep interface files thin.

Preferred module additions:

```text
backend/data_service/code_assets/architecture/doc_registry.py
backend/data_service/code_assets/architecture/doc_claim_extractor.py
backend/data_service/code_assets/architecture/doc_quality.py
backend/data_service/code_assets/architecture/doc_code_alignment.py
backend/data_service/code_assets/architecture/doc_reconstruction.py
backend/data_service/code_assets/architecture/doc_views.py
backend/data_service/code_assets/architecture/doc_contracts.py
```

Interface modules may register HTTP/MCP/CLI entrypoints but must not hold extraction, scoring, alignment or rendering logic.

Do not silently mutate:

- source registry;
- V2.0 snapshot, inventory, symbols or trace artifacts;
- V2.1 DevWiki, graph or quality artifacts;
- V2.4 architecture model artifacts;
- V2.6 scale, taxonomy, review queue or view artifacts;
- original project documents.

Each phase must run a source artifact hash gate:

- record source registry hash;
- record original document hashes;
- record V2.0/V2.1/V2.4/V2.6 artifact hashes;
- run the phase;
- verify those hashes are unchanged unless the owning phase explicitly rebuilds them.

## 4. Shared Acceptance Commands

Exact commands may be adjusted during implementation, but each phase must provide equivalents for:

```text
python -m pytest backend/tests/test_v2_7_*.py
python -m pytest backend/tests/test_public_surface_guard.py
python -m pytest backend/tests/test_v2_6_architecture_scale_profile.py
git diff --check -- .
```

Each phase must also run real-repo E2E against:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

## 5. Phase 49: Document Asset Registry

### Goal

Register project architecture documents as governed assets with stable IDs, document type, phase/version hints, scope, stale hints and evidence.

### Status

Accepted.

Acceptance evidence:

- `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md`
- `data_service`: 318 document assets
- HarnessOS: 628 document assets
- HTTP/MCP/CLI contract tests passed
- snapshot regression passed after adding `.drawio` and `.mmd` default scan support

### Required implementation

- Discover architecture-relevant Markdown, drawio, mermaid and matrix-like files from the existing codebase snapshot.
- Classify documents into:
  - `prd`
  - `target_architecture`
  - `gap_analysis`
  - `drawio`
  - `development_plan`
  - `acceptance_plan`
  - `audit_report`
  - `api_matrix`
  - `handoff_summary`
  - `readme`
  - `unknown_architecture_doc`
- Assign authority metadata:
  - `authority_role`: `target`, `implementation_plan`, `acceptance_result`, `audit_status`, `historical_reference`, or `unknown`;
  - `authority_level`: `primary`, `supporting`, `historical`, or `weak`;
  - `supersedes`;
  - `superseded_by`.
- Persist:
  - `architecture_docs.jsonl`
  - `architecture_doc_sources.jsonl`
- Add read paths through HTTP/MCP/CLI if not already covered by the build response.

### Golden assertions

For `data_service`:

- V2.7 PRD, target architecture, gap analysis, detailed plan, artifact contract, E2E matrix and drawio are discovered.
- V2.0-V2.6 prior documents are not overwritten or reclassified as V2.7 authority.
- `V2_5_*` and `V2_6_*` documents are registered as historical or supporting authority, not V2.7 current target authority.

For HarnessOS:

- at least one V4 design document is discovered;
- at least one V6 target architecture or roadmap document is discovered;
- at least one drawio document is discovered when present.

### Acceptance

- document registry is non-empty for both repos;
- every row has `doc_id`, `doc_type`, `path`, `phase_hint`, `version_hint`, `scope_hint`, `evidence`, `confidence` and `needs_review`;
- every row has `authority_role`, `authority_level`, `supersedes`, and `superseded_by`;
- no public output leaks absolute paths;
- repeated run on the same snapshot produces stable IDs and counts.

### Rejection

- empty registry accepted;
- filename-only classification accepted with high confidence;
- historical docs promoted to current target authority without supersession evidence;
- source registry or prior V2 artifacts changed.

## 6. Phase 50: Architecture Claim Extractor

### Goal

Extract claim-level architecture facts and relations from registered documents.

### Required implementation

- Extend Markdown extraction beyond headings:
  - headings;
  - bullets and numbered lists;
  - simple tables;
  - acceptance criteria;
  - non-goals;
  - stop conditions;
  - interface lists.
- Extend drawio extraction:
  - nodes become document claims;
  - edges become document relations;
  - style/status hints are preserved;
  - copied diagram elements are marked as `source=document_claim`.
- Record claim block provenance:
  - `source_block_type`;
  - `drawio_cell_id`;
  - `drawio_diagram_id`;
  - `line_range` when available.
- Enforce confidence ceilings:
  - explicit heading/table/API matrix claim: <= 0.90;
  - explicit acceptance gate/non-goal/forbidden claim: <= 0.90;
  - Markdown bullet/list claim: <= 0.80;
  - drawio node only: <= 0.70;
  - drawio edge without explicit relation label: <= 0.65;
  - inferred claim: <= 0.60 and `needs_review`.
- Persist:
  - `architecture_doc_claims.jsonl`
  - `architecture_doc_relations.jsonl`

### Golden assertions

For HarnessOS:

- V4 headless workflow chain is represented as ordered or connected claims when source docs exist.
- V6 target architecture planes are extracted as `plane` or `layer` claims when source docs exist.
- governance, policy, runtime, provider or external app claims are classified when source text supports them.

For `data_service`:

- V2.7 target components are extracted:
  - Document Asset Registry;
  - Architecture Claim Extractor;
  - Document Quality Evaluator;
  - Doc-Code Alignment v2;
  - Reconstructed Architecture Model;
  - Governance Overlay.

### Acceptance

- claim and relation artifacts are non-empty for both repos;
- every accepted claim has document evidence;
- every relation has source document evidence or `needs_review`;
- weak/inferred claims are not accepted as high confidence.

### Rejection

- copied drawio shown as code-inferred architecture;
- LLM-only claim without evidence accepted;
- claims lack `doc_id` or source path.
- non-goal or forbidden claim is dropped instead of represented as a first-class claim.

## 7. Phase 51: Document Quality Evaluation

### Goal

Evaluate quality, consistency, freshness and acceptance coverage of architecture documents.

### Required implementation

- Build document quality checks:
  - missing acceptance gate;
  - missing evidence;
  - stale document;
  - scope conflict;
  - status conflict;
  - unsupported claim;
  - ambiguous ownership;
  - missing current/target split;
  - overbroad architecture claim.
- Persist:
  - `architecture_doc_quality_findings.jsonl`
  - `architecture_doc_quality_summary.json`

### Golden assertions

For `data_service`:

- V2.7 docs are recognized as planning docs, not implementation evidence.
- V2.7 document audit is recognized as external-review-ready, not closure evidence.

For HarnessOS:

- if a document says accepted but lacks evidence inventory, quality evaluator emits a finding or `needs_review`;
- if a target architecture document does not map to current code evidence yet, it is not treated as implemented.

### Acceptance

- quality summary includes document count, claim count, finding count, severity counts and needs_review count;
- if any fatal or major finding exists, `overall_status` cannot be `high_quality`;
- findings include evidence and recommended action;
- no document is marked high quality without coverage checks.

### Rejection

- quality score hides high-severity finding;
- planning-ready is treated as implemented;
- findings are generated without evidence or target IDs;
- all documents marked accepted by default.

## 8. Phase 52: Doc-Code Alignment v2

### Goal

Compare document claims against deterministic code facts and prior architecture artifacts.

### Required implementation

- Match claims to:
  - V2.0 public surfaces, symbols and evidence;
  - V2.1 graph nodes and edges;
  - V2.4 roles, layers, boundaries, patterns and drift findings;
  - V2.6 scale, lightweight language/config/deployment/schema facts and review queue.
- Persist:
  - `architecture_doc_code_alignment.jsonl`
  - `architecture_doc_code_drift_v2.jsonl`
- Emit both claim-to-code and code-to-document coverage.

### Match policy

Accepted match requires:

- document evidence;
- code evidence;
- match strategy stronger than token overlap alone;
- confidence at or above configured accepted threshold;
- no blocking `needs_review`.

Token overlap may create `weak_match` only.

Configured thresholds and strategies:

```text
accepted_match_confidence_min = 0.80
weak_match_confidence_range = 0.40 - 0.79
token_overlap_only -> weak_match only
```

Allowed `match_strategy` values:

```text
exact_surface_id
exact_symbol_id
artifact_ref_match
capability_id_match
path_and_line_evidence_match
graph_node_id_match
v24_role_boundary_match
v26_taxonomy_match
manual_reviewed
token_overlap_only
```

### Golden assertions

For `data_service`:

- V2.7 public interfaces in target docs map to implemented public surfaces only after code exists;
- before code exists, they remain `designed_not_found_in_code` or planned.

For HarnessOS:

- target architecture planes may map to modules/components only when code evidence exists;
- code-only components not covered by documents appear as `code_not_documented`.

### Acceptance

- non-empty alignment and drift artifacts for both repos;
- accepted rows contain document and code evidence;
- code-to-document coverage summary is present even if no findings exist;
- weak rows remain visible;
- repeated run on same snapshot is stable.

### Rejection

- token-only match accepted;
- no code evidence accepted;
- low-confidence match counted as implemented.

## 9. Phase 53: Architecture Reconstruction Report

### Goal

Generate target/current/diff architecture model and readable visual reports.

### Required implementation

- Build:
  - target nodes from document claims;
  - current nodes from code facts and V2.4/V2.6 artifacts;
  - diff nodes from alignment and quality findings.
- Persist:
  - `architecture_reconstructed_model.json`
  - `views/document_code_architecture_report.html`
  - `views/document_code_architecture_diff.mmd`

### Golden assertions

- HTML contains three visible sections:
  - Target Architecture from Documents;
  - Current Architecture from Code;
  - Gaps and Drift.
- Mermaid node IDs map to persisted model nodes.
- Original drawio labels appear only as document-derived nodes, never code-inferred nodes.
- HTML text is escaped and links are sanitized.
- Mermaid node IDs are generated from artifact IDs, and labels are escaped.
- Every rendered node resolves to `architecture_reconstructed_model.json`.

### Acceptance

- HTML and Mermaid are non-empty for both repos;
- all high-level nodes have source refs;
- unresolved and low-confidence items remain visible;
- no absolute path leak.
- no raw script injection or Mermaid label injection.

### Rejection

- generated view introduces architecture facts not in persisted artifacts;
- copied drawio used as reconstructed code architecture;
- target/current/diff not visually separated.
- rendered node is not present in the reconstructed model.

## 10. Phase 54: Governance Integration

### Goal

Integrate V2.7 findings into quality governance.

### Required implementation

- Add quality target support for:
  - `architecture_doc`;
  - `architecture_doc_claim`;
  - `architecture_doc_relation`;
  - `architecture_doc_quality_finding`;
  - `architecture_doc_code_alignment`;
  - `architecture_reconstructed_node`;
  - `architecture_reconstructed_edge`.
- Feedback, rule generation, review and correction plan must work for these targets.
- Approved rules apply as read-time overlay only.

### Golden assertions

- Feedback can be recorded for one document claim and one alignment mismatch.
- Rule can be generated and approved.
- Approved rule appears in read output as `applied_rules`.
- Original artifacts hash is unchanged.
- Revoked rule no longer appears in governed read output.

### Acceptance

- governance operations pass focused tests;
- summary includes V2.7 target counts;
- revoke stops read-time application.

### Rejection

- quality rule mutates source document or code artifact;
- target resolver accepts missing target IDs;
- read output hides applied governance state.

## 11. Cross-Link Integrity Gate

Starting in Phase 50 and required for closure:

- every `doc_id` in claims, relations, findings, alignments and reconstructed model resolves to `architecture_docs.jsonl`;
- every `claim_id` in relations, findings and alignments resolves to `architecture_doc_claims.jsonl`;
- every relation endpoint resolves;
- every accepted alignment `code_ref` resolves to a persisted code or architecture artifact;
- every reconstructed node references a document claim, code fact, or explicitly marked inference;
- every rendered view node exists in `architecture_reconstructed_model.json`.

## 12. Phase 55: Closure Acceptance

### Goal

Complete V2.7 PRD coverage and closure audit.

### Required implementation

- Fill `V2_7_FULL_PRD_COVERAGE_MATRIX.md` with actual implementation evidence.
- Create `V2_7_CLOSURE_AUDIT_REPORT.md`.
- Run full real-repo E2E.

### Acceptance

- every PRD item is classified:
  - `accepted`;
  - `conditionally_accepted`;
  - `not_implemented`;
  - `out_of_scope`.
- accepted rows cite tests and artifact evidence;
- no open fatal or major finding;
- business-code implementation is traceable to approved phase plan.

### Rejection

- coverage row accepted without evidence;
- skipped real-repo E2E counted as pass;
- V2.7 claims complete architecture intent recovery from code alone.
- coverage matrix lacks cross-link and hash-gate evidence.

## 13. Required ChatGPT Audit Package

Use this compact package for external audit. Phase-specific documents are indexed in `README.md`; they do not all need to be included in the compact package unless the reviewer requests a deeper phase-by-phase audit.

```text
docs/V2.x/V2_7_TARGET_PRD.md
docs/V2.x/V2_7_TARGET_ARCHITECTURE.md
docs/V2.x/V2_7_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_7_PHASE_49_55_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_7_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md
docs/V2.x/V2_7_GAP_ANALYSIS.md
docs/V2.x/V2_7_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md
docs/V2.x/V2_7_FULL_PRD_COVERAGE_MATRIX.md
docs/V2.x/V2_7_DOCUMENT_AUDIT_REPORT.md
docs/V2.x/V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_7_PHASE_50_DEVELOPMENT_PLAN.md
docs/V2.x/V2_7_PHASE_50_ACCEPTANCE_PLAN.md
docs/V2.x/V2_7_PHASE_50_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_7_TARGET_STATE.drawio
```
