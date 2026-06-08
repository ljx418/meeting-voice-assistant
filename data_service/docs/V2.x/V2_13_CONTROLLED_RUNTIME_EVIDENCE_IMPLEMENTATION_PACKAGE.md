# V2.13 Implementation Package: Controlled Runtime Evidence

## 1. Goal

Collect runtime/test/log evidence under strict allowlist control.

Runtime evidence is a separate evidence layer. It must not overwrite static code evidence.

## 2. Development Plan

Implement:

- runtime command registry;
- default-deny policy;
- allowlisted command execution descriptor;
- test run artifact;
- redacted log artifact;
- runtime-static alignment report.

## 3. Artifact Outputs

```text
coding_agent/runtime/command_registry.json
coding_agent/runtime/runs/{run_id}.json
coding_agent/runtime/logs/{run_id}.redacted.txt
```

## 4. Public Interface Targets

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
knowledge code runtime commands
knowledge code runtime run
knowledge code runtime result
```

## 5. Acceptance Plan

- Default-deny registry blocks unlisted commands.
- Non-allowlisted command returns `RUNTIME_COMMAND_NOT_ALLOWLISTED`.
- At least one allowlisted data_service focused pytest command runs and persists runtime evidence.
- Logs are redacted and public payload has no secrets, absolute paths, or raw tracebacks.
- Runtime evidence links to static evidence without replacing it.

## 6. Stop Conditions

Stop if:

- arbitrary shell command execution is required;
- credentials are needed;
- raw logs must be exposed;
- runtime output is used to claim static source evidence.
