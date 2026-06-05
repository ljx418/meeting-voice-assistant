# V2.7 Target PRD: Documentation-Code Architecture Governance

> Generated for V2.7 documentation development.
> Phase 49-55 are accepted; V2.7 closure is accepted for the current worktree.
> V2.7 extends Project Intelligence with document quality evaluation, document-code comparison, and evidence-backed architecture reconstruction.

Date: 2026-06-04

## 0. Current Implementation Status

V2.7 is partially implemented.

Accepted:

- Phase 49 Document Asset Registry is accepted by `V2_7_PHASE_49_ACCEPTANCE_AUDIT_REPORT.md`.
- Real repository E2E has registered 318 document assets for `data_service` and 628 document assets for HarnessOS.
- Public Phase 49 access is available through HTTP, MCP, and CLI.
- Phase 50 Architecture Claim Extractor is accepted by `V2_7_PHASE_50_ACCEPTANCE_AUDIT_REPORT.md`.
- Real repository E2E has generated non-empty architecture claims and relations for both `data_service` and HarnessOS.
- Public Phase 50 access is available through HTTP, MCP, and CLI.
- Phase 51 Document Quality Evaluation is accepted by `V2_7_PHASE_51_ACCEPTANCE_AUDIT_REPORT.md`.
- Real repository E2E has generated document quality findings and summaries for both `data_service` and HarnessOS.
- Public Phase 51 access is available through HTTP, MCP, and CLI.
- Phase 52 Doc-Code Alignment v2 is accepted by `V2_7_PHASE_52_ACCEPTANCE_AUDIT_REPORT.md`.
- Real repository E2E has generated document-code alignment and drift artifacts for both `data_service` and HarnessOS.
- Public Phase 52 access is available through HTTP, MCP, and CLI.
- Phase 53 Architecture Reconstruction Report is accepted by `V2_7_PHASE_53_ACCEPTANCE_AUDIT_REPORT.md`.
- Real repository E2E has generated target/current/diff reconstructed architecture model, HTML report, and Mermaid diff artifacts for both `data_service` and HarnessOS.
- Public Phase 53 access is available through HTTP, MCP, and CLI.
- Phase 54 Governance Integration is accepted by `V2_7_PHASE_54_ACCEPTANCE_AUDIT_REPORT.md`.
- V2.7 document-code targets are supported by quality feedback, rules, review, correction plans, and read-time overlay.
- Phase 55 Closure Acceptance is accepted by `V2_7_CLOSURE_AUDIT_REPORT.md`.

V2.7 may be described as complete for the accepted PRD scope in this worktree.

## 1. Product Positioning

V2.7 turns Project Intelligence from code-derived architecture audit into documentation-code architecture governance.

V2.6 can summarize large codebases with scale profiles, lightweight multi-language facts, taxonomy, review queues, and large-project views. V2.7 adds the missing document side: it treats PRDs, target architecture documents, drawio diagrams, gap analyses, development plans, and acceptance reports as governed project assets, then compares their architecture claims against code facts and acceptance evidence.

V2.7 is not a pure code-to-design reverse engineering engine. It must not claim it can recover complete human design intent from code alone. Design abstraction reconstruction is accepted only when it is built from documented architecture claims, persisted code facts, evidence, confidence, and explicit review state.

## 2. Current Baseline

V2.7 starts from accepted Project Intelligence baselines:

- V2.0: codebase registry, snapshot, public surface inventory, symbol index, evidence trace, overview, Agent Context Pack.
- V2.1: DevWiki, Code Graph, Quality Governance, read-only views.
- V2.4: code-derived roles, layers, boundaries, patterns, design-code drift.
- V2.6: large-project scale profile, lightweight language/config/deployment/schema facts, taxonomy, review queue, HTML/Mermaid views, architecture context summaries.

Phase 49 must start with a V2.6 closure pre-gate. The implementation must confirm that `V2_6_CLOSURE_AUDIT_REPORT.md` exists, V2.6 architecture artifacts are readable, and V2.7 can consume V2.6 scale/taxonomy/review/view outputs without rebuilding or mutating them. Missing V2.6 artifacts must produce a structured missing-artifact status, not mock data or silent degradation.

Current limitations after Phase 55:

- document discovery and authority classification are implemented as Phase 49 baseline;
- drawio parsing captures labels and edges but not rich architecture intent;
- Markdown parsing is mostly heading-based and misses requirement/acceptance semantics;
- document-code alignment is implemented conservatively and leaves many claims as reviewable drift instead of over-accepting them;
- document quality is scored as a first-class artifact, but major findings still require review and do not imply document-code alignment;
- reconstructed architecture views distinguish documented target architecture, observed code architecture, and inferred gaps;
- governance integration applies approved rules as read-time overlay without mutating original artifacts;
- closure coverage audit is accepted, while larger semantic design-intent recovery remains out of scope.

## 3. Target Users

- Maintainer / Tech Lead: needs to know whether design docs still match the implementation.
- External Coding Agent: needs trustworthy architecture context before changing code.
- Documentation Agent: needs evidence-backed gaps for updating PRD, DevWiki, and architecture docs.
- Review Agent: needs stale, unsupported, or overclaimed documentation called out.
- Auditor: needs a traceable matrix from document claims to code evidence and acceptance artifacts.

## 4. User Stories

### US-027-001: Register and classify project architecture documents

As an audit agent, I want project documents classified by type and phase, so architecture claims can be traced to their governing source.

Acceptance:

- detects PRD, target architecture, gap analysis, drawio, development plan, acceptance plan, audit report, README, API matrix, and handoff summary;
- each document has `doc_id`, `doc_type`, `path`, `phase_hint`, `version_hint`, `scope_hint`, `authority_role`, `authority_level`, `supersedes`, `superseded_by`, `evidence`, and `stale_hint`;
- prior V2.0-V2.6 documents are classified as current, supporting, or historical authority and must not be promoted to V2.7 target authority by filename alone;
- false positives are marked `needs_review`, not accepted.

### US-027-002: Extract architecture claims from documents

As a maintainer, I want architecture statements extracted from Markdown and drawio, so the project design can be compared with code facts.

Acceptance:

- extracts systems, planes, layers, bounded contexts, components, adapters, providers, runtimes, storage, artifacts, public interfaces, governance boundaries, policies, milestones, acceptance gates, and forbidden claims;
- records `source_block_type` for heading, bullet, table row, drawio node, drawio edge, acceptance gate, non-goal, and stop condition sources;
- every claim has document evidence and confidence;
- drawio-only and inferred claims have lower confidence ceilings and must stay reviewable unless supported by stronger document evidence;
- weak or inferred claims are marked `needs_review`;
- the extractor must not copy a diagram wholesale and claim it is code-inferred architecture.

### US-027-003: Evaluate documentation quality

As a tech lead, I want documentation quality findings, so missing acceptance gates, unsupported claims, stale status, and inconsistent scope can be fixed.

Acceptance:

- evaluates completeness, consistency, evidence coverage, freshness, scope clarity, and acceptance closure;
- outputs quality findings with severity and recommended action;
- detects conflicts such as accepted vs pending, target vs current mismatch, missing exit gates, missing evidence, and unsupported overclaims.
- if any fatal or major quality finding exists, a document cannot be summarized as high quality.

### US-027-004: Compare document claims with code facts

As an external coding agent, I want each architecture claim mapped to code facts where possible, so I can know whether the design is implemented, missing, stale, or undocumented.

Acceptance:

- maps document claims to code roles, layers, boundaries, public surfaces, symbols, graph nodes, artifacts, tests, and quality findings;
- outputs statuses: `matched`, `weak_match`, `designed_not_found_in_code`, `code_not_documented`, `doc_claim_without_evidence`, `stale_doc_claim`, and `needs_review`;
- accepted matches require confidence >= 0.80 and a match strategy stronger than token overlap alone;
- token overlap alone is always `weak_match`;
- low-confidence matches are excluded from accepted architecture facts.

### US-027-005: Reconstruct architecture views from documents and code

As a reviewer, I want a target/current/diff architecture report, so I can inspect what the docs say, what the code shows, and where they disagree.

Acceptance:

- generates a canonical reconstructed architecture model;
- generates HTML and Mermaid views showing target architecture, current code architecture, and difference map;
- every displayed node must trace to a document claim, code fact, or explicitly marked inference;
- HTML output escapes document text and sanitizes links; Mermaid output uses generated artifact IDs and escaped labels;
- unresolved claims remain visible.

### US-027-006: Govern document-code mismatches

As a maintainer, I want document-code quality findings to enter the existing governance workflow, so accepted rules can guide future reads without mutating original artifacts.

Acceptance:

- supports feedback and rule planning for architecture document claims, quality findings, alignments, reconstructed nodes, and drift findings;
- approved rules apply as read-time overlay only;
- original documents, code facts, and V2.0-V2.6 artifacts are not silently rewritten.

## 5. Functional Scope

V2.7 in scope:

1. Document asset registry for architecture-relevant project documents.
2. Architecture claim extraction from Markdown and drawio.
3. Document quality evaluation.
4. Document-code alignment v2.
5. Target/current/diff reconstructed architecture views.
6. Governance integration for document-code mismatches.
7. HTTP/MCP/CLI read contracts for V2.7 artifacts.
8. Real-repo E2E on `data_service` and HarnessOS.
9. Document audit, PRD review, false-acceptance review, and closure matrix.
10. Cross-link integrity checks across documents, claims, relations, alignments, reconstructed nodes, views, and evidence.

V2.7 out of scope:

1. Complete recovery of human intent from code alone.
2. Full call graph, data flow, control flow, runtime topology, or type inference.
3. Automatic document rewriting.
4. Automatic architecture refactoring.
5. Treating a copied drawio image as code-derived evidence.
6. Claiming low-confidence matches as accepted architecture facts.

## 6. Target Artifact Layout

```text
workspace/assets/codebase/{codebase_id}/architecture/docs/
  architecture_docs.jsonl
  architecture_doc_sources.jsonl
  architecture_doc_claims.jsonl
  architecture_doc_relations.jsonl
  architecture_doc_quality_findings.jsonl
  architecture_doc_quality_summary.json
  architecture_doc_code_alignment.jsonl
  architecture_doc_code_drift_v2.jsonl
  architecture_reconstructed_model.json
  views/
    document_code_architecture_report.html
    document_code_architecture_diff.mmd
```

Each artifact must include or reference:

- `schema_version`;
- `workspace_id`;
- `codebase_id`;
- `snapshot_id`;
- `doc_id` or source artifact reference where relevant;
- evidence;
- authority metadata where relevant;
- confidence or `needs_review`;
- created timestamp;
- redaction state where relevant.

## 7. Public Interfaces

HTTP target:

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/claims
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/quality
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/alignment
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/reconstructed
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/architecture/docs/views/{view_id}
```

MCP target:

```text
knowledge_code_architecture_docs_build
knowledge_code_architecture_docs_list
knowledge_code_architecture_doc_claims
knowledge_code_architecture_doc_quality
knowledge_code_architecture_doc_code_alignment
knowledge_code_architecture_reconstructed
knowledge_code_architecture_doc_view
```

CLI target:

```text
knowledge code architecture docs build
knowledge code architecture docs list
knowledge code architecture docs claims
knowledge code architecture docs quality
knowledge code architecture docs alignment
knowledge code architecture docs reconstructed
knowledge code architecture docs view
```

## 8. Success Criteria

V2.7 is complete when:

1. `data_service` and HarnessOS both produce non-empty document registry, claim, quality, alignment, and reconstructed architecture artifacts.
2. HarnessOS V4/V6 architecture documents are classified and reflected in target architecture claims.
3. The system can show target architecture, current code architecture, and differences without copying the original diagram as a fake code result.
4. Document quality findings identify missing evidence, stale claims, inconsistent scope, and missing acceptance gates where present.
5. Accepted alignments have code evidence and document evidence.
6. Weak matches and unsupported claims remain visible as `needs_review`.
7. HTML/Mermaid views contain only persisted facts or explicitly marked inference.
8. Existing V2.0-V2.6 artifacts are not silently mutated.
9. Every phase passes source registry, prior V2 artifact, original document, and governance overlay hash gates.
10. HTTP/MCP/CLI read contracts are aligned.
11. Closure audit has no open fatal or major findings.
