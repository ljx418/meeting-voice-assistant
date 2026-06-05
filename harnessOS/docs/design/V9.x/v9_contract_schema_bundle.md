# V9 Contract Schema Bundle

文档状态：V9 P0 machine-readable contract plan / required before runtime implementation。

## 1. Purpose

本文件把 V9 自然语言合同收敛成 schema bundle。当前已落盘最小 P0 JSON Schema 到 `docs/design/V9.x/schemas/`，并可作为 V9-1 implementation-readiness audit 的机器可读输入。

## 2. Required Schemas

```text
agent_execution_policy.schema.json
agent_execution_envelope.schema.json
human_authorization_ref.schema.json
capability_resolver_decision.schema.json
approval_gate_decision.schema.json
kill_switch_decision.schema.json
timeout_policy.schema.json
rollback_descriptor.schema.json
execution_evidence.schema.json
orchestration_message.schema.json
artifact_lineage_record.schema.json
final_acceptance_dashboard.schema.json
```

P0 schema files currently present:

```text
docs/design/V9.x/schemas/agent_execution_policy.schema.json
docs/design/V9.x/schemas/agent_execution_envelope.schema.json
docs/design/V9.x/schemas/human_authorization_ref.schema.json
docs/design/V9.x/schemas/capability_resolver_decision.schema.json
docs/design/V9.x/schemas/approval_gate_decision.schema.json
docs/design/V9.x/schemas/kill_switch_decision.schema.json
docs/design/V9.x/schemas/timeout_policy.schema.json
docs/design/V9.x/schemas/rollback_descriptor.schema.json
docs/design/V9.x/schemas/execution_evidence.schema.json
docs/design/V9.x/schemas/orchestration_message.schema.json
docs/design/V9.x/schemas/artifact_lineage_record.schema.json
docs/design/V9.x/schemas/evidence_package.schema.json
docs/design/V9.x/schemas/high_risk_human_decision.schema.json
docs/design/V9.x/schemas/final_acceptance_dashboard.schema.json
```

## 3. Global Schema Rules

Every schema must define:

```text
schema_version
required fields
enum values
nullable rules
additionalProperties=false
redacted-ref-only fields
forbidden raw payload fields
versioning rule
backward compatibility rule
negative validation examples
```

Forbidden fields in every V9 evidence or execution schema:

```text
raw_prompt
raw_file_content
raw_provider_payload
raw_connector_payload
raw_artifact_content
api_key
bearer_token
signed_url
credential_raw_secret
```

## 4. Required Cross-Schema Invariants

```text
source=agent default durable mutation is always denied.
durable mutation requires user_confirmed=true OR valid human_authorization_ref.
high-risk durable mutation additionally requires approval_gate_ref.
target_refs must be operation-specific and non-empty.
payload_refs must be redacted refs only.
execution_evidence must reference execution_envelope_id and capability_decision_ref.
artifact_lineage_record must preserve producer_agent_id and producer_attempt_id.
final_acceptance_dashboard cannot count planning/spec docs as runtime evidence.
```

## 4.1 Schema Coverage Table

| PRD / Architecture Component | Schema | Negative Fixture |
| --- | --- | --- |
| AgentExecutionPolicy | `agent_execution_policy.schema.json` | unknown field fixture required before implementation |
| AgentExecutionEnvelope | `agent_execution_envelope.schema.json` | `source_agent_durable_mutation.json` |
| HumanAuthorizationRef | `human_authorization_ref.schema.json` | `expired_human_authorization_ref.json` |
| CapabilityResolverDecision | `capability_resolver_decision.schema.json` | source-agent mutation denial fixture |
| ExecutionEvidence | `execution_evidence.schema.json` | `raw_secret_in_evidence.json` |
| OrchestrationMessage | `orchestration_message.schema.json` | fan-in attribution fixture required before V9-3 |
| ArtifactLineageRecord | `artifact_lineage_record.schema.json` | `artifact_lineage_missing_producer_attempt.json` |
| EvidencePackage | `evidence_package.schema.json` | `v9_8_reject_planning_only_sample.json` |
| HighRiskHumanDecision | `high_risk_human_decision.schema.json` | expired/revoked decision fixture required before V9-2 |
| FinalAcceptanceDashboard | `final_acceptance_dashboard.schema.json` | planning-only dashboard rejection fixture required before V9-8 |

## 5. Negative Validation Examples

The schema bundle must include fixtures for:

```text
unknown_field_rejected
missing_schema_version_rejected
source_agent_durable_mutation_rejected
durable_mutation_without_user_confirmation_or_human_authorization_rejected
raw_secret_field_rejected
raw_prompt_field_rejected
empty_target_refs_rejected
wrong_operation_target_refs_rejected
expired_human_authorization_ref_rejected
artifact_lineage_missing_producer_attempt_rejected
```

P0 fixture files currently present:

```text
docs/design/V9.x/fixtures/schema-negative/source_agent_durable_mutation.json
docs/design/V9.x/fixtures/schema-negative/expired_human_authorization_ref.json
docs/design/V9.x/fixtures/schema-negative/raw_secret_in_evidence.json
docs/design/V9.x/fixtures/schema-negative/artifact_lineage_missing_producer_attempt.json
docs/design/V9.x/fixtures/evidence/v9_1_contract_freeze_sample.json
docs/design/V9.x/fixtures/evidence/v9_8_reject_planning_only_sample.json
```

## 6. Acceptance Gate

V9 implementation may not start from this bundle until:

```text
all required JSON Schema files exist.
all schemas parse.
negative fixtures fail as expected.
No False Green scan PASS.
redaction forbidden field scan PASS.
```
