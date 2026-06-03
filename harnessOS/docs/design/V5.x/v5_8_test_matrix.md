# V5-8 Test Matrix

文档状态：V5-8 planning package；implementation has not started。

## Focused Tests

```text
tests/test_v5_8_distributed_run_coordination.py
tests/test_v5_8_state_recovery.py
tests/test_v5_8_attempt_history.py
tests/test_v5_8_artifact_lineage.py
tests/test_v5_8_tenant_policy_credential_boundary.py
tests/test_v5_8_no_false_green.py
```

## Required Coverage

```text
worker lost recovery
coordinator restart recovery
attempt history retained
artifact lineage survives retry
cross-tenant worker denied
provider call requires credential boundary
distributed audit export includes run evidence
No False Green claim guard blocks full multi-Agent orchestration ready
```
