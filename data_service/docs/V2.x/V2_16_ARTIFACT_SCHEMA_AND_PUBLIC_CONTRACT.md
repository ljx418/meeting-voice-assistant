# V2.16 Artifact Schema 与 Public Contract

## 1. 设计原则

V2.16 所有 artifact 必须满足：

- 有 `schema_version`。
- 有 `workspace_id`、`codebase_id`、`snapshot_id` 或明确说明不依赖 snapshot。
- 有 `artifact_refs`。
- 有 `evidence` 或 `needs_review`。
- public payload 不暴露绝对路径、secret、raw traceback、raw provider body。
- accepted 结果必须可追踪。

## 2. ProviderCapability

```json
{
  "schema_version": "v2.16",
  "provider_id": "semantic:jedi",
  "provider_name": "jedi",
  "capability": "semantic_index",
  "kind": "local",
  "known": true,
  "configured": false,
  "execution_supported": false,
  "status": "provider_unavailable",
  "reason": "optional provider not installed",
  "evidence": [],
  "needs_review": [],
  "created_at": "..."
}
```

状态枚举：

```text
available
provider_unavailable
provider_unsupported
provider_missing_credential
provider_auth_failed
provider_timeout
provider_execution_failed
```

## 3. ProviderDecisionRecord

```json
{
  "schema_version": "v2.16",
  "decision_id": "decision_xxx",
  "capability": "semantic_index",
  "selected_provider": "python_ast",
  "decision": "accepted_baseline | provider_unavailable | out_of_scope",
  "reason": "...",
  "real_fixture_evidence": [],
  "unsupported_providers": [],
  "created_at": "..."
}
```

## 4. SemanticProviderFact

```json
{
  "schema_version": "v2.16",
  "fact_id": "semfact_xxx",
  "provider": "python_ast",
  "fact_type": "definition | reference | import | symbol | test_mapping",
  "path": "backend/app/api/v1/example.py",
  "line_range": [10, 20],
  "qualified_name": "module.Class.method",
  "confidence": 0.91,
  "status": "accepted | needs_review | blocked",
  "evidence_refs": ["code://..."],
  "needs_review": [],
  "extractor": "python_ast"
}
```

禁止：

- `runtime_call`
- `data_flow`
- `control_flow`
- `type_inferred_dependency`

## 5. RuntimeProfile

```json
{
  "schema_version": "v2.16",
  "profile_id": "pytest_file",
  "label": "Run one pytest file",
  "command_template": "python -m pytest {test_path} -q",
  "allowed_args": ["test_path"],
  "approval_required": false,
  "timeout_seconds": 30,
  "network": "disabled",
  "writes_source": false,
  "status": "available"
}
```

## 6. RuntimeProfileRun

```json
{
  "schema_version": "v2.16",
  "run_id": "run_xxx",
  "profile_id": "pytest_file",
  "status": "passed | failed | timeout | blocked",
  "exit_code": 0,
  "duration_ms": 1234,
  "linked_patch_plan_id": "patchplan_xxx",
  "linked_static_evidence": [],
  "logs": {
    "stdout_ref": "coding-agent://...stdout.redacted.txt",
    "stderr_ref": "coding-agent://...stderr.redacted.txt",
    "redacted": true
  },
  "error": null,
  "artifact_refs": []
}
```

## 7. WorkbenchV2Payload

```json
{
  "schema_version": "v2.16",
  "workbench_id": "workbench_xxx",
  "summary": {},
  "provider_matrix": [],
  "impact_map": {},
  "risk_lanes": [],
  "blocker_board": [],
  "runtime_results": [],
  "evidence_navigation": [],
  "exports": [],
  "artifact_refs": []
}
```

## 8. LargeProjectAbstractionReport

```json
{
  "schema_version": "v2.16",
  "report_id": "large_project_xxx",
  "project_profile": {},
  "document_claims": [],
  "code_facts": [],
  "pattern_evidence": [],
  "accepted_items": [],
  "needs_review_items": [],
  "blockers": [],
  "next_actions": []
}
```

## 9. PatchSandboxPreview

```json
{
  "schema_version": "v2.16",
  "preview_id": "preview_xxx",
  "source_patch_plan_id": "patchplan_xxx",
  "status": "draft_preview | ready_for_human_review | approved_for_apply | blocked",
  "mutates_source": false,
  "diff_ref": "coding-agent://.../diffs/preview.diff",
  "rollback_ref": "coding-agent://.../rollback/preview.json",
  "validation_profiles": [],
  "approval_required": true,
  "approval_id": null,
  "blockers": []
}
```

## 10. Public Contract

统一 envelope：

```json
{
  "ok": true,
  "schema_version": "v2.16",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": "...",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

错误 envelope：

```json
{
  "ok": false,
  "schema_version": "v2.16",
  "workspace_id": "...",
  "codebase_id": "...",
  "error": {
    "code": "PROVIDER_UNSUPPORTED",
    "message": "...",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 11. HTTP/MCP/CLI Parity

每个 read/build 接口必须比较：

- schema_version
- workspace_id
- codebase_id
- snapshot_id
- stable ids
- counts
- artifact_refs
- warnings
- unresolved
- error code

## 12. Redaction Rules

Public payload 不允许：

- 本机绝对路径。
- API key / token / secret。
- raw traceback。
- raw provider body。
- authorization header。
- external endpoint secret。
