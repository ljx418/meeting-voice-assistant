# V6-5 MiniMax Intent Invocation Model

文档状态：V6-5 detailed planning / MiniMax invocation model。本文定义 V6-5 MiniMax 验收边界。

## 1. Provider Requirement

V6-5 PASS requires real MiniMax invocation evidence.

```text
provider=minimax
credential_ref=env://MINIMAX_API_KEY
base_url_ref=env://MINIMAX_BASE_URL
model_ref from env/config, default MiniMax-M2.1
```

如果 `MINIMAX_API_KEY` 缺失或为占位值，V6-5 必须 BLOCKED，不能 PASS。

## 2. Input Contract

MiniMax receives only redacted references:

```text
redacted_runtime_status_ref
redacted_failure_summary_ref
allowed_operations_ref
target_refs
policy_context_ref
prompt_template_ref
```

MiniMax must not receive:

```text
raw prompt
raw credential
raw artifact content
raw connector payload
Authorization
Bearer
secret
capability_token
subscription_token
```

## 3. Output Contract

MiniMax output must be parsed into AgentExecutionIntent JSON. If parsing fails:

```text
policy_decision=blocked_missing_provider_evidence or deny
blocked_reason=intent_parse_failed
handoff is not created
```

## 4. Evidence Redaction

Evidence may include:

```text
provider
model_ref
provider_config_source
prompt_template_ref
input_runtime_snapshot_ref
output_intent_ref
token_usage_summary if available
redaction_status
correlation_id
```

Evidence must not include raw request or raw response body. Redacted summaries are allowed.

## 5. No False Green Boundary

MiniMax-backed intent generation does not prove:

```text
Agent executor ready
autonomous workflow editing ready
production controlled executor ready
```
