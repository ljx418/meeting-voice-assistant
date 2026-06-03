# V5-5 Test Matrix

文档状态：V5-5 core slice implemented for review。

## Focused Tests

```text
tests/test_v5_5_app_registration.py
tests/test_v5_5_domain_origin_guard.py
tests/test_v5_5_quota_rate_limit.py
tests/test_v5_5_customer_offboarding.py
tests/test_v5_5_sdk_compatibility.py
tests/test_v5_5_no_false_green.py
```

## Required Coverage

```text
app registration is tenant-bound
unverified origin denied
quota denial audited
offboarding revokes app access
SDK avoids direct browser /v1/rpc and /v1/events/subscribe
No False Green claim guard blocks production-ready external app support
```

## Focused Validation Result

```text
./.venv/bin/python -m pytest tests/test_v5_5_*.py -q
10 passed
```
