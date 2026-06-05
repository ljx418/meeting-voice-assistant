# V9 Security Threat Model And Abuse Cases

文档状态：V9 P0 threat model / required before runtime implementation。

## 1. Threat Scope

V9 introduces high-risk execution capabilities. Threat analysis must cover Agent execution, human authorization, terminal worker, Studio BFF, evidence chain and production governance.

## 2. Abuse Cases

```text
source=agent impersonates human user.
authorization replay after expiry.
operation_hash mismatch with target_refs.
cross-tenant authorization reuse.
stale approval reuse.
terminal path traversal.
terminal symlink escape.
secret exfiltration through shell or evidence.
browser route bypass.
BFF bypass.
evidence poisoning.
claim false green.
rollback failure.
lost worker duplicate mutation.
idempotency collision.
fan-in attribution removal.
artifact lineage producer_attempt_id removal.
```

## 3. Required Controls

```text
deny-by-default CapabilityResolver.
HumanAuthorizationRef validation.
approval gate for high-risk actions.
tenant/workspace/project/app binding.
operation_hash binding.
idempotency key for mutation.
append-only attempt history and evidence.
workspace canonicalization and symlink checks.
browser route denylist.
redaction scanner.
No False Green scanner.
incident timeline for denials and failures.
```

## 4. Acceptance Tests

```text
source_agent_impersonation_denied
authorization_replay_denied
operation_hash_mismatch_denied
cross_tenant_authorization_denied
terminal_path_traversal_denied
terminal_symlink_escape_denied
secret_exfiltration_denied
browser_bff_bypass_denied
evidence_poisoning_detected
claim_false_green_detected
lost_worker_duplicate_mutation_prevented
idempotency_collision_returns_prior_ref_or_denies
```
