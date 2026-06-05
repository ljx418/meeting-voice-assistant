# V2.7 Full PRD Coverage Matrix

> Coverage matrix for V2.7.
> Phase 49-55 rows include implementation evidence.
> No row was marked accepted without real artifact and test evidence.

Date: 2026-06-04

## 1. Status Values

Allowed implementation status:

```text
implemented
not_implemented
out_of_scope
```

Allowed acceptance status:

```text
accepted
conditionally_accepted
rejected
out_of_scope
```

## 2. Coverage Matrix

| PRD item | Capability | Target artifact / interface | Phase | Implementation status | Acceptance status | Required evidence before accepted |
| --- | --- | --- | --- | --- | --- | --- |
| US-027-001 | Register and classify project architecture documents | `architecture_docs.jsonl`, `architecture_doc_sources.jsonl` | 49 | implemented | accepted | `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md`; `backend/tests/test_v2_7_document_registry.py`; data_service 318 docs; HarnessOS 628 docs |
| US-027-001 | Document type, phase, version, scope and stale hints | document registry fields | 49 | implemented | accepted | focused golden assertions on V2.7 docs and HarnessOS V4/V6 docs |
| US-027-001 | Document authority and supersession | `authority_role`, `authority_level`, `supersedes`, `superseded_by` | 49 | implemented | accepted | historical V2.5/V2.6 docs not promoted to current V2.7 authority |
| US-027-002 | Extract architecture claims from Markdown | `architecture_doc_claims.jsonl` | 50 | implemented | accepted | `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`; `backend/tests/test_v2_7_document_registry.py`; data_service 20085 claims; HarnessOS 18367 claims |
| US-027-002 | Extract architecture relations from drawio and Markdown | `architecture_doc_relations.jsonl` | 50 | implemented | accepted | `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`; drawio relation fixture; data_service 16704 relations; HarnessOS 13476 relations |
| US-027-002 | Claim confidence policy | `source_block_type`, confidence ceilings, needs_review | 50 | implemented | accepted | focused tests verify drawio claims stay <= 0.70 and remain reviewable |
| US-027-002 | Reject copied diagram as code-derived fact | extractor flags and view labels | 50/53 | implemented | accepted | Phase 50 marks drawio items as document claims with `needs_review`; Phase 53 target/current separation keeps document claims out of code-derived current nodes |
| US-027-003 | Evaluate document quality | `architecture_doc_quality_findings.jsonl`, `architecture_doc_quality_summary.json` | 51 | implemented | accepted | `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`; `backend/tests/test_v2_7_document_quality.py`; data_service 988 findings; HarnessOS 1621 findings |
| US-027-003 | Document quality summary | summary counts and severity distribution | 51 | implemented | accepted | data_service severity counts major: 263, minor: 725; HarnessOS severity counts major: 194, minor: 1427 |
| US-027-003 | Major/fatal finding blocks high quality status | quality summary status | 51 | implemented | accepted | focused quality test and real E2E show major findings produce `needs_review`, not `high_quality` |
| US-027-004 | Compare document claims with code facts | `architecture_doc_code_alignment.jsonl` | 52 | implemented | accepted | `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md`; focused HTTP/MCP/CLI tests; data_service 20827 alignments; HarnessOS 18635 alignments |
| US-027-004 | Report document-code drift | `architecture_doc_code_drift_v2.jsonl` | 52 | implemented | accepted | data_service 13478 drift rows; HarnessOS 13989 drift rows; includes designed-not-found and code-not-documented rows |
| US-027-004 | Reject token-only accepted matches | alignment status and confidence policy | 52 | implemented | accepted | focused tests verify token-only matches are not `matched`; real E2E summary has `token_overlap_only_accepted=false` |
| US-027-004 | Match strategy and threshold policy | `accepted_match_confidence_min`, `match_strategy` | 52 | implemented | accepted | accepted match confidence >= 0.80 and non-token strategy; public summary exposes threshold |
| US-027-005 | Reconstruct target/current/diff architecture model | `architecture_reconstructed_model.json` | 53 | implemented | accepted | `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md`; data_service 180/180/220 nodes, HarnessOS 180/180/220 nodes |
| US-027-005 | Generate HTML architecture report | `views/document_code_architecture_report.html` | 53 | implemented | accepted | focused HTTP/MCP/CLI tests; real data_service and HarnessOS HTML reports generated with target/current/diff sections |
| US-027-005 | Generate Mermaid diff view | `views/document_code_architecture_diff.mmd` | 53 | implemented | accepted | Mermaid `flowchart LR`; edge node endpoints resolve to persisted model node IDs |
| US-027-005 | HTML/Mermaid safety | escaped labels, sanitized links, generated node IDs | 53 | implemented | accepted | renderer-level script escaping test; real E2E path leak checks passed |
| US-027-006 | Governance feedback for document-code findings | quality feedback/rules/plan target types | 54 | implemented | accepted | `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md`; focused tests cover doc claim, alignment, reconstructed node and missing target rejection |
| US-027-006 | Read-time governance overlay only | governed read payloads with `applied_rules` | 54 | implemented | accepted | source artifact hashes unchanged before/after rule approval in focused and real E2E |
| US-027-006 | Governance revoke behavior | governed read payloads after revoke | 54 | implemented | accepted | revoked rule is removed from the rebuilt correction plan and no longer appears in affected governed read `applied_rules` |
| Integrity | V2.6 closure pre-gate | V2.6 closure report and readable artifacts | 49 | implemented | accepted | Phase 49 pre-implementation audit and acceptance audit |
| Integrity | Cross-link integrity | docs/claims/relations/alignments/model/views resolve | 50-55 | implemented | accepted | Phase 50 validates claim/relation IDs; Phase 53 verifies edge node endpoints resolve to persisted model nodes; Phase 54 resolver rejects missing targets |
| Integrity | Source artifact hash gate | source registry, prior V2 artifacts, original docs hashes | 49-55 | implemented | accepted | Phase 54 focused and real E2E verify claim/alignment/reconstruction artifact hashes unchanged after approve/revoke |
| Integrity | HarnessOS path and fixture gate | required HarnessOS sibling repo and V4/V6 samples | 49-55 | implemented | accepted | Phase 49-54 real E2E used the configured HarnessOS sibling repository and extracted HarnessOS docs/artifacts without publishing a full local path |
| Public contract | HTTP document registry reads | V2.7 envelope and docs paths | 49 | implemented | accepted | `POST/GET /architecture/docs`; public surface guard |
| Public contract | MCP document registry reads | V2.7 docs MCP tools | 49 | implemented | accepted | `knowledge_code_architecture_docs_build/list`; MCP registry test |
| Public contract | CLI document registry reads | `knowledge code architecture docs-build/docs` | 49 | implemented | accepted | focused HTTP/MCP/CLI parity test |
| Public contract | Claims read/build | HTTP/MCP/CLI claims build/read | 50 | implemented | accepted | `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`; focused HTTP/MCP/CLI tests |
| Public contract | Quality read/build | HTTP/MCP/CLI quality build/read | 51 | implemented | accepted | `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`; focused HTTP/MCP/CLI tests |
| Public contract | Alignment reads | HTTP/MCP/CLI alignment build/read | 52 | implemented | accepted | `POST/GET /architecture/docs/alignment`; MCP registry test; CLI focused test |
| Public contract | Reconstructed architecture reads | HTTP/MCP/CLI reconstructed build/read/view | 53 | implemented | accepted | focused HTTP/MCP/CLI parity tests; MCP registry count 95; route baseline 127 |
| Public contract | Governance integration reads | quality feedback/rules/summary/plan for V2.7 targets | 54 | implemented | accepted | focused test covers HTTP feedback, MCP summary and CLI summary against V2.7 target types |
| Real E2E | data_service | all V2.7 artifact classes | 55 | implemented | accepted | Phase 49-54 acceptance reports, real E2E matrix, and `V2_7_CLOSURE_AUDIT_REPORT.md` cover registry, claims, quality, alignment, reconstruction, governance, and closure rollup |
| Real E2E | HarnessOS | all V2.7 artifact classes | 55 | implemented | accepted | Phase 49-54 acceptance reports, real E2E matrix, and `V2_7_CLOSURE_AUDIT_REPORT.md` cover registry, claims, quality, alignment, reconstruction, governance, and closure rollup |
| Non-goal | Pure code recovery of human design intent | none | all | out_of_scope | out_of_scope | closure audit confirms no such claim |
| Non-goal | Full call/data/control flow or runtime topology | none | all | out_of_scope | out_of_scope | closure audit confirms no such claim |
| Non-goal | Automatic document rewriting or architecture refactoring | none | all | out_of_scope | out_of_scope | closure audit confirms no such claim |

## 3. Closure Rules

Phase 55 closure:

- every row has an actual implementation status;
- every accepted row cites concrete tests and artifacts;
- every out-of-scope row must cite PRD non-goal language;
- every rejected row must have owner and next action;
- no pending row remains for in-scope V2.7 MVP capability.

## 4. Evidence Columns To Fill During Implementation

When implementation begins, add these evidence fields or linked tables:

```text
test_command
test_result
artifact_path
artifact_count
data_service_result
harnessos_result
audit_report
open_findings
```
