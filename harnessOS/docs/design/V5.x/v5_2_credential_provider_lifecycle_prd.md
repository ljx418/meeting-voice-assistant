# V5-2 Credential / Provider Lifecycle PRD

文档状态：V5-2 implementation planning。本文定义 Credential / Provider Lifecycle 的目标规格，不实现运行时代码。

## 1. Stage Goal

V5-2 的目标是把 V4 / V5-1 中的 dev/local provider 调用证据，升级为可审计的 provider profile 与 credential lifecycle 设计。

V5-2 关注：

```text
provider profile registry
credential issuance / rotation / revocation model
credential binding to tenant / workspace / app / actor
redacted provider invocation evidence
provider capability decision
secret hygiene
```

## 2. User Experience

目标体验：

```text
管理员选择 provider
 -> 创建 provider profile
 -> 绑定 tenant / workspace / app
 -> 配置 credential reference
 -> 执行 provider smoke validation
 -> 查看 redacted invocation evidence
 -> 后续支持 rotate / revoke / emergency revoke
```

## 3. Required Capabilities

```text
ProviderProfileDTO
CredentialReferenceDTO
ProviderCapabilityDTO
CredentialLifecycleEventDTO
ProviderInvocationEvidenceDTO
CredentialPolicyDecisionDTO
```

## 4. Acceptance Criteria

V5-2 implementation 通过条件：

```text
provider profile has tenant/workspace/app binding
credential reference never exposes raw secret
credential lifecycle events are audited
rotation and revocation produce evidence
provider invocation evidence records provider/model/profile refs
provider smoke uses redacted input/output summaries
source=agent cannot create, rotate, revoke, or reveal credential
credential operations require user_confirmed=true or admin-confirmed policy
no API key appears in logs, reports, evidence, DOM, or error responses
```

## 5. Non Goals

No False Green：V5-2 不证明以下能力：

```text
enterprise auth ready
multi-tenant control plane ready
production-ready external app support
Agent executor ready
controlled executor ready
production controlled executor ready
complete Workflow Studio ready
distributed multi-Agent runtime ready
```

V5-2 也不实现 V5-3 audit export、V5-4 executor safety gate、V5-5 external app onboarding 或 V5-7 distributed runtime。

## 6. Stop Conditions

停止进入实现的条件：

```text
credential raw secret would be stored in docs, reports, logs, or evidence
provider profile lacks tenant/workspace/app binding
source=agent can mutate credential state
rotation/revocation has no audit event
provider smoke requires exposing raw prompt or raw file content
implementation would require production auth not yet provided by V5-1
```

