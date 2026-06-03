# V5-2 Target Architecture Delta

文档状态：V5-2 implementation planning。本文描述 Credential / Provider Lifecycle 的架构增量，不实现功能。

## 1. New Logical Components

```text
ProviderProfileRegistry
CredentialReferenceStore
CredentialLifecycleService
ProviderCapabilityResolver
ProviderSmokeValidator
ProviderInvocationEvidenceRecorder
CredentialPolicyGuard
SecretRedactionBoundary
```

## 2. Component Responsibilities

| Component | Responsibility | Runtime Truth Boundary |
| --- | --- | --- |
| ProviderProfileRegistry | 管理 provider profile 元数据和绑定关系 | 不是 WorkflowDraft / WorkflowVersion truth |
| CredentialReferenceStore | 保存 credential ref、状态和绑定，不暴露 raw secret | 不能把 secret 写入 report/evidence |
| CredentialLifecycleService | 处理 issue / rotate / revoke / emergency revoke 的状态机 | 需要 user/admin confirmation |
| ProviderCapabilityResolver | 判断 provider 是否允许用于指定 tenant/workspace/app/action | 不授予 Agent executor 权限 |
| ProviderSmokeValidator | 进行受控 provider smoke validation | 只输出 redacted summary |
| ProviderInvocationEvidenceRecorder | 记录 provider/model/profile 调用证据 | 不能记录 raw prompt/raw content/key |
| CredentialPolicyGuard | 拦截无确认、跨 scope、source=agent mutation | 复用 V5-1 identity boundary |
| SecretRedactionBoundary | 统一过滤 token/secret/raw payload | 应用于 DTO、error、HTML、audit |

## 3. Data Flow

```text
IdentityContext
 -> CredentialPolicyGuard
 -> ProviderProfileRegistry
 -> CredentialReferenceStore
 -> ProviderCapabilityResolver
 -> ProviderSmokeValidator
 -> ProviderInvocationEvidenceRecorder
 -> Evidence Chain / Audit summary
```

## 4. Required Boundaries

```text
Credential reference is not raw secret.
Provider profile is tenant/workspace/app scoped.
source=agent cannot create/rotate/revoke credential.
Credential mutation requires user_confirmed=true or admin-confirmed policy.
Provider smoke must redact raw prompt, raw content, API key, token, signed URL.
Provider invocation evidence cannot become runtime truth.
```

## 5. Dependency On V5-1

V5-2 assumes V5-1 core boundary slice exists:

```text
server-bound identity context
tenant / workspace / project / app ownership validation
actor binding
stable denial audit event
```

V5-2 does not make V5-1 into full enterprise auth or a complete tenant control plane.

