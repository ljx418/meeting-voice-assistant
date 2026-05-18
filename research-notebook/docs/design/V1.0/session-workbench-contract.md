# ResearchNotebook V1.0 Session Workbench Contract

文档状态：P0 implementation contract；V1.0-M3 frozen。
适用阶段：M3。

## Scope

M3 implements session-level knowledge workbench:

workspace -> session -> snippet/context ingest -> session build/status -> session ask -> answer with evidence.

## Close/Delete Decision

M3 chooses option B:

- implement `sessions.close(workspaceId, sessionId)`;
- defer `sessions.delete(workspaceId, sessionId)`;
- Session delete is not an M3 acceptance condition;
- UI may show close as the only lifecycle end action.

Closed sessions may be viewed, but they must not allow ingest, build, or query unless a future backend reopen route exists.

## API Surface

Typed wrappers must live only in `shared/api/dataServiceClient.ts`:

- `sessions.list(workspaceId)`;
- `sessions.create(workspaceId, request)`;
- `sessions.get(workspaceId, sessionId)`;
- `sessions.close(workspaceId, sessionId)`;
- `sessions.ingest(workspaceId, sessionId, request)`;
- `sessions.build.start(workspaceId, sessionId, request?)`;
- `sessions.build.getOperation(workspaceId, sessionId, operationId)`;
- `sessions.build.cancel(workspaceId, sessionId, operationId)`;
- `sessions.query(workspaceId, sessionId, request)`.

Do not add `sessions.delete` in M3.

## State Rules

- `activeSessionId` is app-local state and stores only `session_id`.
- Feature modules must not store raw `SessionDetail` as global mutable state.
- Workspace query state and session query state must remain separate.
- Session query must be mutation-driven and must not fire on mount or session switch.
- Session build polling must reuse `useOperationPolling` with typed `getStatus` and `cancel` functions.
- Session build operation keys must include `workspaceId`, `sessionId`, and `operationId`.

## Ingest Rules

M3 session ingest is session-scoped snippet/context ingest only.

It must not:

- call `sources.create`;
- expose source import;
- expose file upload;
- claim JSON/PPT/video/audio parser readiness;
- attach existing source context unless `SessionIngestRequest` explicitly supports it.

## Evidence Rules

Session answers must reuse:

- `AnswerEvidence`;
- `EvidenceList`;
- `SourceTraceDrawer`.

Trace drawer failure affects only the drawer and must not clear the session answer.
