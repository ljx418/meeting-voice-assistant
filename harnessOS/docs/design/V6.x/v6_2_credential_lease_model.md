# V6-2 Credential Lease Model

文档状态：V6-2 implementation-ready lease model。

## CredentialLease Fields

```text
credential_lease_id
credential_ref_id
provider_profile_id
tenant_id
workspace_id
project_id
app_id
audience
operation
capability_ref
model_ref
issued_at
expires_at
lease_status
request_id
correlation_id
redaction_status
```

## Binding Requirements

```text
tenant-bound: lease.tenant_id == identity.tenant_id
workspace-bound: lease.workspace_id == identity.workspace_id
project-bound: lease.project_id == identity.project_id
app-bound: lease.app_id == identity.app_id
audience-bound: invocation audience must equal lease.audience
operation-bound: invocation operation must equal lease.operation
credential-bound: lease.credential_ref_id must equal profile credential_ref_id
```

## Denial Matrix

| Scenario | Expected |
| --- | --- |
| expired lease | DENY |
| revoked credential | DENY |
| wrong tenant | DENY |
| wrong app | DENY |
| wrong audience | DENY |
| wrong operation | DENY |
| wrong model | DENY |
| wrong capability | DENY |
| emergency revoked credential | DENY |
| valid lease and invocation | ALLOW |

## No False Green

CredentialLease 证明的是 V6-2 pilot lease contract，不证明 production secret lifecycle ready。
