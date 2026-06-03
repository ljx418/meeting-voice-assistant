# V5-1 Test Matrix

文档状态：V5-1 pre-implementation planning。本文定义 V5-1 测试矩阵，不实现测试代码。

## 1. Unit / Contract Tests

Required future tests:

```text
test_v5_1_identity_context_resolver.py
test_v5_1_tenant_scope_guard.py
test_v5_1_ownership_resolver.py
test_v5_1_actor_binding_validator.py
test_v5_1_service_account_scope.py
test_v5_1_audit_context.py
test_v5_1_no_false_green.py
```

## 2. Scope Denial Tests

Required scenarios:

```text
cross_tenant_denied
same_tenant_wrong_workspace_denied
same_workspace_wrong_project_denied
same_project_wrong_app_denied
same_app_wrong_resource_denied
same_instance_wrong_agent_session_denied
service_account_outside_scope_denied
agent_mutation_without_user_confirmation_denied
valid_actor_bound_scope_allowed
```

## 3. Audit Tests

Required assertions:

```text
audit_event_id exists
request_id exists
correlation_id exists
tenant/workspace/project/app refs exist
actor refs exist
target resource refs exist
policy_decision exists
scope_decision exists
redaction_status exists
denial_reason exists for denied request
no token / raw payload leakage
```

## 4. E2E Acceptance

V5-1 implementation acceptance must use real repo-backed fixtures and must not fake production success:

```text
create tenant/workspace/project/app fixture
bind human actor
bind service account actor
attempt cross-tenant access
attempt wrong workspace access
attempt wrong app resource access
attempt agent durable mutation
confirm denials
confirm valid scoped read
confirm audit records
confirm no forbidden claims
```

## 5. No False Green

No False Green：passing V5-1 tests may prove production auth / tenant boundary slice only. It must not prove production-ready external app support, Agent executor ready, production controlled executor ready, complete Workflow Studio, or distributed multi-Agent runtime ready.
