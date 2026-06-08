# V2.13 PRD: Controlled Runtime Evidence

## 1. Product Goal

V2.13 adds a controlled runtime evidence layer for Coding Agents. It lets the system run explicitly allowlisted validation commands, persist redacted runtime evidence, and link those results back to static code evidence and V2.12 patch plans.

The phase does not provide arbitrary command execution. Runtime evidence is a separate evidence layer; it supports or challenges static evidence but never replaces line-level source evidence.

## 2. Users and User Experience

Primary users:

- Coding Agent preparing to validate a patch plan.
- Maintainer reviewing whether a planned change has safe validation evidence.
- Test Agent checking whether a mapped test can be executed under policy.
- Code Reviewer comparing planned validation with actual allowlisted runtime results.

End-of-phase target experience:

1. User creates or reads a V2.12 patch plan.
2. User asks for runtime validation.
3. The service lists allowlisted commands and blocks everything else.
4. User runs one allowlisted command.
5. User receives a runtime evidence artifact with status, exit code, redacted logs, linked static evidence, and diagnosis hints.
6. Public output clearly says whether the command was executed, blocked, failed, timed out, or unavailable.

## 3. In Scope

- Runtime command registry with default-deny policy.
- Allowlisted command descriptors.
- Controlled execution of allowlisted local commands.
- Runtime run artifact persistence.
- Redacted stdout/stderr log artifacts.
- Runtime-static evidence alignment.
- HTTP/MCP/CLI read and run contracts.
- Real `data_service` focused pytest E2E.
- Structured blockers for unavailable or unsafe commands.

## 4. Out of Scope

- Arbitrary shell execution.
- Production environment execution.
- Non-allowlisted command execution.
- Credential-dependent commands.
- Raw log exposure.
- Treating runtime evidence as source evidence.
- Automatically applying a patch before validation.

## 5. Functional Requirements

### FR-001 Runtime Command Registry

The registry stores allowlisted commands:

- `command_id`
- command template
- working directory policy
- timeout
- purpose
- expected artifact type
- redaction policy
- linked patch plan or static evidence refs

Default policy is always `deny`.

### FR-002 Runtime Run

The run service accepts a `command_id`, validates it against the registry, executes only if allowlisted, captures result, redacts logs, and persists a runtime evidence artifact.

Non-allowlisted commands must return:

```text
RUNTIME_COMMAND_NOT_ALLOWLISTED
```

### FR-003 Runtime Evidence

Runtime evidence includes:

- `runtime_evidence_id`
- `command_id`
- `status`
- `exit_code`
- `started_at`
- `finished_at`
- redacted stdout/stderr refs
- linked static evidence
- linked patch plan refs
- diagnosis hints
- warnings and unresolved blockers

### FR-004 Public Contracts

HTTP:

```text
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/commands
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/coding-agent/runtime/runs/{run_id}
```

MCP:

```text
knowledge_code_runtime_commands
knowledge_code_runtime_run
knowledge_code_runtime_result
```

CLI:

```text
knowledge code coding-agent runtime commands
knowledge code coding-agent runtime run
knowledge code coding-agent runtime result
```

## 6. Completion Definition

V2.13 is complete when:

- default-deny behavior is proven;
- at least one allowlisted focused pytest command runs on real `data_service`;
- non-allowlisted commands are blocked with structured errors;
- redacted logs are persisted and public output contains no absolute paths, secrets, or raw tracebacks;
- runtime evidence links to static evidence or a V2.12 patch plan;
- HTTP/MCP/CLI parity passes;
- no open fatal or major audit finding remains.
