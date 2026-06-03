# V4.x Schema Audit Pack

文档状态：V4.x schema 审计汇总包。

用途：把当前 V4.x 统一体验相关 schema 收纳到一个文件，方便独立审计。本文只汇总 schema 与审计问题，不声明 runtime ready。

当前允许基线：

```text
V4.6 complete: governed Agent workflow builder UX ready for dev/local validation.
```

仍禁止声明：

```text
complete Workflow Studio ready
complete AgentTalkWindow ready
Agent executor ready
controlled executor ready
production-ready external app support
full multi-Agent orchestration ready
autonomous workflow editing ready
```

## 1. 审计目标

请重点审计：

1. schema 是否足以表达 Mission Console、Workflow Blueprint、Runtime Report、Review Console、Evidence Chain 的 read model。
2. schema 是否会被误用为 runtime truth。
3. schema 是否允许 Agent 绕过 user confirmation。
4. schema 是否缺少 source_refs、redaction_status、policy_decision、risk_flags、user_confirmed 等治理字段。
5. schema 是否能防止 Drawio / HTML Report / EventBridge payload 构造 truth。
6. schema 是否能区分 supported、partial、planned、unsupported，避免 false green。
7. schema 是否还缺 Runtime Capability Matrix 与 WorkflowSpec Registry。

## 1.1 Schema Strictness Revision

本轮修订已收紧以下合同，供审计优先核对：

```text
target_refs 不再允许 arbitrary object，已拆成 workflow_spec_id / workflow_instance_id / station_id / station_run_id / artifact_id / evidence_id / handoff_id / report_id，additionalProperties=false。
operation 已改成 enum，覆盖 workflow.spec.generate / workflow.patch.propose / workflow.patch.apply / workflow.template.publish / workflow.instance.start / station.rerun / approval.respond / context.update / evidence.show / report.open / drawio.open / handoff.open。
station_states items 必须引用 station_state.schema.json。
available_actions 增加 source_agent_mutation_guard，mutation action 必须 agent_executable=false，user_confirmed_only 必须 requires_user_confirmation=true。
evidence_report.schema.json 增加 created_at / created_by / source_refs / readonly=true / report_actions=view|export|open_handoff。
新增 runtime_capability_matrix.schema.json，用于区分 supported / partial / planned / unsupported。
新增 workflow_spec_registry.schema.json，用于登记 spec hash 与 runtime refs，并明确不替代 WorkflowDraft / WorkflowVersion runtime truth。
```

Runtime truth 边界：

```text
WorkflowSpec Registry 不能替代 WorkflowDraft / WorkflowVersion。
Drawio 不能构造 runtime truth。
HTML Report 不能构造 runtime truth。
EventBridge payload 不能构造 runtime truth。
Report Schema 是 read model。
Interaction Orchestrator 不直接写 runtime。
Experience State Machine 是 UX read model。
```

## 2. Existing Schema Inventory

当前已有 schema：

```text
docs/design/V4.x/schemas/artifact_report.schema.json
docs/design/V4.x/schemas/available_actions.schema.json
docs/design/V4.x/schemas/evidence_report.schema.json
docs/design/V4.x/schemas/experience_state.schema.json
docs/design/V4.x/schemas/handoff_request.schema.json
docs/design/V4.x/schemas/interaction_intent.schema.json
docs/design/V4.x/schemas/interaction_state_projection.schema.json
docs/design/V4.x/schemas/operation.schema.json
docs/design/V4.x/schemas/quality_report.schema.json
docs/design/V4.x/schemas/review_action.schema.json
docs/design/V4.x/schemas/runtime_capability_matrix.schema.json
docs/design/V4.x/schemas/station_report.schema.json
docs/design/V4.x/schemas/station_state.schema.json
docs/design/V4.x/schemas/target_refs.schema.json
docs/design/V4.x/schemas/workflow_report.schema.json
docs/design/V4.x/schemas/workflow_spec_registry.schema.json
```

## 3. Current Schemas

### 3.1 artifact_report.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/artifact_report.schema.json",
  "title": "V4.x Artifact Report DTO",
  "type": "object",
  "additionalProperties": false,
  "required": ["artifact_id", "artifact_kind", "producer_station_id", "lineage_refs", "redaction_status"],
  "properties": {
    "artifact_id": { "type": "string", "minLength": 1 },
    "artifact_kind": { "type": "string", "minLength": 1 },
    "producer_station_id": { "type": "string" },
    "lineage_refs": { "type": "array", "items": { "type": "string" } },
    "redaction_status": { "type": "string", "enum": ["redacted"] }
  }
}
```

审计关注：

```text
是否需要 source_refs？
是否需要 artifact content redaction policy？
是否需要明确 raw_artifact_content 不允许出现？
```

### 3.2 available_actions.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/available_actions.schema.json",
  "title": "V4.x Available Action DTO",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "action_id",
    "operation",
    "requires_user_confirmation",
    "agent_executable",
    "risk_flags",
    "policy_decision"
  ],
  "properties": {
    "action_id": { "type": "string", "minLength": 1 },
    "operation": { "type": "string", "minLength": 1 },
    "requires_user_confirmation": { "type": "boolean" },
    "agent_executable": { "type": "boolean" },
    "risk_flags": { "type": "array", "items": { "type": "string" } },
    "policy_decision": {
      "type": "string",
      "enum": ["read_only", "proposal_only", "handoff_only", "user_confirmed_only", "approval_gated_future", "blocked"]
    }
  }
}
```

审计关注：

```text
agent_executable 是否必须对 mutation 永远为 false？
是否需要 operation allowlist？
是否需要 forbidden source=agent mutation 的机器可读断言？
```

### 3.3 evidence_report.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/evidence_report.schema.json",
  "title": "V4.x Evidence Report DTO",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "proposal_id",
    "handoff_id",
    "user_confirmed",
    "operation_type",
    "runtime_result_ref",
    "risk_flags",
    "policy_decision",
    "correlation_id",
    "redaction_status",
    "review_status"
  ],
  "properties": {
    "proposal_id": { "type": "string" },
    "handoff_id": { "type": "string" },
    "user_confirmed": { "type": "boolean" },
    "operation_type": { "type": "string", "minLength": 1 },
    "runtime_result_ref": { "type": "string" },
    "risk_flags": { "type": "array", "items": { "type": "string" } },
    "policy_decision": { "type": "string", "minLength": 1 },
    "correlation_id": { "type": "string" },
    "redaction_status": { "type": "string", "enum": ["redacted"] },
    "review_status": { "type": "string", "minLength": 1 }
  }
}
```

审计关注：

```text
是否应强制 policy_decision enum？
是否需要 created_at / created_by？
是否需要 source_refs？
是否需要 evidence 只读声明字段？
```

### 3.4 experience_state.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/experience_state.schema.json",
  "title": "V4.x Experience State",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "state_id",
    "label",
    "description",
    "available_actions",
    "blocked_actions",
    "requires_user_confirmation",
    "risk_level",
    "evidence_required",
    "visible_in"
  ],
  "properties": {
    "state_id": { "type": "string", "minLength": 1 },
    "label": { "type": "string", "minLength": 1 },
    "description": { "type": "string", "minLength": 1 },
    "available_actions": { "type": "array", "items": { "type": "string" } },
    "blocked_actions": { "type": "array", "items": { "type": "string" } },
    "requires_user_confirmation": { "type": "boolean" },
    "risk_level": { "type": "string", "enum": ["low", "medium", "high"] },
    "evidence_required": { "type": "boolean" },
    "visible_in": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": [
          "mission_console",
          "workflow_blueprint",
          "runtime_report",
          "review_console",
          "evidence_chain",
          "tui",
          "drawio",
          "html_report",
          "thin_web_console"
        ]
      },
      "minItems": 1
    }
  }
}
```

审计关注：

```text
是否需要 state_scope: workflow / station / evidence？
是否需要 allowed transition 表？
当前 schema 是 state 描述，不是 transition validator，是否足够？
```

### 3.5 handoff_request.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/handoff_request.schema.json",
  "title": "V4.x Handoff Request",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "handoff_id",
    "source",
    "target_console",
    "operation",
    "requires_user_confirmation",
    "risk_flags",
    "policy_decision"
  ],
  "properties": {
    "handoff_id": { "type": "string", "minLength": 1 },
    "source": { "type": "string", "minLength": 1 },
    "target_console": { "type": "string", "enum": ["mission_console", "review_console", "thin_web_console"] },
    "operation": { "type": "string", "minLength": 1 },
    "requires_user_confirmation": { "type": "boolean" },
    "risk_flags": { "type": "array", "items": { "type": "string" } },
    "policy_decision": { "type": "string", "minLength": 1 }
  }
}
```

审计关注：

```text
是否需要 source enum？
是否需要 source=agent mutation guard？
是否需要 target_panel / target_ref？
```

### 3.6 interaction_intent.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/interaction_intent.schema.json",
  "title": "V4.x Interaction Intent",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "intent_id",
    "source",
    "actor_type",
    "operation",
    "requested_action",
    "target_refs"
  ],
  "properties": {
    "intent_id": { "type": "string", "minLength": 1 },
    "source": {
      "type": "string",
      "enum": ["mission_console", "tui", "thin_web_console", "html_report", "agent", "future_business_app"]
    },
    "actor_type": { "type": "string", "enum": ["human", "agent", "service_account"] },
    "operation": { "type": "string", "minLength": 1 },
    "natural_language_goal": { "type": "string" },
    "requested_action": { "type": "string", "minLength": 1 },
    "target_refs": {
      "type": "object",
      "additionalProperties": { "type": "string" }
    },
    "user_confirmed": { "type": "boolean" }
  }
}
```

审计关注：

```text
是否需要 operation enum？
是否需要 source=agent + user_confirmed 仍不可 mutation 的规则？
target_refs 是否过宽？
```

### 3.7 interaction_state_projection.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/interaction_state_projection.schema.json",
  "title": "V4.x Interaction State Projection",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "workflow_state",
    "station_states",
    "evidence_state",
    "available_actions",
    "blocked_actions",
    "source_refs"
  ],
  "properties": {
    "workflow_state": { "type": "string", "minLength": 1 },
    "station_states": { "type": "array", "items": { "type": "object" } },
    "evidence_state": { "type": "string", "minLength": 1 },
    "available_actions": { "type": "array", "items": { "$ref": "available_actions.schema.json" } },
    "blocked_actions": { "type": "array", "items": { "type": "string" } },
    "source_refs": { "type": "array", "items": { "type": "string" } }
  }
}
```

审计关注：

```text
station_states items 是否过宽？
是否需要 generated_at？
是否需要 refresh_generation？
是否需要 stale_reasons？
```

### 3.8 quality_report.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/quality_report.schema.json",
  "title": "V4.x Quality Report DTO",
  "type": "object",
  "additionalProperties": false,
  "required": ["quality_id", "target_ref", "status", "findings", "redaction_status"],
  "properties": {
    "quality_id": { "type": "string", "minLength": 1 },
    "target_ref": { "type": "string", "minLength": 1 },
    "status": { "type": "string", "enum": ["passed", "warning", "failed", "unknown"] },
    "findings": { "type": "array", "items": { "type": "string" } },
    "redaction_status": { "type": "string", "enum": ["redacted"] }
  }
}
```

审计关注：

```text
是否需要 rule_id / quality_gate_id？
是否需要 severity？
是否需要 evidence_ref？
```

### 3.9 station_report.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/station_report.schema.json",
  "title": "V4.x Station Report DTO",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "station_id",
    "station_run_id",
    "state",
    "attempt_count",
    "latest_attempt_id",
    "input_artifact_refs",
    "output_artifact_refs",
    "quality_status",
    "error_summary",
    "available_actions"
  ],
  "properties": {
    "station_id": { "type": "string", "minLength": 1 },
    "station_run_id": { "type": "string" },
    "state": { "type": "string", "minLength": 1 },
    "attempt_count": { "type": "integer", "minimum": 0 },
    "latest_attempt_id": { "type": ["string", "null"] },
    "input_artifact_refs": { "type": "array", "items": { "type": "string" } },
    "output_artifact_refs": { "type": "array", "items": { "type": "string" } },
    "quality_status": { "type": "string" },
    "error_summary": { "type": ["string", "null"] },
    "available_actions": { "type": "array", "items": { "type": "object" } }
  }
}
```

审计关注：

```text
state 是否应引用 experience_state？
available_actions items 是否应引用 available_actions schema？
是否需要 stale_reason / downstream_stale_refs？
```

### 3.10 workflow_report.schema.json

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://harnessos.dev/schemas/v4.x/workflow_report.schema.json",
  "title": "V4.x Workflow Report DTO",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "report_id",
    "workflow_spec_ref",
    "workflow_version_ref",
    "workflow_instance_ref",
    "generated_at",
    "source_refs",
    "stations",
    "artifacts",
    "quality",
    "evidence",
    "available_actions",
    "redaction_status"
  ],
  "properties": {
    "report_id": { "type": "string", "minLength": 1 },
    "workflow_spec_ref": { "type": "string" },
    "workflow_version_ref": { "type": "string" },
    "workflow_instance_ref": { "type": "string" },
    "generated_at": { "type": "string" },
    "source_refs": { "type": "array", "items": { "type": "string" } },
    "stations": { "type": "array", "items": { "type": "object" } },
    "artifacts": { "type": "array", "items": { "type": "object" } },
    "quality": { "type": "array", "items": { "type": "object" } },
    "evidence": { "type": "array", "items": { "type": "object" } },
    "available_actions": { "type": "array", "items": { "type": "object" } },
    "redaction_status": { "type": "string", "enum": ["redacted"] }
  }
}
```

审计关注：

```text
stations / artifacts / quality / evidence / available_actions 是否应使用 $ref？
是否需要 freshness / stale_reasons？
是否需要 explicit read_only=true？
```

## 4. Missing Schemas For Next V4 Stage

下一阶段 V4-U5A 应新增：

```text
docs/design/V4.x/schemas/runtime_capability_matrix.schema.json
docs/design/V4.x/schemas/workflow_spec_registry.schema.json
```

### 4.1 Runtime Capability Matrix 应覆盖

```text
capability_id
status: supported | partial | planned | unsupported
stage_owner
evidence_refs
agent_executable
requires_user_confirmation
false_green_risk
notes
```

审计重点：

```text
Agent executor 必须是 unsupported。
production external app support 必须是 unsupported 或 planned。
full multi-Agent orchestration 不能被 V4.3/V4.4 deterministic evidence 误标为 supported。
```

### 4.2 WorkflowSpec Registry 应覆盖

```text
spec_id
spec_hash
schema_version
source
created_by
generated_by
validated_at
linked_draft_id
linked_version_id
linked_instance_id
compatibility_status
runtime_truth_boundary
```

审计重点：

```text
WorkflowSpec Registry 不能替代 WorkflowDraft / WorkflowVersion。
Registry 不能从 Drawio / HTML Report / EventBridge payload 构造 truth。
```

## 5. Suggested Audit Questions

建议给 ChatGPT 的审计问题：

```text
1. 当前 schema 是否过宽，尤其是 target_refs、station_states、available_actions items？
2. 哪些 schema 应该用 $ref 而不是 object？
3. 哪些字段必须加入 source_refs / generated_at / stale_reasons / read_only？
4. 是否需要统一 policy_decision enum？
5. 是否需要在 schema 层表达 source=agent cannot execute mutation？
6. 是否需要在 schema 层禁止 raw payload / token / secret 字段？
7. Runtime Capability Matrix 如何避免 false green？
8. WorkflowSpec Registry 是否会被误用为 runtime truth？
```
