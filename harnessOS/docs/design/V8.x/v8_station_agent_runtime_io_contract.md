# V8 Station Agent Runtime I/O Contract

文档状态：V8-0 P0 runtime I/O contract / implementation-readiness input。

本文定义 V8-4 工位 Agent 运行试点必须使用的输入、输出、状态和证据合同。

## 1. Runtime Principle

```text
Station Agent Runtime is a governed pilot.
It does not prove Agent executor ready.
It does not allow source=agent direct durable mutation.
It uses user-confirmed workflow run boundaries inherited from V7/V6.
```

## 2. StationAgentRunRequest

Required fields:

```text
run_request_id
workflow_spec_id
workflow_instance_id
station_id
station_run_id
attempt_id
agent_descriptor_ref
context_envelope_ref
capability_decision_ref
user_confirmed
source
actor_type
correlation_id
request_id
created_at
```

Rules:

```text
user_confirmed must be true for durable workflow run or rerun handoff.
source=agent must be denied for durable mutation.
```

## 3. StationAgentContextEnvelope

Required fields:

```text
context_envelope_id
agent_id
station_id
workflow_context_refs
upstream_artifact_refs
evidence_refs
memory_refs
prompt_template_ref
redaction_status
context_scope
created_at
```

Forbidden fields:

```text
raw_prompt
raw_file_content
raw_artifact_content
raw_provider_payload
raw_connector_payload
api_key
bearer_token
signed_url
```

Rules:

```text
context_scope must be station_scoped or workflow_scoped_readonly.
Any cross-station context must be referenced by artifact/evidence refs, not raw content.
```

## 4. StationAgentRunResult

Required fields:

```text
run_result_id
agent_id
station_id
station_run_id
attempt_id
status: PASS | PARTIAL | FAIL | BLOCKED
output_artifact_refs
quality_refs
evidence_refs
llm_invocation_refs
tool_call_refs
mcp_call_refs
capability_decision_refs
redaction_status
created_at
```

Rules:

```text
LLM-backed output requires llm_invocation_refs.
Tool-backed output requires tool_call_refs.
MCP-backed output requires mcp_call_refs.
```

## 5. AgentInvocationEvidence

Required fields:

```text
invocation_id
agent_id
station_id
provider
model_ref
provider_config_source
prompt_template_ref
input_artifact_refs
output_artifact_refs
redaction_status
correlation_id
request_id
created_at
```

Forbidden fields:

```text
raw_prompt
raw_response
raw_provider_payload
api_key
token
```

## 6. V8-4 Local Document Agent Map

Minimum pilot workflow:

```text
MissionAgent -> captures user goal and explains state.
PlannerAgent -> generates WorkflowSpec / Diff / station-agent registry.
ScannerAgent -> reads authorized Markdown path through read-only capability.
FolderSummaryAgent -> generates per-folder summaries.
OverviewAgent -> generates overview summary.
QualityAgent -> creates quality report.
EvidenceAgent -> writes evidence chain.
WorkflowExplainerAgent -> explains workflow result, risks and evidence.
```

PASS requires:

```text
station_agent_descriptor_count == station_count
workflow_explainer_agent_exists=true
agent_invocation_count >= station_count requiring LLM/tool work
scanner_actual_read_count > 0
folder_summaries_generated=PASS
overview_summary_generated=PASS
quality_report_generated=PASS
evidence_chain_generated=PASS
redaction_scan=PASS
claim_scan=PASS
```

