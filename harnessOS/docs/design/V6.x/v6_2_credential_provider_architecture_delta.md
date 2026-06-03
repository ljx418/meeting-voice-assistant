# V6-2 Credential / Provider Architecture Delta

文档状态：V6-2 implementation-ready architecture delta。

## Delta Summary

V6-2 在 V5-2 credential/provider registry 上增加生产试点 lease 语义：

```text
V5-2 ProviderProfile / CredentialReference
 -> V6-2 CredentialLease
 -> CredentialLeaseDecision
 -> ProviderInvocationEvidenceV6
 -> V6-2 evidence package
```

## Components

```text
ProductionProviderProfile
CredentialReference
CredentialLease
CredentialLeaseDecision
CredentialLifecycleEvent
ProviderInvocationEvidence
CredentialRedactionGuard
```

## Data Flow

```text
identity context from V6-1
 -> provider profile scope check
 -> credential reference issue / rotate / revoke
 -> lease issue with tenant/app/audience/operation binding
 -> invocation validates profile, credential, lease, model, capability
 -> redacted evidence records provider/model/credential_ref/lease_ref
```

## Runtime Truth Boundary

Credential/provider lifecycle is a policy and evidence boundary. It does not construct workflow runtime truth, does not call unrestricted external LLM, and does not expose raw secrets.

## Secret Boundary

V6-2 may record only:

```text
env://KEY_NAME
secret://[REDACTED]
vault://[REDACTED]
keychain://[REDACTED]
```

No raw secret, Authorization header, Bearer token, raw prompt, or raw connector payload may appear in logs, JSON, HTML, evidence, or prompts.
