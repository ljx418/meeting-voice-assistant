# V4.2-C Controlled Runtime MVP / 受控运行时 MVP Plan

Status: implemented for focused dev/local validation.

## 1. Goal

V4.2-C implements the minimum controlled runtime wrapper required by the Headless-first V4.x line:

```text
user-confirmed workflow start
user-confirmed station rerun
attempt history
downstream stale state
runtime evidence
timeout baseline
kill switch baseline
Drawio / HTML report regeneration from runtime result
```

Allowed claim:

```text
V4.2-C complete: controlled runtime MVP ready for dev/local validation.
```

Forbidden claims:

```text
forbidden controlled executor ready
forbidden Agent executor ready
forbidden autonomous workflow editing ready
forbidden production-ready external app support
forbidden full multi-Agent orchestration ready
forbidden complete Workflow Studio ready
```

## 2. Implementation Boundary

1. Browser access stays BFF-only through `/bff/v4_2/runtime/*`.
2. Browser must not call `/v1/rpc` or `/v1/events/subscribe`.
3. `source=agent` cannot start, rerun, or continue runtime work.
4. Every durable runtime operation requires `user_confirmed=true`.
5. V4.2-C validates the generic controlled runtime contract against the V4.1 local Markdown workflow fixtures.
6. This stage does not implement Agent executor, production auth, production filesystem permissions, or full multi-Agent orchestration.

## 3. PR Slices

### PR1 Runtime BFF Wrapper

Add `/bff/v4_2/runtime/workflows/local-folder-summary/start`, `/rerun-station`, `/continue-downstream`, `/attempt-history`, `/downstream-stale`, and `/evidence`.

### PR2 Attempt And Stale DTO

Expose a redacted runtime result with attempt history and downstream stale state.

### PR3 Runtime Evidence

Record runtime evidence for workflow start, station rerun, and downstream continuation with timeout and kill switch baseline metadata.

### PR4 Evidence Package

Generate `docs/design/V4.2/evidence/controlled-runtime/` with TUI transcript, runtime JSON, Drawio, HTML reports, and summary.

### PR5 Thin Web Console Client Boundary

Add V4.2 runtime client methods that only call `/bff/v4_2/runtime/*`.

## 4. Acceptance

V4.2-C cannot pass unless:

1. Scenario A uses `tests/fixtures/desktop/技术分享`.
2. Scenario B uses `tests/fixtures/desktop/技术分享_损坏`.
3. Workflow start requires user confirmation.
4. Station rerun requires user confirmation.
5. Agent source is rejected for start/rerun/continue.
6. Rerun creates a new attempt and preserves old error.
7. Downstream stations become stale after upstream rerun.
8. Downstream continuation requires user confirmation.
9. Evidence is generated from real operation results.
10. Drawio and HTML reports are regenerated from runtime result.
11. No sensitive field leaks into DTOs, reports, docs, or UI.

## 5. Risk Review

Spec Drift Risk: LOW

False Green Risk: LOW

Reason: V4.2-C explicitly limits controlled runtime to dev/local validation and keeps Agent executor, production support, and multi-Agent orchestration out of scope.
