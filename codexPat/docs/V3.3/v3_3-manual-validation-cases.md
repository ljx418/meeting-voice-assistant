# V3.3 Manual Validation Cases

status: ready-for-operator

date: 2026-05-24

## Current Remaining Work

V3.3 automatic acceptance has passed for scoped Codex window/session-to-pet binding. The remaining work is manual visual and operator validation, not new feature development.

Remaining concrete items:

- Confirm terminal title update is visible in the user's actual terminal app.
- Confirm a real Codex session launched through `petctl codex launch` visually maps to the expected cat.
- Confirm explicit in-session `petctl notify` states are visible on the bound cat.
- Confirm two real Codex terminal windows do not cross-route events.
- Confirm failure/interrupt behavior is understandable to the operator.
- Confirm documentation examples are usable by a human without reading source code.

V3.3 still does not cover:

- unqualified OS-level Codex window binding ready.
- automatic inference of Codex internal thinking from arbitrary terminal text.
- all Codex workflows verified.
- Claude Code integration verified.

## Preconditions

- Desktop app is running.
- Local bridge health returns ok:

```bash
curl -sS http://127.0.0.1:17321/api/health
```

- `petctl` is built:

```bash
pnpm --filter @agent-desktop-pet/petctl build
```

## Case 1：Single Real Codex Window Binding

Command:

```bash
node packages/petctl/dist/cli.js codex launch --name "Manual V3.3 Cat" -- --help
```

Expected:

- A new Codex instance cat appears or is listed.
- The terminal title shows an Agent Pet / instance hint when the terminal supports title updates.
- The cat enters `running` while the child command is active.
- The cat enters `success` after command exit.
- No token, Authorization header, config path, workspace path, or full local path is printed.

Result fields for operator:

```text
status:
terminal title visible:
target cat observed:
final state:
notes:
```

## Case 2：In-session Explicit State Routing

Start a shell bound to a new instance:

```bash
eval "$(node packages/petctl/dist/cli.js attach codex --name 'Manual Env Cat' --print-env)"
```

Send states without `--instance`:

```bash
node packages/petctl/dist/cli.js notify --level thinking --title "Manual thinking"
node packages/petctl/dist/cli.js notify --level need_input --title "Manual needs input"
node packages/petctl/dist/cli.js notify --level success --title "Manual success"
```

Expected:

- All three events route to the same attached cat.
- Default cat is not affected by the env-routed events.
- Other Codex cats are not affected.

Result fields for operator:

```text
status:
thinking visible:
need_input visible:
success visible:
no cross-route observed:
notes:
```

## Case 3：Two Window Isolation

Terminal A:

```bash
eval "$(node packages/petctl/dist/cli.js attach codex --name 'Manual A' --print-env)"
node packages/petctl/dist/cli.js notify --level running --title "A running"
```

Terminal B:

```bash
eval "$(node packages/petctl/dist/cli.js attach codex --name 'Manual B' --print-env)"
node packages/petctl/dist/cli.js notify --level error --title "B error"
```

Expected:

- A cat shows `running`.
- B cat shows `error`.
- A does not change when B sends its event.
- B does not change when A sends its event.

Result fields for operator:

```text
status:
A cat state:
B cat state:
cross-route observed:
notes:
```

## Case 4：Failure Exit Mapping

Command:

```bash
node packages/petctl/dist/cli.js codex launch --name "Manual Failure Cat" --bin false -- --json
```

Expected:

- A new instance is created.
- The wrapper returns a nonzero CLI status.
- The target cat enters `error`.
- The output does not include token, Authorization header, raw payload, config path, workspace path, or full local path.

Result fields for operator:

```text
status:
target cat entered error:
output redacted:
notes:
```

## Case 5：Documentation Usability

Open:

- `README.md`
- `docs/reference/multi-codex-workflow.md`
- `docs/V3.3/v3_3-codex-window-binding-design.md`

Expected:

- A user can find the recommended `petctl codex launch` path.
- The docs clearly state that V3.3 is wrapper-first.
- The docs do not imply unqualified OS-level window binding.
- The docs do not imply Claude Code is verified.

Result fields for operator:

```text
status:
examples usable:
claim wording acceptable:
notes:
```

## Final Manual Decision

Manual validation can be accepted only if:

- Cases 1-5 are passed or explicitly waived with rationale.
- No forbidden claim is used as ready.
- Any visual limitation is recorded as a V3.4 candidate, not silently treated as V3.3 passed.

Allowed V3.3 claim remains:

```text
V3.3 Codex window/session-to-pet binding smoke passed for tested local macOS terminal scenarios.
```
