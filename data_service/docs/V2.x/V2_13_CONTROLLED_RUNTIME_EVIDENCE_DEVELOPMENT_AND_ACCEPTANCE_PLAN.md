# V2.13 Development and Acceptance Plan: Controlled Runtime Evidence

## 1. Development Steps

1. Create pre-implementation audit report.
2. Add runtime command registry persistence.
3. Add default-deny policy gate.
4. Add controlled runner for allowlisted commands.
5. Add log redaction and redacted log artifact persistence.
6. Add runtime evidence schema and readback.
7. Add HTTP/MCP/CLI contracts.
8. Add focused tests, real `data_service` E2E, PRD review, false-green audit, and closure report.

## 2. Implementation Boundaries

Do not implement:

- arbitrary shell execution;
- credential-dependent execution;
- production command execution;
- automatic patch application;
- non-redacted public logs.

## 3. Required Tests

```text
test_v2_13_runtime_default_deny
test_v2_13_non_allowlisted_command_blocked
test_v2_13_allowlisted_pytest_run_persists_evidence
test_v2_13_runtime_logs_redacted
test_v2_13_runtime_static_evidence_alignment
test_v2_13_http_mcp_cli_parity
test_v2_13_public_payload_redaction
```

## 4. Real E2E

Use:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Required scenarios:

1. Try a non-allowlisted command and confirm it is blocked.
2. Run one allowlisted focused pytest command.
3. Read the persisted runtime evidence artifact.
4. Confirm logs are redacted.
5. Confirm runtime evidence links to static evidence or V2.12 patch plan refs.

## 5. Acceptance Criteria

- Registry exists and defaults to `deny`.
- Non-allowlisted command is not executed.
- Allowlisted command produces runtime evidence.
- Redacted logs are persisted.
- Public payload has no absolute path, secret, or raw traceback.
- HTTP/MCP/CLI return the same stable IDs, counts, warning counts, unresolved counts, and error codes.

## 6. False-Green Rejections

Reject acceptance if:

- a command executes without allowlist;
- tests are mocked but claimed as real runtime evidence;
- raw stdout/stderr is exposed publicly;
- runtime evidence overwrites static evidence;
- failed or timed-out command is reported as passed;
- only HTTP is tested while MCP/CLI are missing.

## 7. Closure Artifacts

Create:

```text
docs/V2.x/V2_13_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_13_ACCEPTANCE_AUDIT_REPORT.md
```
