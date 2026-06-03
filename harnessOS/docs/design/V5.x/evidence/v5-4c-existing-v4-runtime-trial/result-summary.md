# V5-4C Existing V4 Local Runtime Trial Evidence Summary

- Existing V4 runtime entrypoint identified: PASS, `bff:/bff/v4_2/runtime`.
- User-confirmed start against real dev/local fixture: PASS, `completed`.
- Failure fixture creates failed station: PASS, `failed`.
- User-confirmed rerun creates new attempt and stale downstream: PASS, `5` stale stations.
- User-confirmed downstream continuation: PASS, `completed`.
- source=agent runtime mutation denial: PASS, `source_agent_cannot_execute_mutation`.
- runtime_backed=true and devlocal_only=true: PASS.
- No token/raw payload leakage: PASS.

No False Green: this package does not prove production controlled executor readiness or Agent executor readiness.
