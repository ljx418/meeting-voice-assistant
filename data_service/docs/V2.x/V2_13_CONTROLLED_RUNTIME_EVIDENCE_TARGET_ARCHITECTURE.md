# V2.13 Target Architecture: Controlled Runtime Evidence

## 1. Architecture Position

V2.13 sits after V2.12 Safe Patch Planning.

```text
V2.12 Patch Plan
  -> Runtime Command Registry
  -> Allowlist Policy Gate
  -> Controlled Runner
  -> Redaction Pipeline
  -> Runtime Evidence Store
  -> HTTP / MCP / CLI
```

The runtime layer is a consumer of patch plans and static evidence. It is not a source-code editor and not a replacement for static code evidence.

## 2. Components

### 2.1 Runtime Command Registry

Stores allowlisted command descriptors. The default registry policy is `deny`.

Descriptor fields:

- `command_id`
- `label`
- `command`
- `working_directory_policy`
- `timeout_seconds`
- `purpose`
- `allowed_args`
- `redaction_policy`
- `linked_artifact_refs`

### 2.2 Allowlist Policy Gate

Validates every runtime request before execution.

Rules:

- command must match a known `command_id`;
- raw shell command strings are rejected unless they exactly match an allowlisted descriptor;
- working directory must resolve under the codebase root or configured safe workspace;
- timeout is mandatory;
- failure must be structured and public-safe.

### 2.3 Controlled Runner

Executes the allowlisted command with bounded timeout. It captures exit code, duration, stdout, stderr, and execution status.

The runner must not:

- run non-allowlisted commands;
- execute in production environments;
- load credentials;
- mutate source artifacts beyond normal test/cache side effects.

### 2.4 Redaction Pipeline

Transforms stdout/stderr into public-safe log artifacts. It must redact:

- absolute local paths;
- secrets and tokens;
- authorization headers;
- raw provider or system tracebacks when unsafe;
- environment variable dumps.

### 2.5 Runtime Evidence Store

Persists:

```text
workspace/assets/codebase/{codebase_id}/coding_agent/runtime/
  command_registry.json
  runs/{run_id}.json
  logs/{run_id}.stdout.redacted.txt
  logs/{run_id}.stderr.redacted.txt
```

## 3. Public Error Codes

```text
RUNTIME_COMMAND_REGISTRY_NOT_FOUND
RUNTIME_COMMAND_NOT_ALLOWLISTED
RUNTIME_WORKDIR_NOT_ALLOWED
RUNTIME_COMMAND_TIMEOUT
RUNTIME_LOG_REDACTION_FAILED
RUNTIME_RUN_NOT_FOUND
RUNTIME_EVIDENCE_SCHEMA_INVALID
```

## 4. Safety Boundaries

- Runtime evidence is separate from static evidence.
- Runtime success does not imply the patch is correct.
- Runtime failure does not automatically invalidate static evidence.
- Public payloads must be redacted.
- V2.13 may run only allowlisted commands.

## 5. Target User Experience

After V2.13, a user can inspect a patch plan, ask which validation commands are safe, run an allowlisted local test, and review redacted runtime evidence linked to the original static evidence and patch plan.
