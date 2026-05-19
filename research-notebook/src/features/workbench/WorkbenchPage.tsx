import { FormEvent, useCallback, useEffect, useId, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { dataServiceClient } from '../../shared/api/dataServiceClient';
import {
  useCloseSessionMutation,
  useCreateSessionMutation,
  useSessionIngestMutation,
  useSessionQuery,
  useSessionQueryMutation,
  useSessionsQuery,
  useStartSessionBuildMutation
} from '../../shared/api/workspaceM3Queries';
import { useSourcesQuery } from '../../shared/api/workspaceM2Queries';
import { useSessionGraphQuery } from '../../shared/api/workspaceM4Queries';
import { queryKeys } from '../../app/routes/queryKeys';
import { useOperationPolling } from '../../shared/hooks/useOperationPolling';
import type { BuildOperation, SessionDetail, SessionState, SessionSummary } from '../../shared/types/api';
import { ApiErrorState } from '../../shared/components/ApiErrorState';
import { EvidenceList } from '../../shared/components/EvidenceList';
import { SourceTraceDrawer } from '../../shared/components/SourceTraceDrawer';
import { EmptyState, LoadingState, StateBlock, UnsupportedFeatureState } from '../../shared/components/StateBlock';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';
import { SessionGraphContext } from '../../shared/components/GraphContextPanel';

function visibleSessionState(state?: SessionState) {
  if (state === 'closed') return 'Closed';
  if (state === 'building') return 'Building';
  if (state === 'ready') return 'Ready';
  if (state === 'ingested_not_built') return 'Needs build';
  if (state === 'failed_build' || state === 'failed_ingest') return 'Failed';
  return 'Active';
}

function SessionCreateForm({ workspaceId, onCreated }: { workspaceId: string; onCreated: (sessionId: string) => void }) {
  const titleId = useId();
  const [title, setTitle] = useState('');
  const createSession = useCreateSessionMutation(workspaceId);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = title.trim();
    if (!trimmed) return;
    createSession.mutate(
      { title: trimmed },
      {
        onSuccess: (response) => {
          setTitle('');
          onCreated(response.session.session_id);
        }
      }
    );
  };

  return (
    <form className="session-create-form" onSubmit={submit} aria-label="Create session">
      <label>
        <span className="field-label">Session title</span>
        <input id={titleId} className="text-input" value={title} onChange={(event) => setTitle(event.target.value)} />
      </label>
      {createSession.error ? <ApiErrorState title="Create session failed" error={createSession.error} /> : null}
      <button className="primary-button" type="submit" disabled={createSession.isPending || !title.trim()}>
        {createSession.isPending ? 'Creating' : 'Create session'}
      </button>
    </form>
  );
}

function SessionList({
  workspaceId,
  activeSessionId,
  onSelect
}: {
  workspaceId: string;
  activeSessionId: string | null;
  onSelect: (sessionId: string) => void;
}) {
  const sessionsQuery = useSessionsQuery(workspaceId);

  return (
    <section className="panel session-sidebar" aria-labelledby="session-list-title">
      <div className="panel-header">
        <h2 id="session-list-title">Sessions</h2>
      </div>
      <div className="panel-body page-grid">
        <SessionCreateForm workspaceId={workspaceId} onCreated={onSelect} />
        {sessionsQuery.isLoading ? <LoadingState label="Loading sessions" /> : null}
        {sessionsQuery.error ? (
          <ApiErrorState title="Session list unavailable" error={sessionsQuery.error} onRetry={() => void sessionsQuery.refetch()} />
        ) : null}
        {sessionsQuery.data && sessionsQuery.data.length === 0 ? (
          <EmptyState title="No sessions yet">Create a session to start a focused workbench.</EmptyState>
        ) : null}
        {sessionsQuery.data && sessionsQuery.data.length > 0 ? (
          <div className="session-list">
            {sessionsQuery.data.map((session) => (
              <button
                className={`session-row${activeSessionId === session.session_id ? ' active' : ''}`}
                key={session.session_id}
                type="button"
                onClick={() => onSelect(session.session_id)}
              >
                <span>{session.title}</span>
                <small>{visibleSessionState(session.state)}</small>
              </button>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function SessionSummaryPanel({
  workspaceId,
  session,
  onClosed
}: {
  workspaceId: string;
  session: SessionDetail;
  onClosed: () => void;
}) {
  const closeSession = useCloseSessionMutation(workspaceId);
  const isClosed = session.state === 'closed';

  const close = () => {
    closeSession.mutate(session.session_id, { onSuccess: onClosed });
  };

  return (
    <section className="panel" aria-labelledby="session-summary-title">
      <div className="panel-header">
        <h2 id="session-summary-title">Session Context</h2>
      </div>
      <div className="panel-body page-grid">
        <div className="toolbar-row">
          <div>
            <div className="eyebrow">Current session</div>
            <h3>{session.title}</h3>
          </div>
          <span className={`state-pill state-${session.state}`}>{visibleSessionState(session.state)}</span>
        </div>
        <dl className="source-meta-grid">
          <div>
            <dt>session_id</dt>
            <dd>{session.session_id}</dd>
          </div>
          <div>
            <dt>artifact refs</dt>
            <dd>{session.artifact_refs?.length ? `${session.artifact_refs.length} present` : 'none'}</dd>
          </div>
          <div>
            <dt>source context</dt>
            <dd>{session.source_ids?.length ? `${session.source_ids.length} sources` : 'none'}</dd>
          </div>
        </dl>
        <p>{session.context_summary || 'No session context summary returned yet.'}</p>
        {closeSession.error ? <ApiErrorState title="Close session failed" error={closeSession.error} /> : null}
        <button className="secondary-button" type="button" onClick={close} disabled={isClosed || closeSession.isPending}>
          {isClosed ? 'Closed' : closeSession.isPending ? 'Closing' : 'Close session'}
        </button>
      </div>
    </section>
  );
}

function SessionIngestPanel({ workspaceId, session }: { workspaceId: string; session: SessionSummary }) {
  const labelId = useId();
  const contentId = useId();
  const [label, setLabel] = useState('');
  const [content, setContent] = useState('');
  const isClosed = session.state === 'closed';
  const ingest = useSessionIngestMutation(workspaceId, session.session_id);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = content.trim();
    if (!trimmed || isClosed) return;
    ingest.mutate(
      { content: trimmed, label: label.trim() || undefined },
      {
        onSuccess: () => {
          setLabel('');
          setContent('');
        }
      }
    );
  };

  return (
    <section className="panel" aria-labelledby="session-ingest-title">
      <div className="panel-header">
        <h2 id="session-ingest-title">Snippet Ingest</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label>
            <span className="field-label">Context label</span>
            <input id={labelId} className="text-input" value={label} onChange={(event) => setLabel(event.target.value)} disabled={isClosed} />
          </label>
          <label className="wide-field">
            <span className="field-label">Snippet or context</span>
            <textarea
              id={contentId}
              className="text-area"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              disabled={isClosed}
              placeholder="Session-scoped text/context only. Source import and file upload are not part of M3 ingest."
            />
          </label>
          {ingest.error ? <ApiErrorState title="Session ingest failed" error={ingest.error} /> : null}
          <button className="primary-button" type="submit" disabled={isClosed || ingest.isPending || !content.trim()}>
            {isClosed ? 'Session closed' : ingest.isPending ? 'Ingesting' : 'Ingest snippet'}
          </button>
        </form>
      </div>
    </section>
  );
}

function SessionBuildPanel({ workspaceId, session }: { workspaceId: string; session: SessionSummary }) {
  const queryClient = useQueryClient();
  const [activeOperationId, setActiveOperationId] = useState<string | null>(null);
  const isClosed = session.state === 'closed';
  const startBuild = useStartSessionBuildMutation(workspaceId, session.session_id);

  const onCompleted = useCallback(
    async (operation: BuildOperation) => {
      if (operation.status === 'completed') {
        await queryClient.invalidateQueries({ queryKey: queryKeys.session(workspaceId, session.session_id) });
      }
    },
    [queryClient, session.session_id, workspaceId]
  );

  const polling = useOperationPolling({
    operationId: isClosed ? null : activeOperationId,
    scope: 'session',
    staleKey: `${workspaceId}:${session.session_id}`,
    getStatus: () => dataServiceClient.sessions.build.getOperation(workspaceId, session.session_id, activeOperationId ?? ''),
    cancel: () => dataServiceClient.sessions.build.cancel(workspaceId, session.session_id, activeOperationId ?? ''),
    onCompleted
  });

  const start = () => {
    if (isClosed) return;
    startBuild.mutate(
      { reason: 'session_rebuild' },
      {
        onSuccess: (response) => setActiveOperationId(response.operation_id)
      }
    );
  };

  return (
    <section className="panel" aria-labelledby="session-build-title">
      <div className="panel-header">
        <h2 id="session-build-title">Session Build</h2>
      </div>
      <div className="panel-body page-grid">
        {startBuild.error ? <ApiErrorState title="Session build start failed" error={startBuild.error} /> : null}
        <div className="toolbar-row">
          <div>
            <div className="workspace-meta">Active session operation</div>
            <strong>{activeOperationId ?? 'none'}</strong>
          </div>
          <button className="primary-button" type="button" onClick={start} disabled={isClosed || startBuild.isPending}>
            {isClosed ? 'Session closed' : startBuild.isPending ? 'Starting' : 'Build session'}
          </button>
        </div>
        <StateBlock
          title={`Session build status: ${polling.uiState}`}
          tone={polling.uiState === 'failed' || polling.uiState === 'operation_unavailable' ? 'error' : 'neutral'}
          action={
            polling.canCancel ? (
              <button className="secondary-button" type="button" onClick={() => void polling.cancelOperation()} disabled={polling.isCancelling}>
                {polling.isCancelling ? 'Cancelling' : 'Cancel'}
              </button>
            ) : null
          }
        >
          {polling.operation?.message || 'Session build status is scoped to the selected session only.'}
        </StateBlock>
      </div>
    </section>
  );
}

function SessionAskPanel({
  workspaceId,
  session,
  onTraceSourceId
}: {
  workspaceId: string;
  session: SessionSummary;
  onTraceSourceId: (sourceId: string) => void;
}) {
  const questionId = useId();
  const [question, setQuestion] = useState('');
  const isClosed = session.state === 'closed';
  const querySession = useSessionQueryMutation(workspaceId, session.session_id);
  const sourcesQuery = useSourcesQuery(workspaceId);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isClosed) return;
    querySession.mutate({
      question: trimmed,
      registrySourceIds: sourcesQuery.data?.map((source) => source.source_id)
    });
  };

  return (
    <section className="panel" aria-labelledby="session-query-title">
      <div className="panel-header">
        <h2 id="session-query-title">Session Ask</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label className="wide-field">
            <span className="field-label">Session question</span>
            <textarea
              id={questionId}
              className="text-area"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              disabled={isClosed}
              placeholder="Ask against the selected session context."
            />
          </label>
          <button className="primary-button" type="submit" disabled={isClosed || querySession.isPending || !question.trim()}>
            {isClosed ? 'Session closed' : querySession.isPending ? 'Asking' : 'Ask session'}
          </button>
        </form>
        {querySession.error ? <ApiErrorState title="Session query failed" error={querySession.error} /> : null}
        {querySession.data ? (
          <article className="answer-card">
            <h3>Session Answer</h3>
            <p>{querySession.data.answer}</p>
            <EvidenceList evidence={querySession.data.evidence} onTrace={onTraceSourceId} />
            <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'session_answer', session_id: session.session_id }} />
          </article>
        ) : null}
      </div>
    </section>
  );
}

function SessionGraphPanel({ workspaceId, sessionId }: { workspaceId: string; sessionId: string }) {
  const graphQuery = useSessionGraphQuery(workspaceId, sessionId);

  return (
    <section className="panel" aria-labelledby="session-graph-title">
      <div className="panel-header">
        <h2 id="session-graph-title">Read-only Session Graph</h2>
      </div>
      <div className="panel-body page-grid">
        {graphQuery.isLoading ? <LoadingState label="Loading session graph" /> : null}
        {graphQuery.error ? (
          <ApiErrorState title="Session graph unavailable" error={graphQuery.error} onRetry={() => void graphQuery.refetch()} />
        ) : null}
        {graphQuery.data ? <SessionGraphContext graph={graphQuery.data} /> : null}
      </div>
    </section>
  );
}

function SessionWorkbench({ workspaceId, activeSessionId, onSessionClosed }: { workspaceId: string; activeSessionId: string | null; onSessionClosed: () => void }) {
  const [traceSourceId, setTraceSourceId] = useState<string | null>(null);
  const sessionQuery = useSessionQuery(workspaceId, activeSessionId);

  if (!activeSessionId) {
    return <EmptyState title="No active session">Select or create a session to use the workbench.</EmptyState>;
  }
  if (sessionQuery.isLoading) return <LoadingState label="Loading session" />;
  if (sessionQuery.error) {
    return <ApiErrorState title="Session unavailable" error={sessionQuery.error} onRetry={() => void sessionQuery.refetch()} />;
  }
  if (!sessionQuery.data) return <EmptyState title="Session unavailable">The selected session returned no detail.</EmptyState>;

  const session = sessionQuery.data;

  return (
    <div className="session-workbench-main page-grid">
      <SessionSummaryPanel workspaceId={workspaceId} session={session} onClosed={onSessionClosed} />
      <SessionIngestPanel workspaceId={workspaceId} session={session} />
      <SessionBuildPanel workspaceId={workspaceId} session={session} />
      <SessionGraphPanel workspaceId={workspaceId} sessionId={session.session_id} />
      <SessionAskPanel workspaceId={workspaceId} session={session} onTraceSourceId={setTraceSourceId} />
      {session.last_answer ? (
        <article className="answer-card">
          <h3>Last Answer</h3>
          <p>{session.last_answer.answer}</p>
          <EvidenceList evidence={session.last_answer.evidence} onTrace={setTraceSourceId} />
          <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'session_answer', session_id: session.session_id }} />
        </article>
      ) : null}
      <SourceTraceDrawer workspaceId={workspaceId} sourceId={traceSourceId} onClose={() => setTraceSourceId(null)} />
    </div>
  );
}

export function WorkbenchPage() {
  const { workspaceId = '' } = useParams();
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  useEffect(() => {
    // Workspace route changes must detach the old selected session id.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setActiveSessionId(null);
  }, [workspaceId]);

  if (!workspaceId) {
    return (
      <UnsupportedFeatureState title="Open Workbench From A Workspace">
        Session Workbench is scoped to a workspace. Open a workspace first, then use its workbench route.
      </UnsupportedFeatureState>
    );
  }

  return (
    <div className="session-workbench">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">V1.0-M3</div>
          <h2 className="page-title">Session Workbench</h2>
        </div>
        <Link className="secondary-button" to={`/workspaces/${workspaceId}`}>
          Workspace
        </Link>
      </div>
      <div className="session-workbench-grid">
        <SessionList workspaceId={workspaceId} activeSessionId={activeSessionId} onSelect={setActiveSessionId} />
        <SessionWorkbench workspaceId={workspaceId} activeSessionId={activeSessionId} onSessionClosed={() => undefined} />
      </div>
    </div>
  );
}
