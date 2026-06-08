# V2.15 Development and Acceptance Plan: Interactive Review Workbench

## 1. Development Steps

1. Create pre-implementation audit report.
2. Add workbench payload builder.
3. Add HTML renderer.
4. Add Mermaid graph renderer.
5. Add risk lanes and blocker board.
6. Add context export builder.
7. Add HTTP/MCP/CLI contracts.
8. Add focused tests, data_service E2E, large-project E2E, PRD review, false-green audit, and closure report.

## 2. Required Tests

```text
test_v2_15_workbench_payload_schema
test_v2_15_html_from_persisted_payload_only
test_v2_15_mermaid_node_integrity
test_v2_15_blockers_visible
test_v2_15_context_export_preserves_evidence
test_v2_15_public_payload_redaction
test_v2_15_data_service_workbench_e2e
test_v2_15_large_project_workbench_or_structured_blocker
test_v2_15_http_mcp_cli_parity
```

## 3. Real E2E

Use:

```text
/Users/Zhuanz/Desktop/workspace/data_service
/Users/Zhuanz/Desktop/workspace/harnessOS
```

If HarnessOS is unavailable, use another large local repository and record the replacement.

Scenarios:

1. Generate data_service workbench.
2. Open/read HTML report.
3. Validate Mermaid node integrity.
4. Confirm blockers and `needs_review` are visible.
5. Export task context and verify evidence preservation.
6. Generate large-project report or structured blocker.

## 4. Acceptance Criteria

- Workbench payload is persisted.
- HTML renders from payload only.
- Mermaid graph references persisted node IDs.
- Every visible fact resolves to backend artifact refs.
- Risk lanes and blocker board are visible.
- Context export preserves evidence.
- Public output is redacted and escaped.
- HTTP/MCP/CLI parity passes.

## 5. False-Green Rejections

Reject acceptance if:

- HTML creates facts not present in payload;
- Mermaid contains unpersisted node IDs;
- blockers are hidden;
- labels are unescaped;
- context export drops evidence but keeps recommendations;
- only mock data is used for real E2E;
- large-project failure is reported as accepted without structured blocker.

## 6. Closure Artifacts

Create:

```text
docs/V2.x/V2_15_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_15_ACCEPTANCE_AUDIT_REPORT.md
```
