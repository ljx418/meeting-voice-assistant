# V9-5 Development And Acceptance Plan

文档状态：V9-5 detailed development and acceptance plan / implementation complete for review.

This document records the V9-5 stage plan and completed governed terminal worker evidence package. It does not authorize unrestricted shell, production terminal automation or browser account automation.

## 1. Entry Baseline

V9-5 entered implementation after:

```text
V9-4 evidence PASS or a documented proceed decision scopes V9-5 independently as a narrow sandbox readiness slice only.
Terminal sandbox engineering design accepted.
Command allowlist catalog accepted.
Filesystem boundary and symlink policy accepted.
human high-risk proceed decision recorded for terminal worker write sandbox.
No False Green scan PASS.
Redaction scan PASS.
```

V9-5 completion evidence:

```text
docs/design/V9.x/evidence/v9-5-terminal-worker/acceptance-data.json
docs/design/V9.x/evidence/v9-5-terminal-worker/index.html
docs/design/V9.x/evidence/v9-5-terminal-worker/result-summary.md
```

Independent proceed is narrow:

```text
It may validate workspace boundary, command tier policy, transcript capture, diff capture and denial evidence.
It must not enable broad terminal runtime, unrestricted shell, production deploy, git push or browser account automation.
It must not authorize terminal write actions beyond explicitly scoped sandbox readiness fixtures.
```

## 2. Scope

V9-5 expands terminal worker behavior inside a governed workspace sandbox:

```text
workspace-scoped readonly commands
workspace-scoped build and test commands
controlled diff proposal generation
approval-gated workspace write attempts
transcript capture
diff capture
denial evidence for escape and sensitive access attempts
```

V9-5 must not:

```text
provide unrestricted shell access.
run production deployment.
push to remote repositories.
automate production browser accounts.
allow workspace escape.
```

## 3. Implementation Slices

| Slice | Output | Acceptance |
| --- | --- | --- |
| V9-5A Workspace boundary guard | path decision records | canonical path, symlink target and denied prefixes recorded |
| V9-5B Command tier resolver | terminal_command_decision records | tier, policy decision and human authorization requirement visible |
| V9-5C Transcript capture | transcript_ref records | command, status and redacted output refs visible |
| V9-5D Diff capture | diff_capture records | write attempts create proposal / diff refs |
| V9-5E Denial evidence | denied action records | escape, sensitive access, git push and deployment attempts denied |
| V9-5F Dashboard | HTML and acceptance data | auditor can inspect command tiers and denial evidence |

## 4. Required Fixtures

Positive fixture:

```text
fixtures/terminal/workspace_scoped_test_and_diff_capture.json
```

Negative fixtures:

```text
fixtures/terminal/terminal_workspace_escape.json
fixtures/terminal/terminal_symlink_escape.json
fixtures/terminal/terminal_sensitive_read_attempt.json
fixtures/terminal/terminal_network_without_policy.json
fixtures/terminal/terminal_git_push_attempt.json
fixtures/terminal/terminal_production_deploy_attempt.json
```

## 5. Acceptance Tests

```text
v9_5_workspace_canonicalization_records_scope
v9_5_readonly_command_records_transcript
v9_5_build_or_test_command_records_exit_status
v9_5_write_action_requires_diff_capture
v9_5_write_action_requires_valid_human_authorization
v9_5_workspace_escape_denied
v9_5_symlink_escape_denied
v9_5_sensitive_read_denied
v9_5_git_push_denied
v9_5_production_deploy_denied
v9_5_claim_scan_pass
v9_5_redaction_scan_pass
```

## 6. Evidence Package

V9-5 completion evidence must include:

```text
acceptance-data.json
index.html
result-summary.md
terminal_session_ref
command_decision_refs
transcript_refs
diff_capture_refs
denied_action_refs
human_authorization_refs
claim_scan_result
redaction_scan_result
```

## 7. Stop Conditions

```text
Unrestricted shell is allowed.
Workspace escape succeeds.
Symlink escape succeeds.
Sensitive content is read into evidence.
Git push or production deployment executes.
Write action occurs without diff capture and valid authorization.
Terminal worker is claimed as production terminal automation.
V9-5 evidence is reused to claim unrestricted terminal worker ready.
V9-5 evidence is reused to authorize V9-7 production automation.
```
