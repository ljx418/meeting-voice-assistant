# V2.11-V2.15 Milestones and Exit Gates

## 1. Milestones

| Milestone | Stage | Exit Result |
| --- | --- | --- |
| M1 | V2.11 | Coding Agent can request evidence-backed impact analysis and edit plan. |
| M2 | V2.12 | System can generate safe read-only patch plans with rollback and validation. |
| M3 | V2.13 | System can collect allowlisted runtime/test evidence safely. |
| M4 | V2.14 | System can detect and report incremental project intelligence changes. |
| M5 | V2.15 | Human and agent workbench can inspect evidence, risks, blockers, and exports. |

## 2. Stage Exit Gates

### V2.11

- Actionability index exists.
- Impact analysis exists.
- Task-to-edit plan exists.
- Test mapping exists.
- HTTP/MCP/CLI parity passes.
- Real data_service E2E passes.
- Large-project E2E passes or structured blocker is accepted.

### V2.12

- Patch plan artifact exists.
- No file mutation occurs.
- Validation plan and rollback plan are present.
- All recommendations have evidence or `needs_review`.
- Validation commands are marked `plan_only` and are not executed.
- Readiness cannot be `ready_for_review` when edit candidates, validation, rollback, or evidence are incomplete.
- HTTP/MCP/CLI read back the same stable `patch_plan_id`, status, counts, warnings, unresolved items, and artifact refs.
- Large-project run either returns a reviewable plan or exact structured blockers.

### V2.13

- Command allowlist exists.
- Default deny behavior passes.
- At least one allowlisted data_service test command runs.
- Logs are redacted.
- Runtime evidence stays separate from static evidence.

### V2.14

- Snapshot diff artifact exists.
- Changed files/symbols/surfaces/docs are reported.
- Historical artifacts are not silently rewritten.
- Incremental result is traceable to snapshot IDs.

### V2.15

- Workbench HTML exists.
- Capability graph exists.
- Visible facts resolve to artifact IDs.
- Blockers and needs_review are visible.
- Public output has no absolute path or secret leak.

## 3. Human Approval Gates

Human approval is required before:

- applying a patch;
- running a non-allowlisted command;
- using production credentials;
- exposing raw logs;
- sending code to an external provider;
- marking a weak or provider-unavailable result accepted.

## 4. Final Closure Gate

Final closure requires:

- all stage closure reports accepted;
- all in-scope coverage rows accepted or conditionally accepted with evidence;
- no open fatal or major findings;
- real data_service E2E;
- large-project E2E;
- artifact inspection;
- HTTP/MCP/CLI parity;
- false-green audit.
