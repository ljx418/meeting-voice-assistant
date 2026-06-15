# V2.18-V2.24 Artifact Schema 与 Public Contract

## 1. 文档目标

本文件把 V2.18-V2.24 平台产品化路线图中的关键产物、公共响应、错误形态和 HTTP/MCP/CLI parity 约束固定下来，避免后续实现阶段只按高层 PRD 开发而产生规格漂移。

## 2. 通用 Artifact Envelope

所有 V2.18-V2.24 新增 artifact 必须包含：

```json
{
  "schema_version": "v2.18",
  "artifact_type": "platform_console | artifact_contract | mcp_tool_catalog | incremental_build_plan | provider_capability | governance_rule | ci_readiness",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "artifact_id": "string",
  "created_at": "ISO-8601",
  "source_artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "needs_review": [],
  "metadata": {}
}
```

验收要求：

- `schema_version` 必填。
- `artifact_type` 必须在枚举内。
- `source_artifact_refs` 必须能解析到真实 artifact 或明确 unresolved reason。
- `evidence_refs` 如果存在，必须能解析到 repo-relative path / line range / artifact id。
- public payload 不得包含本机绝对路径、secret、raw traceback。

## 3. V2.18 Console Artifact

```json
{
  "artifact_type": "platform_console",
  "summary": {
    "project_name": "string",
    "latest_snapshot_id": "string",
    "status": "ready | needs_review | blocked",
    "top_next_actions": []
  },
  "panels": [
    {
      "panel_id": "overview",
      "title": "项目总览",
      "source_artifact_refs": [],
      "visible_findings": [],
      "next_actions": []
    }
  ],
  "view_refs": []
}
```

禁止：

- Console 自己推断新事实。
- Console 隐藏 blocker / unresolved。
- HTML renderer 输出 artifact 中不存在的 capability、risk 或 recommendation。

## 4. V2.19 Artifact Contract Registry

```json
{
  "artifact_type": "artifact_contract",
  "contracts": [
    {
      "artifact_family": "architecture_context_pack_v3",
      "schema_version": "v2.19",
      "required_fields": [],
      "row_artifact": false,
      "summary_artifact": true,
      "validator": "string",
      "status": "covered | partial | missing"
    }
  ],
  "validation_summary": {
    "checked_count": 0,
    "passed_count": 0,
    "failed_count": 0
  }
}
```

验收要求：

- `.jsonl` 必须逐行是 JSON row。
- summary 必须使用 `.json`。
- validator 不能自动修正事实，只能报告 pass/fail/warning。

## 5. V2.20 MCP Tool Catalog

```json
{
  "artifact_type": "mcp_tool_catalog",
  "tool_count": 156,
  "groups": [
    {
      "group_id": "coding_agent",
      "tools": []
    }
  ],
  "tools": [
    {
      "tool_name": "knowledge_code_task_plan",
      "group_id": "coding_agent",
      "goal_tags": ["coding_task_preparation"],
      "preconditions": [],
      "outputs": [],
      "failure_modes": [],
      "next_actions": []
    }
  ],
  "workflow_guides": [
    {
      "goal": "coding_task_preparation",
      "steps": []
    }
  ]
}
```

验收要求：

- catalog 必须从当前 MCP registry 生成，不手写静态列表。
- 不得推荐不存在、deprecated 或 disabled 的 tool。
- 每个推荐链必须有前置条件和失败恢复建议。

## 6. V2.21 Incremental Build Plan

```json
{
  "artifact_type": "incremental_build_plan",
  "from_snapshot_id": "string",
  "to_snapshot_id": "string",
  "changed_files": [],
  "reused_artifacts": [],
  "refreshed_artifacts": [],
  "invalidated_artifacts": [],
  "scan_budget": {
    "max_files": 0,
    "max_loc": 0,
    "duration_ms": 0
  },
  "fallback_reason": "full_rebuild_required | null"
}
```

验收要求：

- 每个 cache decision 必须有 reason。
- 如果全量刷新，必须说明原因。
- 不允许静默跳过 changed file。

## 7. V2.22 Provider Capability Contract

```json
{
  "artifact_type": "provider_capability",
  "providers": [
    {
      "provider_id": "python_ast",
      "kind": "semantic",
      "mandatory": true,
      "health_known": true,
      "configured": true,
      "execution_supported": true,
      "status": "ready"
    }
  ],
  "unavailable": [
    {
      "provider_id": "tree_sitter",
      "status": "unavailable",
      "reason": "not_configured"
    }
  ]
}
```

验收要求：

- AST baseline 必须 ready。
- optional provider unavailable 不得记为 accepted。
- health-known 不等于 execution-ready。

## 8. V2.23 Governance Rule Artifact

```json
{
  "artifact_type": "governance_rule",
  "rule_id": "string",
  "target_type": "finding | claim | evidence | context_item | tool_guidance",
  "target_id": "string",
  "status": "draft | approved | rejected | revoked",
  "effect": "read_time_overlay",
  "applied_to": [],
  "source_artifact_hash_before": "string",
  "source_artifact_hash_after": "string"
}
```

验收要求：

- missing target 必须拒绝。
- approve 后 read output 出现 `applied_rules`。
- revoke 后 read output 不再应用。
- 原始 artifact hash 不变。

## 9. V2.24 CI Readiness Artifact

```json
{
  "artifact_type": "ci_readiness",
  "test_layers": {
    "unit": "passed | failed | skipped",
    "contract": "passed | failed | skipped",
    "artifact": "passed | failed | skipped",
    "frontend": "passed | failed | skipped",
    "real_repo_e2e": "passed | failed | skipped"
  },
  "warning_budget": {
    "current": 0,
    "budget": 0,
    "over_budget": false
  },
  "security_gate": {
    "redaction": "passed | failed",
    "absolute_path_leak_count": 0,
    "secret_leak_count": 0
  }
}
```

验收要求：

- skipped test 不能被写成 passed。
- release readiness 必须引用真实 test command。
- redaction failure 阻塞 release gate。

## 10. Public Envelope

HTTP/MCP/CLI read 输出应统一：

```json
{
  "ok": true,
  "schema_version": "v2.18",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

错误输出：

```json
{
  "ok": false,
  "schema_version": "v2.18",
  "workspace_id": "string",
  "codebase_id": "string",
  "snapshot_id": null,
  "error": {
    "code": "ARTIFACT_SCHEMA_INVALID",
    "message": "string",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 11. 公共错误码

```text
PLATFORM_CONSOLE_NOT_BUILT
ARTIFACT_SCHEMA_INVALID
ARTIFACT_REF_UNRESOLVED
MCP_TOOL_CATALOG_NOT_BUILT
MCP_TOOL_NOT_FOUND
WORKFLOW_GUIDE_NOT_FOUND
INCREMENTAL_DIFF_NOT_FOUND
INCREMENTAL_BUILD_UNSAFE_REUSE
PROVIDER_PLUGIN_UNAVAILABLE
PROVIDER_EXECUTION_UNSUPPORTED
GOVERNANCE_TARGET_NOT_FOUND
GOVERNANCE_RULE_REVOKED
CI_READINESS_NOT_BUILT
PUBLIC_PAYLOAD_REDACTION_FAILED
```

## 12. HTTP/MCP/CLI Parity

每个阶段至少验证：

- same `schema_version`
- same `workspace_id`
- same `codebase_id`
- same `snapshot_id`
- same `artifact_refs` count
- same warnings/unresolved count
- same status/error code
