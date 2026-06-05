# V2.7 Development and Acceptance Plan

> V2.7 Phase 49, Phase 50, Phase 51, Phase 52, Phase 53, Phase 54, and Phase 55 are accepted.
> V2.7 closure is accepted for the current worktree.
> Each implementation phase must complete pre-implementation audit, real-data E2E, PRD/spec review, and false-acceptance review.

Date: 2026-06-04

## 0. Current Phase Status

Accepted:

- Phase 49 Document Asset Registry.
- Phase 50 Architecture Claim Extractor.
- Phase 51 Document Quality Evaluation.
- Phase 52 Doc-Code Alignment v2.
- Phase 53 Architecture Reconstruction Report.
- Phase 54 Governance Integration.
- Phase 55 Closure Acceptance.

Evidence:

- `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_7_CLOSURE_AUDIT_REPORT.md`
- `backend/tests/test_v2_7_document_registry.py`
- real `data_service` registry: 318 document assets
- real HarnessOS registry: 628 document assets
- real `data_service` claims: 20085 claims and 16704 relations
- real HarnessOS claims: 18367 claims and 13476 relations
- real `data_service` quality: 988 findings, overall_status `needs_review`
- real HarnessOS quality: 1621 findings, overall_status `needs_review`
- real `data_service` alignment: 20827 rows, 13478 drift rows, 7349 matched rows
- real HarnessOS alignment: 18635 rows, 13989 drift rows, 4646 matched rows
- real `data_service` reconstruction: 180 target nodes, 180 current nodes, 220 diff nodes, 81 edges, HTML and Mermaid generated
- real HarnessOS reconstruction: 180 target nodes, 180 current nodes, 220 diff nodes, 100 edges, HTML and Mermaid generated
- real `data_service` governance: 3 V2.7 feedback records, 3 approved rules, revoked rule removed from rebuilt plan, artifact hashes unchanged
- real HarnessOS governance: 3 V2.7 feedback records, 3 approved rules, revoked rule removed from rebuilt plan, artifact hashes unchanged

Next phase:

- none inside accepted V2.7 scope.

## 1. Scope

V2.7 implements documentation-code architecture governance. Phase 49, Phase 50, Phase 51, Phase 52, Phase 53, Phase 54, and Phase 55 are complete:

```text
document registry [accepted]
-> architecture claim extraction [accepted]
-> document quality evaluation [accepted]
-> doc-code alignment v2 [accepted]
-> reconstructed architecture reports [accepted]
-> governance integration [accepted]
-> closure audit [accepted]
```

It builds on V2.0-V2.6 artifacts and does not reopen V2.5 ResearchNotebook backend work.

## 2. Shared Gates

Every phase must satisfy:

- pass V2.6 closure and artifact availability pre-gate before Phase 49;
- use real `data_service` and HarnessOS repositories;
- verify HarnessOS path case and fixture availability;
- inspect persisted artifacts on disk;
- compare HTTP/MCP/CLI outputs where public interfaces exist;
- run focused tests plus relevant V2.6 regression tests;
- run public redaction checks for paths and secrets;
- run HTML/Mermaid escaping checks where rendered outputs exist;
- run cross-link integrity checks after claim, alignment and reconstruction artifacts exist;
- run source artifact hash gates for source registry, prior V2 artifacts and original documents;
- preserve prior V2 artifacts unless the phase explicitly rebuilds them;
- produce phase acceptance audit report;
- stop for human review if fatal or major PRD/spec drift is found.

False-green rejection:

- mock-only data;
- empty artifacts marked accepted;
- copied drawio presented as code-derived architecture;
- low-confidence match counted as accepted;
- generated view contains claims not in artifacts;
- document claim accepted without document evidence;
- code alignment accepted without code evidence.
- missing V2.6 artifact replaced with mock data;
- historical document promoted to current authority without supersession evidence;
- HTML/Mermaid output contains unescaped document text injection;
- accepted artifact has unresolved doc/claim/code/model links.

## 3. Phase 49: Document Asset Registry

Goal:

- Register architecture-relevant project documents as first-class assets.

Implementation design:

- Add document discovery under architecture docs root.
- Classify document types using path, filename, heading, and content signals.
- Store document metadata separately from extracted claims.

Inputs:

- snapshot files;
- known architecture source discovery from V2.4;
- real docs from `docs/V2.x` and HarnessOS `docs/design`.

Outputs:

- `architecture_docs.jsonl`
- `architecture_doc_sources.jsonl`

Acceptance:

- `data_service` and HarnessOS both produce non-empty document registries.
- V2.7 documents are classified as PRD, architecture, gap, plan, audit, drawio, or unknown with `needs_review`.
- HarnessOS V4/V6 docs are discovered.
- Every registered doc has evidence and repo-relative path.

Audit:

- no source registry mutation;
- no business code implementation before phase plan audit;
- no document type accepted solely from one weak filename token.

## 4. Phase 50: Architecture Claim Extractor

Goal:

- Extract structured architecture claims and relations from Markdown and drawio documents.

Implementation design:

- Extend drawio parsing from labels to claim records.
- Extend Markdown parsing from headings to claim blocks, lists, tables, acceptance gates, and non-goals.
- Preserve document evidence line ranges where available.

Outputs:

- `architecture_doc_claims.jsonl`
- `architecture_doc_relations.jsonl`

Acceptance:

- HarnessOS V6 target architecture docs produce plane/component/governance claims.
- HarnessOS V4 docs produce headless workflow chain claims.
- `data_service` V2.7 docs produce target architecture and phase claims.
- Claims without evidence are rejected or marked `needs_review`.

Audit:

- copied diagrams remain document claims, not code facts;
- no LLM-only architecture fact is accepted;
- unsupported relation semantics are marked `needs_review`.

## 5. Phase 51: Document Quality Evaluation

Goal:

- Score and report document quality risks.

Implementation design:

- Evaluate completeness, consistency, evidence, freshness, scope, acceptance gates, and closure state.
- Produce findings with severity, recommendation, evidence, and review state.

Outputs:

- `architecture_doc_quality_findings.jsonl`
- `architecture_doc_quality_summary.json`

Acceptance:

- finds missing acceptance gates where documents declare implementation scope without exit criteria;
- finds unsupported or overbroad architecture claims;
- detects status conflicts such as accepted vs pending;
- produces non-empty coverage statistics even when findings are empty.

Audit:

- quality score must not hide high-severity findings;
- findings must include evidence or `needs_review`;
- no document is marked high quality without required coverage checks.

## 6. Phase 52: Doc-Code Alignment v2

Goal:

- Compare architecture document claims with code facts and prior architecture artifacts.

Implementation design:

- Match claims against V2.0 surfaces/symbols, V2.1 graph, V2.4 roles/layers/boundaries/patterns, and V2.6 lightweight facts.
- Use match strategy labels and confidence thresholds.
- Produce both claim-to-code and code-to-document coverage.

Outputs:

- `architecture_doc_code_alignment.jsonl`
- `architecture_doc_code_drift_v2.jsonl`

Acceptance:

- accepted match requires document evidence and code evidence.
- token-only weak matches remain `weak_match`.
- produces coverage for public interfaces, modules, providers, runtime/storage artifacts, and governance boundaries.
- reports `designed_not_found_in_code` and `code_not_documented` where applicable.

Audit:

- low-confidence match cannot be accepted;
- alignment result must be stable across repeated runs on same snapshot;
- prior drift artifacts are consumed, not overwritten.

## 7. Phase 53: Architecture Reconstruction Report

Goal:

- Generate target/current/diff architecture report and views.

Implementation design:

- Build reconstructed model from document claims, code facts, alignments, and quality findings.
- Render HTML and Mermaid from persisted artifacts only.

Outputs:

- `architecture_reconstructed_model.json`
- `views/document_code_architecture_report.html`
- `views/document_code_architecture_diff.mmd`

Acceptance:

- HTML clearly separates target architecture, current code architecture, and differences.
- Mermaid node IDs map to persisted artifact IDs.
- all major nodes have source references.
- unresolved or low-confidence nodes remain visible.

Audit:

- no hand-drawn architecture node without artifact backing;
- no absolute path leak;
- no generated architecture claim absent from artifacts.

## 8. Phase 54: Governance Integration

Goal:

- Feed document quality and doc-code mismatch findings into quality governance.

Implementation design:

- Add governance target support for documents, claims, quality findings, alignments, and reconstructed nodes.
- Approved rules apply as read-time overlay only.

Outputs:

- quality feedback/rule/plan entries for V2.7 target types;
- governed read output with `applied_rules`.

Acceptance:

- can record feedback for a document claim and a doc-code mismatch.
- rule build/review/plan works for V2.7 targets.
- original documents and architecture artifacts are unchanged after feedback/rule approval.

Audit:

- approved rule does not mutate source artifacts;
- revoked rule is no longer applied to read output;
- quality summary includes V2.7 target counts.

## 9. Phase 55: Closure Acceptance

Goal:

- Close V2.7 with real-repo E2E, PRD coverage matrix, and audit.

Outputs:

- `V2_7_FULL_PRD_COVERAGE_MATRIX.md`
- `V2_7_CLOSURE_AUDIT_REPORT.md`

Acceptance:

- every PRD item is classified as accepted, conditionally accepted, not implemented, or out of scope.
- accepted rows have test and artifact evidence.
- `data_service` and HarnessOS E2E pass.
- no open fatal or major findings.

Audit:

- no false-green claims;
- no unreviewed PRD drift;
- no business-code changes before documented phase gates.
