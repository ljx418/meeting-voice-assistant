# V2.6 Full PRD Coverage Matrix

> Scope: coverage template and closure status tracker for V2.6.
> Business code must not be changed by this document.
> Current status: V2.6 accepted for planned scope.

Date: 2026-06-03

## 1. Status Values

Allowed `acceptance_status` values:

```text
accepted
needs_review
not_implemented
out_of_scope
non_claim
blocked
```

No row may be marked `accepted` without test, artifact, or audit evidence.

## 2. Coverage Matrix

| PRD Item | Capability | Expected Artifact / Interface | External Dependency | Owner | Implementation Status | Acceptance Status | Required Evidence | Evidence Path | Audit Status | Final Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| US-026-001 | Architecture scale profile | `architecture_scale_profile.json`; HTTP/MCP/CLI reads | data_service + HarnessOS repos | Phase 44 | implemented | accepted | Phase 44 focused tests, public surface guard, HTTP/MCP/CLI contract tests, real data_service + HarnessOS E2E | `docs/V2.x/V2_6_PHASE_44_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-002 | Lightweight TS/JS/Vue facts | `language_facts.jsonl` with evidence | real repo files | Phase 45 | implemented | accepted | Phase 45 focused tests + data_service/HarnessOS real E2E | `docs/V2.x/V2_6_PHASE_45_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-002 | Config inventory | `config_inventory.jsonl` | real repo config files | Phase 45 | implemented | accepted | redaction tests + real E2E artifact counts | `docs/V2.x/V2_6_PHASE_45_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-002 | Deployment inventory | `deployment_inventory.jsonl` | real repo deployment/package script files | Phase 45 | implemented | accepted | real E2E artifact counts + no-runtime-topology audit | `docs/V2.x/V2_6_PHASE_45_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-002 | Schema inventory | `schema_inventory.jsonl` | real repo schema-like files | Phase 45 | implemented | accepted | real E2E artifact counts + non-claim audit | `docs/V2.x/V2_6_PHASE_45_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-003 | Default taxonomy | `architecture_taxonomy.json` | none | Phase 46 | implemented | accepted | Phase 46 focused tests + real E2E | `docs/V2.x/V2_6_PHASE_46_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-003 | Taxonomy override | `architecture_taxonomy_override.json` merge behavior | none | Phase 46 | implemented | accepted | focused override merge test | `docs/V2.x/V2_6_PHASE_46_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-003 | Review queue | `architecture_review_queue.jsonl`; HTTP/MCP/CLI reads | none | Phase 46 | implemented | accepted | focused tests + real E2E queue counts + HTTP/MCP/CLI samples | `docs/V2.x/V2_6_PHASE_46_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-004 | Large-project HTML view | `views/architecture_large_project_overview.html` | persisted artifacts | Phase 47 | implemented | accepted | focused tests + real data_service/HarnessOS E2E non-empty HTML + no path leak | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-004 | Mermaid key boundaries | `views/architecture_key_boundaries.mmd` | persisted artifacts | Phase 47 | implemented | accepted | focused tests + real data_service/HarnessOS E2E non-empty Mermaid + persisted id evidence | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| US-026-005 | Context Pack architecture summary | Agent Context Pack section | persisted artifacts | Phase 47 | implemented | accepted | token-budget tests + real data_service/HarnessOS context packs | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Public Interface | HTTP reads | V2 success/error envelope | existing FastAPI | Phase 44-47 | implemented | accepted | public surface guard + focused HTTP tests | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Public Interface | MCP reads | V2 success/error envelope | existing MCP dispatcher | Phase 44-47 | implemented | accepted | MCP contract tests and focused MCP calls | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Public Interface | CLI reads | JSON output | existing CLI | Phase 44-47 | implemented | accepted | focused CLI command tests | `docs/V2.x/V2_6_PHASE_47_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Non-claim | Full call graph | none | n/a | Phase 48 | intentionally absent | non_claim | Phase 48 closure audit confirms no full call graph claim | `docs/V2.x/V2_6_PHASE_48_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Non-claim | Data/control flow | none | n/a | Phase 48 | intentionally absent | non_claim | Phase 48 closure audit confirms no data/control-flow claim | `docs/V2.x/V2_6_PHASE_48_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Non-claim | Runtime dispatch/type inference | none | n/a | Phase 48 | intentionally absent | non_claim | Phase 48 closure audit confirms no runtime/type-inference claim | `docs/V2.x/V2_6_PHASE_48_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Closure | data_service real E2E | all V2.6 artifact classes | real repo | Phase 48 | implemented | accepted | Phase 47 E2E plus Phase 48 rollup | `docs/V2.x/V2_6_PHASE_48_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |
| Closure | HarnessOS real E2E | all V2.6 artifact classes | real repo | Phase 48 | implemented | accepted | Phase 47 E2E plus Phase 48 rollup | `docs/V2.x/V2_6_PHASE_48_ACCEPTANCE_AUDIT_REPORT.md` | accepted | accepted |

## 3. Closure Rule

V2.6 can be declared complete only when:

- every in-scope PRD row is `accepted` or explicitly `needs_review` with human-review rationale;
- every out-of-scope claim is marked `out_of_scope` or `non_claim`;
- no `blocked` row has fatal or major severity;
- data_service and HarnessOS E2E rows are accepted;
- public redaction and prior artifact hash gate pass.

## 4. Evidence Types

Accepted evidence types:

```text
test
artifact
http_sample
mcp_sample
cli_sample
e2e_record
audit_report
hash_gate_report
redaction_report
```

Rows with `Evidence Path = TBD` must not be marked `accepted`.
