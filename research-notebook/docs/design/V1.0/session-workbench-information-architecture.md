# ResearchNotebook V1.0 Session Workbench Information Architecture

文档状态：P1 implementation contract；V1.0-M3 frozen。
适用阶段：M3。

## Layout

M3 uses a workspace-scoped workbench route:

- `/workspaces/:workspaceId/workbench`

The generic `/workbench` route remains a scoped-entry placeholder and does not create global sessions.

## Left Rail

- session list;
- create session;
- active session selection;
- visible state: Empty / Active / Needs build / Building / Ready / Closed / Failed.

## Main Workbench

- selected session summary;
- snippet/context ingest;
- session build panel;
- session ask panel;
- answer with evidence;
- optional last answer from `SessionDetail`.

## Trace Drawer

The existing source trace drawer is reused. Session evidence opens source trace only through `source_id`.

## Disabled States

Closed sessions:

- can display detail and last answer;
- cannot ingest;
- cannot build;
- cannot query;
- cannot reopen in M3.

No selected session:

- show explicit empty state;
- do not auto-create a session.
