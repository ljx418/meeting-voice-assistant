# V6-5 Agent Policy Matrix

文档状态：V6-5 detailed planning / policy matrix input。本文定义 Agent intent 准入与拒绝矩阵。

## 1. Intent Operation Policy

| Operation | Agent Intent | Handoff | Human Confirmation | Approval Gate | Notes |
| --- | --- | --- | --- | --- | --- |
| `workflow.instance.start` | allowed | required | required | optional | V6-4 controlled executor decides final execution |
| `station.rerun` | allowed | required | required | optional | old attempt retention remains V6-4 responsibility |
| `artifact.write` | allowed | required | required | required | append-only, no raw content in intent |
| `quality.evaluation.create` | allowed | required | required | required | append-only, target refs required |

## 2. Excluded Operations

Always denied for Agent intent:

```text
business.event.emit
context.update
workflow.template.publish
approval.respond
connector.call
external_llm.call
credential.rotate
credential.revoke
audit.export.mutate
```

## 3. Source Policy

| Source | Intent Generation | Durable Mutation |
| --- | --- | --- |
| `agent` | allowed for intent only | denied |
| `product_console` | may request handoff view | allowed only through V6-4 with human authorization |
| `approved_api` | may open handoff only with human authorization | allowed only through V6-4 boundary |

## 4. Required Denial Cases

```text
agent_auto_apply_denied
agent_auto_publish_denied
agent_auto_run_denied
agent_auto_rerun_denied
agent_excluded_operation_denied
agent_raw_credential_input_denied
agent_raw_prompt_input_denied
agent_raw_artifact_content_input_denied
agent_missing_minimax_evidence_blocked
agent_intent_parse_failed
agent_handoff_without_human_confirmation_blocked
source_agent_controlled_executor_mutation_denied
```

## 5. No False Green Policy

Passing this matrix means only:

```text
governed Agent execution intent pilot gate ready for review
```

It does not mean:

```text
Agent executor ready
autonomous workflow editing ready
full multi-Agent orchestration ready
```
