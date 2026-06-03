# V5-7B Staging Fixture Design

文档状态：V5-7B staging fixture design。本文只定义 staging fixture，不创建 runtime worker，不执行 production action。

## Scope

```text
design_only=true
runtime_worker_created=false
production_executor_route_created=false
source_agent_durable_mutation_allowed=false
```

## Required Fixture Fields

```text
tenant_id
workspace_id
app_id
human_actor_id
service_account_id
human_authorization_ref
workflow_instance_id
station_id
station_run_id
artifact_id
credential_ref
audit_export_package_id
incident_timeline_id
idempotency_key
correlation_id
request_id
```

## Negative Cases

```text
cross_tenant_denied
wrong_workspace_denied
wrong_app_denied
wrong_workflow_instance_denied
unknown_credential_ref_denied
raw_secret_absent
source_agent_denied
```

## Fixture Boundary

The fixture must be isolated from production data. It may use production-like identifiers and staged DTOs, but it must not:

```text
call production executor route
start production runtime worker
allow source=agent durable mutation
include raw credentials
include raw artifact content in evidence/log/HTML/JSON
mark staging_only evidence as production PASS
```

## Current Status

```text
NOT_CREATED
```

Reason:

```text
This stage is still closure-only. The fixture is designed but not instantiated.
```
