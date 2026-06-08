# V2.14 Development and Acceptance Plan: Incremental Intelligence

## 1. Development Steps

1. Create pre-implementation audit report.
2. Add fingerprint index persistence.
3. Add snapshot diff builder.
4. Add changed file/symbol/surface/doc detector.
5. Add artifact diff report.
6. Add task memory and drift timeline stores.
7. Add HTTP/MCP/CLI contracts.
8. Add focused tests, real E2E, PRD review, false-green audit, and closure report.

## 2. Required Tests

```text
test_v2_14_snapshot_diff_changed_file
test_v2_14_generated_at_not_identity_input
test_v2_14_changed_symbol_or_needs_review
test_v2_14_changed_surface_or_needs_review
test_v2_14_previous_artifacts_immutable
test_v2_14_task_memory_redaction
test_v2_14_drift_timeline_persists_events
test_v2_14_http_mcp_cli_parity
```

## 3. Real E2E

Use a controlled copy of:

```text
/Users/Zhuanz/Desktop/workspace/data_service
```

Scenarios:

1. Create snapshot A.
2. Modify one fixture file.
3. Create snapshot B.
4. Generate incremental diff.
5. Confirm changed file appears.
6. Confirm changed facts include evidence or `needs_review`.
7. Confirm prior artifacts are unchanged.

## 4. Acceptance Criteria

- Diff artifact is persisted and readable.
- Changed files are deterministic.
- `generated_at` does not affect identity.
- Changed facts are evidence-backed or `needs_review`.
- Historical artifacts are not silently overwritten.
- Task memory is redacted.
- Drift timeline records events.
- HTTP/MCP/CLI parity passes.

## 5. False-Green Rejections

Reject acceptance if:

- diff output is produced from mock-only data;
- old artifacts are silently rewritten;
- timestamp-only changes change identity;
- changed fact claims semantic meaning without evidence;
- task memory leaks absolute paths or secrets;
- full rebuild output is mislabeled as targeted incremental output.

## 6. Closure Artifacts

Create:

```text
docs/V2.x/V2_14_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_14_ACCEPTANCE_AUDIT_REPORT.md
```
