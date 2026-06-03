# Historical V5-7 Test Matrix

文档状态：historical / superseded。Distributed multi-Agent runtime 已移动到 V5-8；本文不再是当前控制计划。

## Focused Tests

```text
tests/test_v5_7_distributed_run_coordination.py
tests/test_v5_7_state_recovery.py
tests/test_v5_7_attempt_history.py
tests/test_v5_7_artifact_lineage.py
tests/test_v5_7_tenant_policy_credential_boundary.py
tests/test_v5_7_no_false_green.py
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
