# V5-4A Test Matrix

文档状态：V5-4A core slice implemented for review。

## Focused Tests

```text
tests/test_v5_4a_policy_capability_matrix.py
tests/test_v5_4a_approval_gate_design.py
tests/test_v5_4a_sandbox_boundary.py
tests/test_v5_4a_kill_switch_design.py
tests/test_v5_4a_no_false_green.py
```

## Required Coverage

```text
every candidate operation has classification
source=agent mutation remains denied
high-risk action approval-gated
never_executor never enters allowlist
sandbox boundary rejects raw payload and token
No False Green claim guard blocks Agent executor ready
```

## Focused Validation Result

```text
./.venv/bin/python -m pytest tests/test_v5_4a_*.py -q
13 passed
```
