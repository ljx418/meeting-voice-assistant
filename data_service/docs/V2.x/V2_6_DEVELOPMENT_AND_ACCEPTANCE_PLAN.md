# V2.6 Development and Acceptance Plan

> Scope: Large-scale architecture abstraction hardening.
> Business code was not modified by this document.
> V2.6 does not reopen V2.5 ResearchNotebook backend closure.

Date: 2026-06-03

## 1. Phase Plan

| Phase | Name | Goal | Primary Outputs |
| --- | --- | --- | --- |
| Phase 43 | Documentation and Target State | Freeze PRD, architecture, gap, acceptance, audit, and drawio plan. | V2.6 planning docs and target state diagram |
| Phase 44 | Architecture Scale Profile | Measure large-project architecture artifact scale and summary requirements. | `architecture_scale_profile.json` |
| Phase 45 | Lightweight Multi-language and Config Inventory | Add TS/JS/Vue/config/deployment/schema facts. | `config_inventory.jsonl`, `deployment_inventory.jsonl`, `schema_inventory.jsonl` |
| Phase 46 | Taxonomy and Review Queue | Add architecture taxonomy and needs-review queue. | `architecture_taxonomy.json`, `architecture_review_queue.jsonl` |
| Phase 47 | Large-project Views and Context Integration | Render compact views and feed architecture summaries to Agent Context Pack. | HTML/Mermaid views and context-pack integration |
| Phase 48 | Closure Audit | Complete real-repo E2E and closure audit. | `V2_6_CLOSURE_AUDIT_REPORT.md` |

Detailed execution, artifact schema, public contract, real-repo E2E, and closure coverage are governed by:

- `V2_6_PHASE_44_48_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
- `V2_6_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md`
- `V2_6_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md`
- `V2_6_FULL_PRD_COVERAGE_MATRIX.md`
- `V2_6_PHASE_44_PRE_IMPLEMENTATION_AUDIT_REPORT.md`
- `V2_6_CLOSURE_AUDIT_REPORT.md`

## 2. Phase 43: Documentation and Target State

Development tasks:

- Create V2.6 PRD, architecture, gap, development/acceptance, document audit, and drawio files.
- Create detailed Phase 44-48 development and acceptance plan.
- Create artifact schema and public contract.
- Create real-repo E2E acceptance matrix.
- Create full PRD coverage matrix.
- Create Phase 44 pre-implementation audit report.
- Create closure audit template.
- Update `docs/V2.x/README.md`.
- Update `docs/active/README.md`.
- Ensure V2.6 scope is engineering hardening, not full static analysis.

Acceptance:

- drawio XML parses.
- all V2.6 docs exist and are non-empty.
- document audit has no fatal/major finding.
- V2.6 references V2.4 and V2.5 correctly.
- ChatGPT audit package remains under 20 files.
- open product questions are closed in `V2_6_GAP_ANALYSIS.md`.
- artifact schema, public contract, E2E matrix, coverage matrix, and closure template are decision-complete for implementation.

## 3. Phase 44: Architecture Scale Profile

Development tasks:

- Build `ArchitectureScaleProfile` from existing artifacts.
- Record artifact sizes, durations, counts, warning totals, confidence distribution, and needs_review totals.
- Add summary-first public payload.
- Add hash gate for prior V2 artifacts.
- Add HTTP/MCP/CLI build/read paths according to the public contract.

Acceptance:

- `data_service` E2E produces non-empty scale profile.
- HarnessOS E2E produces non-empty scale profile.
- profile contains file_count, LOC, language distribution, artifact sizes, warning counts, confidence distribution, and summary mode flag.
- public output has no absolute paths.
- prior artifact hashes are unchanged unless explicitly rebuilt.
- missing prerequisites return structured errors, not fake profiles.

## 4. Phase 45: Lightweight Multi-language and Config Inventory

Development tasks:

- Extract TS/JS/Vue lightweight facts.
- Extract config/deployment/schema inventory.
- Redact sensitive config values.
- Persist inventory artifacts.

Acceptance:

- `data_service` and HarnessOS both produce non-empty config/deployment inventory.
- package manifests, Python config, frontend package hints, and CI/container/deployment hints are detected where present.
- no raw secret values in public output.
- non-Python facts include confidence and evidence.
- unsupported claims are placed into `needs_review`.

## 5. Phase 46: Taxonomy and Review Queue

Development tasks:

- Add default taxonomy.
- Add optional taxonomy override artifact.
- Generate review queue from ambiguous, low-confidence, unsupported, or missing-evidence items.
- Add HTTP/MCP/CLI reads for review queue.

Acceptance:

- role/layer/pattern samples have evidence.
- low-confidence items are excluded from accepted summaries.
- review queue count is exposed through HTTP/MCP/CLI.
- taxonomy override keeps default fallback behavior.

## 6. Phase 47: Large-project Views and Agent Context Integration

Development tasks:

- Render large-project HTML overview.
- Render key boundaries Mermaid view.
- Integrate V2.6 architecture summary into Agent Context Pack.
- Enforce token-budget safe evidence handling.

Acceptance:

- HTML and Mermaid render from persisted artifacts only.
- Mermaid nodes exist in artifact IDs.
- Agent Context Pack includes scale/profile/review summaries.
- small token budget does not keep evidence-free architecture advice.

## 7. Phase 48: Closure Audit

Development tasks:

- Run final real-repo E2E on `data_service`.
- Run final real-repo E2E on HarnessOS.
- Inspect persisted artifacts.
- Run public redaction checks.
- Produce closure report.

Acceptance:

- all phase-focused tests pass;
- `data_service` and HarnessOS E2E pass;
- no open fatal/major audit finding;
- closure report explicitly lists accepted, needs_review, out-of-scope, and non-claims.

## 8. Required Test Files

Planned focused tests:

```text
backend/tests/test_v2_6_architecture_scale_profile.py
backend/tests/test_v2_6_config_deployment_inventory.py
backend/tests/test_v2_6_architecture_taxonomy_review_queue.py
backend/tests/test_v2_6_large_project_views.py
backend/tests/test_v2_6_closure_acceptance.py
```

## 9. Global False-Green Rejection

Reject any phase if:

- mocks replace the required real `data_service` or HarnessOS E2E;
- output claims full call graph, data flow, control flow, runtime tracing, or type inference;
- low-confidence items are counted as accepted facts;
- public output leaks absolute paths or secrets;
- views display facts not backed by persisted artifacts;
- prior V2 artifacts are silently rewritten.

## 10. ChatGPT Audit Package

The V2.6 document package for external audit is limited to these files:

```text
docs/V2.x/V2_6_TARGET_PRD.md
docs/V2.x/V2_6_TARGET_ARCHITECTURE.md
docs/V2.x/V2_6_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_6_GAP_ANALYSIS.md
docs/V2.x/V2_6_DOCUMENT_AUDIT_REPORT.md
docs/V2.x/V2_6_TARGET_STATE.drawio
docs/V2.x/V2_6_PHASE_44_48_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_6_ARTIFACT_SCHEMA_AND_PUBLIC_CONTRACT.md
docs/V2.x/V2_6_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md
docs/V2.x/V2_6_FULL_PRD_COVERAGE_MATRIX.md
docs/V2.x/V2_6_PHASE_44_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_6_CLOSURE_AUDIT_REPORT.md
docs/V2.x/README.md
docs/active/README.md
```

This package has 14 files. It is the complete V2.6 document-audit package for development readiness. It is not implementation closure evidence.
