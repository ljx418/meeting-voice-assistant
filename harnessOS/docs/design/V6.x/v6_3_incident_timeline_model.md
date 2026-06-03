# V6-3 Incident Timeline Model

文档状态：V6-3 implementation-ready incident timeline model。

## Timeline Requirements

Incident timeline must be:

```text
read-only
correlation_id backed
tenant scoped
workspace scoped
event_ref linked
evidence_ref linked
redacted
```

## Event Types

V6-3 fixture timeline must include at least:

```text
identity.scope.denied
provider.invocation.recorded
runtime.failure.recorded
runtime.retry.recorded
kill_switch.checked
rollback.recorded
```

## Allowed Actions

```text
view
export
open_evidence
```

Forbidden:

```text
Apply
Publish
Approve
Reject
Execute
Run
```

## No False Green

Incident timeline is a read model and cannot construct runtime truth.
