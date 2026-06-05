# V2.10 Full Coverage Matrix

> Planning scaffold. This is not closure evidence until Phase 75 fills implementation evidence.

| PRD item | Architecture item | Phase | Planned status | Closure evidence required | Acceptance status |
| --- | --- | ---: | --- | --- | --- |
| Pattern Adapter Registry | Pattern Adapter Registry | 69 | implemented | registry artifact, attempts artifact, HTTP/MCP/CLI parity | accepted |
| Generic adapter taxonomy | Pattern Adapter Registry | 69 | implemented | adapter list, no HarnessOS-hardcode scan, project config isolation | accepted |
| Adapter attempt persistence | Adapter Attempt Store | 69 | implemented | attempts JSONL for match/no_match/unavailable/blocked | accepted |
| AST registry binding | AST Binding Engine | 70 | implemented | fixture tests and real repo accepted/blocker artifacts | accepted |
| Decorator binding | AST Binding Engine | 70 | implemented | decorator fixture and truth-check evidence | accepted |
| Class inheritance binding | AST Binding Engine | 70 | implemented | class fixture and truth-check evidence | accepted |
| Factory call binding | AST Binding Engine | 70 | implemented | factory fixture and truth-check evidence | accepted |
| CLI/TUI command binding | AST Binding Engine | 70 | implemented | parser/table fixture and real repo attempts | accepted |
| Definition lookup | Definition Lookup Provider | 71 | implemented | cross-file fixture, ambiguous/unavailable contract | accepted |
| Optional Jedi/tree-sitter handling | Definition Lookup Provider | 71 | structured unavailable | provider unavailable is structured and not accepted | conditionally_accepted |
| Document-code evidence v3 | Doc-Code Evidence Matcher | 72 | implemented | matched/weak/missing/code_not_documented artifact | accepted |
| Document/code evidence separation | Evidence Acceptance Gate | 72 | implemented | document-only false-green test | accepted |
| Manifest resolver | Manifest Resolver | 73 | implemented | valid/invalid manifest tests, candidate-only rule | accepted |
| Runtime introspection safety | Runtime Candidate Importer | 73 | implemented | disabled/default, allowlist, unsafe command tests | accepted |
| Pattern report | Multi-Project Report | 74 | implemented | HTML/Mermaid generated from artifacts with consistency checks | accepted |
| V2.9 compatibility feed | V2.9 Consumer Bridge | 74 | implemented as separate V2.10 read layer | accepted |
| data_service E2E | Real Repo E2E | 75 | implemented | accepted evidence 206, attempts 2559 | accepted |
| HarnessOS E2E | Real Repo E2E | 75 | implemented | accepted evidence 431, attempts 7599 | accepted |
| Generic fixture / third repo | Generality proof | 75 | implemented through fixture and two real repos | accepted |
| HTTP/MCP/CLI parity | Public Contract | 75 | implemented | focused test covers service, HTTP, MCP, CLI | accepted |
| Redaction | Public Contract | 75 | implemented | no absolute path, secret, raw traceback, unsafe runtime output | accepted |
| False-green guard | Acceptance Gate | 75 | implemented | negative test matrix | accepted |

## Closure Field Template

Each row must be updated with:

```text
implementation_status
acceptance_status
test_command
test_result
artifact_paths
real_repo_result
audit_report_path
open_findings
```

## Required Closure Status Values

```text
accepted
conditionally_accepted
structured_blocker
not_implemented
out_of_scope
blocked_major
blocked_fatal
```

Rules:

- `accepted` requires real test result, artifact path, real repo or fixture evidence, and audit report path.
- `structured_blocker` is allowed for HarnessOS if the blocker is more precise than V2.9 `LINE_RANGE_INVALID`.
- `conditionally_accepted` must explain exactly which provider, project type, or adapter family is accepted.
- `blocked_major` or `blocked_fatal` prevents V2.10 closure.

## Closure Evidence Summary

```text
test_command: pytest backend/tests/test_v2_10_pattern_evidence.py -q
test_result: 2 passed
regression_command: pytest backend/tests/test_v2_7_document_registry.py backend/tests/test_v2_9_architecture_evidence_review.py backend/tests/test_v2_10_pattern_evidence.py backend/tests/test_public_surface_guard.py -q
regression_result: 19 passed
data_service_real_e2e: accepted=206 attempts=2559
HarnessOS_real_e2e: accepted=431 attempts=7599
audit_report: docs/V2.x/V2_10_PHASE_69_75_IMPLEMENTATION_ACCEPTANCE_AUDIT_REPORT.md
closure_report: docs/V2.x/V2_10_PHASE_75_CLOSURE_AUDIT_REPORT.md
```
