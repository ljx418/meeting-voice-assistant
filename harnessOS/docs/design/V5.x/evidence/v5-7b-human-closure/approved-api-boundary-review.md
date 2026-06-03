# V5-7B approved_api Boundary Review

文档状态：V5-7B closure evidence。本文只记录 approved_api 边界审查要求，不启用 approved_api runtime。

## Boundary Requirements

approved_api 不得绕过人工确认。V5-7B 进入 implementation 前必须证明：

```text
tenant-bound API client identity
service account binding
human_authorization_ref
capability scope restricted to initial action set
rate limit and quota policy checked
audit evidence records API client / service account / human authorization refs
```

## Required Denial / Audit Tests

```text
approved_api_without_human_authorization_denied
approved_api_with_expired_human_authorization_denied
approved_api_wrong_tenant_denied
approved_api_wrong_workspace_denied
approved_api_source_agent_denied
approved_api_records_api_client_service_account_and_human_authorization_refs
```

## Current Review Decision

```text
NEEDS_MORE_EVIDENCE
```

Reason:

```text
approved_api boundary has not been proven by runtime or staging fixture evidence.
```

## Stop Conditions

```text
approved_api can start/rerun/write/evaluate without human authorization
approved_api accepts source=agent
approved_api accepts raw credential
approved_api bypasses tenant/app/workspace scope
```
