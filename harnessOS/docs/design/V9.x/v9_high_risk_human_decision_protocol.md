# V9 High-Risk Human Decision Protocol

文档状态：V9 P0 human decision protocol / required before high-risk implementation。

## 1. Purpose

V9-1、V9-2、V9-4、V9-5、V9-7 是高风险阶段。进入实现或高风险能力启用前，必须有可审计的人类 proceed decision。

## 2. Decision Fields

Required fields:

```text
decision_ref
stage_id
decision
decision_owner
required_reviewers
risk_class
scope
allowed_work
blocked_work
created_at
expires_at
revoked
revoked_at
revocation_reason
evidence_refs
audit_ref
correlation_id
```

Allowed `decision`:

```text
GO_FOR_IMPLEMENTATION
GO_FOR_CONTRACT_AUDIT_ONLY
NO_GO
DEFERRED
NEEDS_MORE_EVIDENCE
```

## 3. Rules

```text
approval does not replace HumanAuthorizationRef for runtime durable mutation.
decision_ref is stage-bound and scope-bound.
expired or revoked decision_ref blocks implementation.
high-risk runtime evidence must link to decision_ref.
decision_ref cannot be issued by source=agent.
```

## 4. Required Stage Decisions

```text
V9-1: contract audit decision and separate implementation decision.
V9-2: controlled executor implementation decision.
V9-4: autonomous coding workflow implementation decision.
V9-5: terminal worker write sandbox decision.
V9-7: governance / evidence hardening / terminal automation gate decision.
```

## 5. Stop Conditions

```text
implementation starts with missing decision_ref.
decision_ref has expired.
decision_ref is reused for another stage.
approval gate is treated as human proceed decision.
source=agent issues decision_ref.
```
