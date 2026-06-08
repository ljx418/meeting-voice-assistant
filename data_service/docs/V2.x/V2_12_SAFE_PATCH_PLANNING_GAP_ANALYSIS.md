# V2.12 Gap Analysis: Safe Patch Planning

## 1. Current State

V2.11 can generate:

- actionability index;
- AST-backed definitions and references;
- impact analysis;
- test mapping;
- task-to-edit plans.

However, it does not yet produce a complete patch planning artifact with edit options, validation plan, rollback scope, and readiness scoring.

## 2. Target State

V2.12 should produce safe patch plans:

```text
task -> actionability/impact/task-plan -> patch options -> validation descriptors -> rollback scope -> readiness score
```

## 3. Gap Matrix

| Gap | Current State | V2.12 Target | Risk |
| --- | --- | --- | --- |
| Patch plan artifact | No dedicated persisted patch plan | `coding_agent/patch_plans/{patch_plan_id}.json` | Agent cannot review a coherent edit plan |
| Candidate edit regions | Task plan has recommendations but no region grouping | Proposed files, symbols, and line regions | Overbroad or vague edits |
| Multi-option planning | Single advisory list | Minimal/broader/test-doc options | No tradeoff visibility |
| Validation plan | Suggested tests exist but are not formal descriptors | Descriptor-only validation plan | Unsafe command execution if unclear |
| Rollback scope | Not formalized | Every proposed file covered | Hard to review risk |
| Readiness score | Not formalized | Ready/needs_review/blocked with reasons | False confidence |
| No-mutation proof | V2.11 does not mutate but V2.12 needs explicit proof | Before/after source diff gate | Safety regression |

## 4. Key Risks

### Risk 1: Patch Plan Becomes Patch Application

Mitigation:

- `mutates_code=false` required.
- No source write APIs.
- No diff apply command.
- Acceptance checks source state before/after.

### Risk 2: Validation Plan Runs Commands

Mitigation:

- Validation commands are descriptors only.
- V2.13 owns execution under allowlist.
- V2.12 must not call subprocess.

### Risk 3: Readiness Score Overclaims Safety

Mitigation:

- Blockers force `needs_review` or `blocked`.
- Low evidence prevents ready status.
- Missing rollback or validation blocks readiness.

### Risk 4: Large-Project Performance

Mitigation:

- Reuse V2.11 actionability artifacts.
- Allow structured blocker if HarnessOS exceeds runtime window.
- Do not add HarnessOS-only logic.

## 5. Readiness for Implementation

V2.12 will be ready for implementation after:

- this PRD and acceptance plan are reviewed;
- drawio target state is updated;
- pre-implementation audit closes fatal/major findings.
