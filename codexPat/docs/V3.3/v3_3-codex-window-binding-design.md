# V3.3 Codex Window/Session Binding Design

文档状态：final。

## Design Decision

V3.3 uses wrapper-first binding instead of OS-level terminal introspection.

`petctl codex launch` is the ownership boundary:

```bash
node packages/petctl/dist/cli.js codex launch --name "Review Cat" -- <codex args>
```

The wrapper:

- attaches a Codex `PetInstance` through the existing localhost bridge。
- injects `AGENT_DESKTOP_PET_INSTANCE_ID` into the child process。
- writes a terminal title when stdout is a TTY。
- sends `running` before starting the child。
- sends `success` on exit code `0`。
- sends `error` on nonzero or signal exit。

## Routing Model

The existing `petctl notify` behavior remains the route source:

1. explicit `--instance` wins。
2. otherwise `AGENT_DESKTOP_PET_INSTANCE_ID` is used。
3. otherwise legacy `/api/events` default route is used。

This means commands inside a launched Codex session can simply call:

```bash
node packages/petctl/dist/cli.js notify --level thinking --title "Codex thinking"
```

and the event routes to the current session's cat.

## Non-goals

V3.3 does not infer Codex internal state from arbitrary OS window text. Fine-grained states such as `thinking` or `need_input` require explicit event emission from inside the Codex session.

V3.3 does not claim:

- OS-level Codex window binding ready。
- all Codex workflows verified。
- Claude Code integration verified。
- Windows / cross-platform readiness。

## Security Boundary

The wrapper uses the same local token, schema validation, whitelist, rate limit, diagnostics, and instance routing as existing `petctl` flows.

Evidence must not include token, Authorization header, raw payload, config path, workspace path, full local path, raw tty path, or token file content.
