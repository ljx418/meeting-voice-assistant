# V8 Schema Contract Pack

文档状态：V8-0 P0 contract pack / implementation-readiness input。

本文定义 V8 后续实现必须落成的 DTO / schema 合同。当前仍是文档合同，不代表代码已实现。

## 1. Common Rules

所有 V8 schema 必须遵守：

```text
additionalProperties=false
required fields explicit
ids are non-empty strings
timestamps are ISO-8601 strings
raw secret / raw prompt / raw file content / raw provider payload / raw artifact content fields forbidden
source=agent cannot authorize durable mutation
ready for review cannot be shortened to ready
```

公共字段：

```text
tenant_id
workspace_id
project_id
app_id
workflow_spec_id
workflow_instance_id
station_id
station_run_id
attempt_id
correlation_id
request_id
audit_ref
created_at
```

## 2. StationAgentDescriptor

Purpose:

```text
Declares the Agent assigned to one workflow station.
```

Required fields:

```text
agent_id
station_id
agent_name
role
goal
agent_runtime_profile_ref
model_profile_ref
memory_policy_ref
tool_policy_ref
skill_binding_refs
mcp_binding_refs
context_policy_ref
evidence_policy_ref
allowed_operations
forbidden_operations
source_policy
created_at
```

Rules:

```text
role and goal must be human-readable.
skill_binding_refs and mcp_binding_refs may be empty but must be explicit arrays.
source_policy must deny source=agent durable mutation.
Every workflow must include at least one descriptor with role=workflow_explainer or equivalent.
```

## 3. AgentRuntimeProfile

Required fields:

```text
profile_id
agent_id
runtime_kind: llm_only | tool_enabled | mcp_enabled | terminal_worker_handoff
max_attempts
timeout_policy_ref
kill_switch_policy_ref
requires_user_confirmation_for_mutation
high_risk_handoff_required
created_at
```

Rules:

```text
terminal_worker_handoff cannot be enabled before V8-5 design gate and V8-6 human high-risk decision.
runtime_kind does not imply Agent executor ready.
```

## 4. AgentModelProfile

Required fields:

```text
model_profile_id
provider
model_ref
provider_config_source
temperature_policy
prompt_template_refs
redaction_policy_ref
created_at
```

Forbidden fields:

```text
api_key
raw_provider_payload
raw_prompt
raw_response_payload
```

## 5. AgentMemoryPolicy

Required fields:

```text
memory_policy_id
agent_id
memory_mode: disabled | station_short_term | workflow_scoped_summary | approved_long_term_ref
readable_memory_refs
writable_memory_refs
retention_policy_ref
redaction_policy_ref
created_at
```

Rules:

```text
approved_long_term_ref requires explicit approval evidence.
Memory writes cannot construct runtime truth.
```

## 6. AgentToolPolicy

Required fields:

```text
tool_policy_id
agent_id
allowed_tools
denied_tools
high_risk_tools
requires_handoff_tools
policy_decision_ref
created_at
```

Rules:

```text
Durable mutation tools must require user_confirmed=true.
connector.call and external_llm.call are denied unless separately approved by a stage-specific policy.
```

## 7. AgentSkillBinding

Required fields:

```text
skill_binding_id
agent_id
skill_id
skill_version
scope
input_contract_ref
output_contract_ref
policy_decision_ref
created_at
```

Rules:

```text
Skill binding grants instruction capability, not permission to bypass tools or runtime policy.
```

## 8. AgentMcpBinding

Required fields:

```text
mcp_binding_id
agent_id
mcp_server_id
allowed_mcp_tools
denied_mcp_tools
resource_scope_refs
policy_decision_ref
evidence_required
created_at
```

Rules:

```text
MCP server calls require allowlist.
MCP resource reads must use scoped refs.
MCP calls must record evidence.
```

## 9. StationAgentRegistry

Required fields:

```text
registry_id
workflow_spec_id
workflow_version_ref
station_agent_descriptors
workflow_explainer_agent_id
validation_result
created_at
```

Rules:

```text
validation_result must fail if any station lacks AgentDescriptor.
validation_result must fail if workflow_explainer_agent_id is missing.
Registry is not runtime truth.
```

## 10. AgentCapabilityDecision

Required fields:

```text
decision_id
agent_id
station_id
operation
source
actor_type
allowed
requires_user_confirmation
requires_handoff
risk_level
policy_decision_ref
forbidden_reason
created_at
```

Rules:

```text
source=agent and operation durable_mutation implies allowed=false.
```

