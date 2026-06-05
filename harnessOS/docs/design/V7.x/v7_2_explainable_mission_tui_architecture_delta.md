# V7-2 Explainable Mission TUI Architecture Delta

文档状态：V7 planning package / architecture delta。

## Baseline

Current repo has:

```text
cli.main run
cli.main --oh Textual TUI
V4 Experience State Projection
V6 Product Console projection
```

## Delta

V7-2 adds a first-class command:

```text
harness tui
```

It should bind these sources:

```text
ExperienceStateProjection
WorkflowSpec Registry
Workflow Blueprint / Drawio refs
Runtime Report DTO
Review Console DTO
Evidence Chain DTO
AvailableAction resolver
ForbiddenActionReason resolver
```

## Runtime Boundary

```text
TUI is a workflow head.
TUI is not runtime truth.
TUI may request user confirmation.
TUI may open handoff.
TUI may not directly write WorkflowDraft / WorkflowVersion / StationRun.
```

