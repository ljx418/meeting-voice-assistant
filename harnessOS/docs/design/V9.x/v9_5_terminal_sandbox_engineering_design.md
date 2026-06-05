# V9-5 Terminal Sandbox Engineering Design

文档状态：V9-5 engineering design / planned only。

## 1. Sandbox Boundary

Terminal worker is workspace-scoped and policy-controlled. It is not an unrestricted shell, not production terminal automation and not browser account automation.

## 2. Filesystem Boundary

Required checks:

```text
workspace_root canonicalization
relative path normalization
absolute path allowlist check
.. traversal denial
symlink target resolution
denied path prefix scan
write path allowlist
```

Denied by default:

```text
/etc
/var
/System
~/.ssh
~/.aws
~/.config
.env
.env.local
credential files
```

## 3. Command Allowlist Catalog

```text
Tier 0: pwd, ls, find, rg, sed, nl, cat for allowed paths
Tier 1: pytest, npm test, npm run build, type checks
Tier 2: patch proposal generation through controlled diff capture
Tier 3: high-risk workspace write requiring human_authorization_ref
Denied: git push, production deploy, credential export, shell privilege escalation
```

## 4. Network And Secret Policy

```text
network egress denied unless explicit policy exists.
secret read denied.
environment variable redaction required.
token pattern redaction required.
signed URL redaction required.
```

## 5. Transcript And Diff Capture

Every session records:

```text
terminal_session_id
command_tier
workspace_scope
policy_decision
transcript_ref
diff_ref
redaction_status
audit_ref
```

## 6. Acceptance Tests

```text
terminal_workspace_escape_denied
terminal_symlink_escape_denied
terminal_secret_read_denied
terminal_network_without_policy_denied
terminal_write_requires_diff_capture
terminal_tier3_requires_human_authorization_ref
terminal_git_push_denied
terminal_production_deploy_denied
```
