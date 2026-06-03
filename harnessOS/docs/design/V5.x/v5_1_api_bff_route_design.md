# V5-1 API / BFF Route Design

文档状态：V5-1 pre-implementation planning。本文定义 route design，不新增实际路由。

## 1. Route Design Principle

V5-1 routes must be production auth / tenant aware. Route handlers may only execute after identity context and ownership guard pass.

## 2. Proposed Route Groups

Route groups for future implementation:

```text
/bff/v5/identity/context
/bff/v5/tenants/{tenant_id}/workspaces
/bff/v5/workspaces/{workspace_id}/projects
/bff/v5/projects/{project_id}/apps
/bff/v5/apps/{app_id}/workflow-specs
/bff/v5/apps/{app_id}/workflow-instances
/bff/v5/apps/{app_id}/reports
/bff/v5/apps/{app_id}/evidence
```

## 3. Required Guard Inputs

Every protected route must resolve:

```text
request_id
correlation_id
tenant_id
workspace_id
project_id
app_id
actor_type
actor_id
user_id or service_account_id or agent_id
session_id when applicable
target_resource_type
target_resource_id
```

## 4. Stable Error Codes

Future implementation should use stable errors:

```text
AUTH_REQUIRED
TENANT_SCOPE_DENIED
WORKSPACE_SCOPE_DENIED
PROJECT_SCOPE_DENIED
APP_SCOPE_DENIED
RESOURCE_SCOPE_DENIED
ACTOR_BINDING_DENIED
SERVICE_ACCOUNT_SCOPE_DENIED
AGENT_EXECUTION_DENIED
AUDIT_CONTEXT_REQUIRED
```

## 5. Browser Boundary

Browser clients must continue to use BFF routes and must not directly call internal runtime routes or bypass tenant guard.

## 6. No False Green

No False Green：本文只定义 future route design，不新增 production auth route，不证明 enterprise auth ready、多租户控制台已完成或 production-ready external app support。
