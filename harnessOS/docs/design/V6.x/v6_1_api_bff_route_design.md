# V6-1 API / BFF Route Design

文档状态：V6-1 implementation-ready route design。

## Route Boundary

V6-1 不新增完整 enterprise auth routes。所有 future BFF / Product Console routes 必须先通过 identity / tenant guard。

## Protected Route Groups

```text
/bff/v6/identity/context
/bff/v6/tenants/{tenant_id}/workspaces
/bff/v6/workspaces/{workspace_id}/projects
/bff/v6/projects/{project_id}/apps
/bff/v6/apps/{app_id}/workflow-specs
/bff/v6/apps/{app_id}/workflow-instances
/bff/v6/apps/{app_id}/runtime-report
/bff/v6/apps/{app_id}/review-console
/bff/v6/apps/{app_id}/evidence-chain
```

## Required Guard Inputs

```text
request_id
correlation_id
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
user_id
service_account_id
agent_id
session_id
operation
target_resource_type
target_resource_id
```

## Stable Error Codes

```text
AUTH_REQUIRED
TENANT_SCOPE_DENIED
WORKSPACE_SCOPE_DENIED
PROJECT_SCOPE_DENIED
APP_SCOPE_DENIED
RESOURCE_SCOPE_DENIED
ACTOR_BINDING_DENIED
SERVICE_ACCOUNT_SCOPE_DENIED
SERVICE_ACCOUNT_OPERATION_DENIED
AGENT_EXECUTION_DENIED
USER_CONFIRMATION_REQUIRED
AUDIT_CONTEXT_REQUIRED
```

## Browser Boundary

Browser clients must use BFF / Product Console routes. Browser clients must not bypass tenant guard or call internal runtime routes directly.
