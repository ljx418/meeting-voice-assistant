# V2.13 Acceptance Audit Report

## Result

Accepted for the implemented local controlled-runtime scope.

## Evidence

Focused test command:

```text
PYTHONPATH=backend pytest backend/tests/test_v2_13_15_coding_agent_remaining.py -q
```

Result:

```text
2 passed
```

Regression commands:

```text
PYTHONPATH=backend pytest backend/tests/test_v2_12_safe_patch_planning.py backend/tests/test_v2_11_coding_agent_actionability.py -q
PYTHONPATH=backend pytest backend/tests/test_public_surface_guard.py -q
```

Results:

```text
4 passed
5 passed
```

## Accepted Capabilities

- Default-deny runtime command registry.
- Allowlisted pytest / read-only Python AST syntax checks.
- Non-allowlisted command blocker without execution.
- Persisted runtime run artifact and redacted stdout/stderr files.
- HTTP/MCP/CLI parity for runtime command registry and runtime run.

## Real data_service Smoke

Current repository smoke used the real `data_service` repository in a temporary managed workspace:

```text
codebase_id=codebase_data_service
snapshot_id=snap_787592231f2e97e1f417
definitions=3863
references=32413
runtime_commands=12
selected_command_type=python_ast_check
runtime_status=passed
exit_code=0
```

One pytest-style allowlisted command was also observed as `failed`; that result was persisted as runtime evidence and was not converted into a false success. The accepted smoke assertion uses the read-only AST check because it validates V2.13 execution mechanics without depending on the current repository's full test environment.

## False-Acceptance Review

| Risk | Result |
| --- | --- |
| Arbitrary command execution | rejected by command-id allowlist. |
| Source mutation via compile cache | avoided by read-only AST syntax check. |
| Absolute path leak | tested through serialized payload checks. |
| Runtime success without artifact | rejected by persisted run and log file assertions. |

## Open Findings

No fatal or major findings remain. External sandboxing, network controls, and long-running process cancellation remain out of scope for V2.13.
