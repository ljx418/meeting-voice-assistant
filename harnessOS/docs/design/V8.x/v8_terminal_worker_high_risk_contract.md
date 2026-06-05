# V8 Terminal Worker High-Risk Contract

文档状态：V8-0 P0 high-risk contract / V8-5 entry input。

## 1. Scope

Terminal worker support covers:

```text
Codex CLI Worker
Claude CLI Worker
ChromeCLI WebChat Worker
```

V8 does not make any of them an unrestricted Agent executor.

## 2. TerminalWorkerDescriptor

Required fields:

```text
worker_id
worker_type: codex_cli | claude_cli | chromecli_webchat
agent_id
station_id
workspace_scope_ref
command_allowlist_ref
session_policy_ref
transcript_capture_ref
diff_capture_ref
handoff_policy_ref
timeout_policy_ref
kill_switch_policy_ref
created_at
```

## 3. TerminalSessionPolicy

Required fields:

```text
session_policy_id
worker_type
allowed_workspace_paths
denied_workspace_paths
allowed_commands
denied_commands
network_policy_ref
credential_policy_ref
max_runtime_seconds
requires_human_review
created_at
```

## 4. Codex / Claude CLI Rules

```text
May generate analysis, plan, patch proposal or diff.
Must capture transcript.
Must capture diff before apply.
Cannot commit, push, publish or deploy without separate human-confirmed controlled action.
Cannot read outside workspace scope.
Cannot receive raw credentials.
```

## 5. ChromeCLI WebChat Rules

```text
Must be treated as highest risk.
May only use user-owned browser session.
Must not automate production account actions.
Must not scrape secrets.
Must capture page/session evidence without leaking credentials.
Must remain design-gate only until explicit human high-risk proceed decision.
```

## 6. HumanReviewHandoff

Required fields:

```text
handoff_id
worker_id
agent_id
station_id
proposed_action
diff_ref
transcript_ref
risk_level
requires_user_confirmation
human_authorization_ref
policy_decision_ref
created_at
```

Rules:

```text
No apply / commit / push / publish without human_authorization_ref.
source=agent cannot be the authorizing actor.
```

## 7. V8-6 PASS Conditions

```text
human high-risk proceed decision exists.
Codex or Claude worker produces transcript.
Codex or Claude worker produces diff proposal.
workspace scope guard PASS.
command allowlist PASS.
source=agent durable mutation denied PASS.
human review handoff exists.
No False Green PASS.
Redaction PASS.
```

