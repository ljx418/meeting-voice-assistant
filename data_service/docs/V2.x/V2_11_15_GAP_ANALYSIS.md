# V2.11-V2.15 Gap Analysis

## 1. Current Capability

The project can:

- import and snapshot repositories;
- extract symbols, surfaces, documents, claims, architecture evidence, and pattern evidence;
- produce evidence-backed reports;
- expose HTTP/MCP/CLI read contracts;
- run real data_service and HarnessOS architecture evidence E2E for V2.10.

## 2. Remaining Code Assistant Gaps

| Gap | Current State | Target Stage | Target Outcome |
| --- | --- | --- | --- |
| Actionability | Context packs explain project facts but do not deeply plan edits. | V2.11 | Impact analysis and task-to-edit planning. |
| Reference graph | Symbol/evidence exists, but references are shallow. | V2.11 | Definition/reference graph v1 with provider confidence. |
| Test mapping | Suggested tests exist, but mapping is heuristic and not formalized. | V2.11 | File/symbol/capability to likely tests mapping. |
| Patch planning | Automatic edits are out of scope. | V2.12 | Read-only patch plans with rollback and validation. |
| Runtime evidence | Runtime introspection is disabled and not connected to tests/logs. | V2.13 | Allowlisted test/runtime evidence artifacts. |
| Incremental updates | Builds are mostly snapshot/full artifact based. | V2.14 | Changed-file/symbol/surface/doc detection. |
| Review UX | Reports exist but are not a complete workbench. | V2.15 | Interactive review workbench with evidence graph. |

## 3. Risks

### Risk 1: Overclaiming Static Analysis

Mitigation:

- Keep import/reference/call/runtime relation labels separate.
- Use confidence and `needs_review`.
- Reject runtime claims without runtime evidence.

### Risk 2: Unsafe Code Mutation

Mitigation:

- V2.12 generates read-only plans.
- File mutation remains out of scope until explicitly approved in a future phase.
- V2.12 acceptance must compare source file hashes or `git diff --stat` before and after plan creation.
- Validation commands are plan-only in V2.12 and must not execute until V2.13 allowlist governance exists.

### Risk 3: Unsafe Runtime Commands

Mitigation:

- V2.13 uses default deny allowlist.
- Non-allowlisted commands return structured errors.

### Risk 4: Frontend Becomes Source of Truth

Mitigation:

- V2.15 renders only persisted backend artifacts.
- HTML/Mermaid consistency checks are required.

### Risk 5: Large Project Generality

Mitigation:

- data_service remains the self-hosting sample.
- HarnessOS or another large project remains a real E2E sample.
- Project-specific logic is forbidden in generic modules.

## 4. Non-Blocking Limitations

These are accepted limitations unless a future PRD reopens them:

- no full call graph;
- no data/control flow;
- no type inference;
- no autonomous patch application;
- no arbitrary runtime execution;
- no complete human design-intent recovery from code alone.

## 5. Readiness Assessment

The roadmap is ready for document audit. It is not implementation evidence. Each stage still requires phase-specific planning, implementation, E2E, and closure audit.

## 6. V2.12 Specific Gap Closure

| Gap | Required Closure Evidence |
| --- | --- |
| Advisory edit recommendations are not persisted as reviewable artifacts. | `coding_agent/patch_plans/{patch_plan_id}.json` exists and is read back by HTTP/MCP/CLI. |
| Candidate edit regions may be too broad for safe review. | Each candidate includes repo-relative path, symbol or line range, evidence refs or `needs_review`, and confidence. |
| Validation guidance may be disconnected from impacted files/tests. | Validation commands cite V2.11 test mapping, existing command evidence, or `needs_review`; commands are not executed in V2.12. |
| Rollback scope may miss files. | Every file referenced by an edit candidate is covered by at least one rollback step or blocks readiness. |
| Large projects may not yield deterministic candidates. | Large-project runs persist structured blockers instead of pretending the plan is ready. |
