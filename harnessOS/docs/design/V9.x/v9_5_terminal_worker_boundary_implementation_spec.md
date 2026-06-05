# V9-5 Governed Terminal Worker Expansion Implementation Spec

文档状态：V9-5 implementation-readiness spec / planned only。

## 1. Boundary

V9-5 expands governed terminal worker capability. It must not become an unrestricted shell, production terminal automation, or browser account automation.

Allowed claim:

```text
V9-5 complete: governed terminal worker expansion ready for review.
```

## 2. Command Tiers

```text
Tier 0: readonly inspection commands
Tier 1: workspace-scoped test/build commands
Tier 2: workspace-scoped file write through diff proposal
Tier 3: high-risk commands requiring human approval
Denied: secret read, credential export, production deploy, git push, root/system mutation, browser account automation
```

## 3. Filesystem / Network / Secret Policy

Required policies:

```text
workspace_root
allowed_read_paths
allowed_write_paths
denied_paths
network_policy_ref
secret_read_policy_ref
command_allowlist_ref
transcript_capture_policy_ref
diff_capture_policy_ref
```

Rules:

```text
path traversal outside workspace denied.
raw credential and token reads denied.
network calls require explicit policy.
write operations produce diff proposal before durable mutation.
```

## 4. Evidence Format

Required evidence:

```text
terminal_session_id
worker_id
command
command_tier
workspace_scope_ref
transcript_ref
diff_proposal_ref
policy_decision_ref
human_authorization_ref
correlation_id
request_id
audit_ref
redaction_status
```

## 5. Acceptance Tests

```text
terminal_worker_readonly_command_allowed
terminal_worker_workspace_escape_denied
terminal_worker_secret_read_denied
terminal_worker_git_push_denied_by_default
terminal_worker_production_deploy_denied_by_default
terminal_worker_write_requires_diff_proposal
terminal_worker_high_risk_command_requires_human_authorization_ref
terminal_worker_transcript_capture_exists
terminal_worker_diff_capture_exists
terminal_worker_no_false_green
```

## 6. Stop Conditions

```text
unrestricted shell is allowed.
workspace escape succeeds.
secret read succeeds.
git push or production deploy runs without separate gate.
browser account automation is enabled without separate PRD.
```
