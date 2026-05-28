# V5 Preflight Instance Cleanup Evidence

status: passed

date: 2026-05-28

## Scope

Clean existing local desktop pet instances before continuing V5.x development.

Policy selected:

```text
Keep only default.
```

## Initial State

Desktop health: ok.

Initial instance count: 7.

Initial instances:

| instanceId | displayName | isDefault |
| --- | --- | --- |
| default | Agent Desktop Pet | true |
| codex_1779677664049 | V3.4 Hook Cat | false |
| codex_1779846896461 | V4.2 Cat | false |
| codex_1779848119813 | V4.2 Cat | false |
| codex_1779864407019 | V4.5 TUI Cat | false |
| codex_1779865675809 | V4.5 TUI Cat Fixed | false |
| codex_1779865832392 | V4.5 TUI Cat Real | false |

## Cleanup Result

Detached instances:

```text
codex_1779677664049
codex_1779846896461
codex_1779848119813
codex_1779864407019
codex_1779865675809
codex_1779865832392
```

Final instance count: 1.

Final remaining instance:

| instanceId | displayName | isDefault |
| --- | --- | --- |
| default | Agent Desktop Pet | true |

## Security

The cleanup evidence records only instance IDs and display names. It does not record credential material, request bodies, prompt content, tool content, or local filesystem locations.

