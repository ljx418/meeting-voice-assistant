# ResearchNotebook V1.0 Error State Model

文档状态：P0 implementation contract；V1.0-M4 frozen。
适用阶段：M1-M4。

## 1. Purpose

ResearchNotebook must map normalized backend errors to stable page and component states. UI must not infer meaning from raw exceptions, stack traces, or filesystem paths.

## 2. Global Error Classes

Required normalized UI states:

- backend unavailable;
- backend version mismatch;
- schema/capability mismatch;
- blocked;
- not found;
- validation error;
- archived workspace;
- missing graph artifact;
- missing session artifact;
- operation unavailable;
- generic service unavailable.

## 3. Page Mapping

| Surface | Required states |
| --- | --- |
| Home | backend unavailable, empty workspace list, create failed, version mismatch |
| Workspace | workspace not found, archived workspace, source import failed, source list failed |
| Source Library | unsupported type, failed import, failed build, removed source |
| Build Panel | queued, running, completed, failed, cancelled, operation unavailable, operation not found |
| Query Answer | validation error, service unavailable, no evidence available |
| Trace Drawer | source not found, trace unavailable, service unavailable |
| Graph Panel | missing graph artifact, graph unavailable, workspace not found, backend unavailable, version/schema mismatch |
| Session Graph | missing session artifact, session not found, graph unavailable, backend unavailable |
| Session Workbench | session not found, session closed, missing session artifact, session query failed |
| Feedback Entry | feedback failed, validation error, service unavailable |

## 4. Component Rules

- Error components must be scoped to the failed surface where possible.
- A trace drawer failure must not erase the answer.
- A graph artifact missing state must not block workspace query.
- A feedback failure must not block answer rendering.
- Unsupported/future capability states are product states, not generic errors.

## 5. Acceptance

M1-M4 acceptance requires at least one visual state or component path for each page-level error class listed above.
