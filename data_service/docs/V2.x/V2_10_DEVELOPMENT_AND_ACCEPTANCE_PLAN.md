# V2.10 Development and Acceptance Plan

## Phase 69: Pattern Adapter Registry

Development:

- Implement adapter registry schema.
- Add generic adapter taxonomy.
- Add adapter attempt recording.
- Add configuration loading for optional project pattern packs.

Acceptance:

- Registry lists enabled, disabled, and unavailable adapters.
- Adapter attempts are persisted even when no match is accepted.
- No HarnessOS-specific rule is hardcoded into generic engine.

## Phase 70: Python AST Binding Engine

Development:

- Extract registry assignments, decorators, class inheritance, call expressions, imports, and aliases.
- Bind registry entries to symbol candidates.
- Emit candidate source path and line range.

Acceptance:

- Real Python fixture covers dictionary registry, decorator, class inheritance, factory call, and import alias.
- Accepted binding line ranges pass truth check.
- Dynamic or unresolved binding becomes `needs_review`.

## Phase 71: Definition Lookup Provider

Development:

- Add default AST import resolver.
- Add optional Jedi provider if available.
- Define provider status and structured unavailable errors.

Acceptance:

- Cross-file imported symbol resolves on real fixture.
- Provider unavailable path returns structured status.
- Token/string matching alone cannot become accepted evidence.

## Phase 72: Document Claim to Code Evidence Matching v3

Development:

- Use V2.7 document claims and V2.10 code bindings.
- Produce matched, weak_match, missing_code_evidence, and code_not_documented.
- Keep document and code evidence separate.

Acceptance:

- Matched item has document evidence and code line evidence.
- Weak match is never accepted.
- HarnessOS architecture docs are evaluated without being copied as code facts.

## Phase 73: Manifest and Runtime Introspection Contracts

Development:

- Define architecture manifest schema.
- Add manifest candidate loader.
- Add disabled-by-default runtime introspection contract.
- Add allowlist, timeout, redaction, and structured error semantics.

Acceptance:

- Valid manifest can improve candidate discovery but not bypass line evidence gate.
- Invalid manifest returns schema error.
- Runtime introspection is off by default.
- Allowlisted command output is candidate-only until statically bound.

## Phase 74: Multi-Project Evidence Report

Development:

- Generate human-readable pattern evidence report.
- Include adapter attempts, matches, blockers, accepted evidence, confidence, and next steps.
- Add Mermaid adapter map.
- Feed accepted evidence into V2.9 public surface evidence where compatible.

Acceptance:

- HTML report is readable and escaped.
- Mermaid nodes map to persisted artifacts.
- data_service and HarnessOS reports explain accepted evidence or blockers.
- At least one non-HarnessOS generic fixture or real repo demonstrates generic adapter reuse.

## Phase 75: Closure Acceptance

Development:

- Update coverage matrix and gap analysis.
- Run real E2E on data_service and HarnessOS.
- Run generic fixture tests.
- Produce closure audit.

Acceptance:

- No open fatal/major finding.
- HarnessOS blocker improves from `LINE_RANGE_INVALID` to accepted evidence or more precise blockers.
- False-green scan passes.
- Public outputs contain no absolute paths, secrets, or runtime traceback.

## Shared Stop Conditions

Stop and request human review if:

- implementation requires running non-allowlisted target project code;
- accepted evidence lacks line range;
- adapter logic becomes HarnessOS-only in generic modules;
- manifest-only or document-only claim is promoted to accepted code evidence;
- full call graph or runtime-flow claims appear.

## Shared Pre-Implementation Gates

Every phase must close these gates before business code changes begin:

1. Authority gate: `V2_10_TARGET_PRD.md`, `V2_10_TARGET_ARCHITECTURE.md`, this plan, and the phase-specific plan are the controlling specifications for V2.10.
2. Baseline gate: V2.9 closure artifacts for `data_service` and HarnessOS are readable, or the phase records a structured `V29_BASELINE_UNAVAILABLE` blocker and does not claim improvement.
3. Immutability gate: V2.0-V2.9 source artifacts are treated as read-only inputs unless their owning phase is explicitly rebuilt.
4. Generality gate: generic V2.10 modules must not contain project names, local absolute paths, or HarnessOS-specific path fragments.
5. Truth-check gate: accepted code evidence requires repo-relative path, valid source file, valid line range, readable snippet, and `truth_check=passed`.
6. Public contract gate: HTTP, MCP, and CLI success and error envelopes must use the same schema version, stable ids, counts, warnings, unresolved items, artifact refs, and error codes.
7. Redaction gate: public payloads, HTML, Mermaid, logs, audit reports, and error bodies must not expose absolute paths, secrets, raw tracebacks, or non-redacted runtime output.

## Shared Automated Acceptance Tests

The phase test suite must include, at minimum:

```text
test_v2_10_artifact_schema_validation.py
test_v2_10_public_contract_parity.py
test_v2_10_no_harnessos_hardcode.py
test_v2_10_line_range_truth_check.py
test_v2_10_false_green_rejections.py
test_v2_10_public_payload_redaction.py
```

Phase-specific tests may use different filenames, but the audit report must map each shared rule to a concrete test command and result.

## Real Repository Acceptance Baseline

V2.10 must be evaluated against:

```text
data_service: /Users/Zhuanz/Desktop/workspace/data_service
HarnessOS: /Users/Zhuanz/Desktop/workspace/harnessOS
generic fixture or third real repo: documented in the phase audit report
```

Accepted outcomes:

- `data_service`: accepted evidence exists for at least three adapter families by Phase 75.
- `HarnessOS`: accepted evidence count improves over V2.9, or blockers become more precise than the V2.9 generic `LINE_RANGE_INVALID` blocker.
- generic fixture / third repo: at least three adapter families produce accepted evidence without project-specific code.

Rejected outcomes:

- all accepted evidence comes from one repository;
- HarnessOS-specific logic is embedded in generic modules;
- a skipped third-repo/generic-fixture run is counted as generality proof.

## Phase Audit Report Template

Each phase must produce or update a phase audit report with:

```text
phase
controlling_documents
implemented_artifacts
test_commands
test_results
real_repo_results
http_mcp_cli_parity_result
immutability_result
redaction_result
false_green_result
prd_spec_review
open_findings
audit_opinion
```

`audit_opinion` may be `pass`, `pass_with_minor_findings`, `blocked_major`, or `blocked_fatal`. A phase with open fatal or major findings cannot advance to the next implementation phase.
