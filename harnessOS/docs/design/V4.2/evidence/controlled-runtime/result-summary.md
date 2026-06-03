# V4.2-C Controlled Runtime Evidence Summary

- Real data Scenario A: PASS, `completed`.
- Real data Scenario B failure: PASS, `failed`.
- Station rerun creates stale downstream: PASS, 5 stale stations.
- User-confirmed downstream continuation: PASS, `completed`.
- backed_by=generic_controlled_runtime: PASS.
- source=agent cannot execute mutation: PASS.
- Browser direct /v1/rpc: PASS, not used by evidence package.
- Browser direct /v1/events/subscribe: PASS, not used by evidence package.
- No token/raw payload leakage: PASS.
