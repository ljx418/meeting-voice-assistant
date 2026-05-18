import { FormEvent, useCallback, useEffect, useId, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { isNormalizedApiError, dataServiceClient } from '../../shared/api/dataServiceClient';
import { useArchiveWorkspaceMutation, useWorkspaceQuery } from '../../shared/api/workspaceQueries';
import {
  useCreateSourceMutation,
  useRemoveSourceMutation,
  useSourcesQuery,
  useStartBuildMutation,
  useWorkspaceQueryMutation
} from '../../shared/api/workspaceM2Queries';
import { queryKeys } from '../../app/routes/queryKeys';
import { useOperationPolling } from '../../shared/hooks/useOperationPolling';
import type { BuildOperation, SourceSummary } from '../../shared/types/api';
import {
  BackendUnavailableState,
  EmptyState,
  LoadingState,
  StateBlock,
  VersionMismatchState
} from '../../shared/components/StateBlock';
import { ApiErrorState } from '../../shared/components/ApiErrorState';
import { EvidenceList } from '../../shared/components/EvidenceList';
import { SourceTraceDrawer } from '../../shared/components/SourceTraceDrawer';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';

function SourceStateBadge({ source }: { source: SourceSummary }) {
  const state = source.build_state ?? source.import_state ?? 'idle';
  return <span className={`state-pill state-${state}`}>{state}</span>;
}

function SourceImportForm({ workspaceId }: { workspaceId: string }) {
  const titleId = useId();
  const typeId = useId();
  const contentId = useId();
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('');
  const [content, setContent] = useState('');
  const createSource = useCreateSourceMutation(workspaceId);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedTitle = title.trim();
    if (!trimmedTitle) return;
    createSource.mutate(
      {
        title: trimmedTitle,
        source_type: sourceType.trim() || undefined,
        content: content.trim() || undefined
      },
      {
        onSuccess: () => {
          setTitle('');
          setSourceType('');
          setContent('');
        }
      }
    );
  };

  return (
    <form className="source-import-form" onSubmit={submit} aria-label="Import source">
      <label>
        <span className="field-label">Source title</span>
        <input id={titleId} className="text-input" value={title} onChange={(event) => setTitle(event.target.value)} />
      </label>
      <label>
        <span className="field-label">Source type</span>
        <input
          id={typeId}
          className="text-input"
          value={sourceType}
          onChange={(event) => setSourceType(event.target.value)}
          placeholder="Optional backend-supported type"
        />
      </label>
      <label className="wide-field">
        <span className="field-label">Text or JSON payload</span>
        <textarea
          id={contentId}
          className="text-area"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Minimal source create payload. Full file upload and format support are future backend capabilities."
        />
      </label>
      {createSource.error ? <ApiErrorState title="Source import failed" error={createSource.error} /> : null}
      <button className="primary-button" type="submit" disabled={createSource.isPending || !title.trim()}>
        {createSource.isPending ? 'Importing' : 'Import source'}
      </button>
    </form>
  );
}

function SourceLibrary({
  workspaceId,
  onTrace,
  onAsk,
  onRebuild
}: {
  workspaceId: string;
  onTrace: (source: SourceSummary) => void;
  onAsk: () => void;
  onRebuild: () => void;
}) {
  const sourcesQuery = useSourcesQuery(workspaceId);
  const removeSource = useRemoveSourceMutation(workspaceId);

  return (
    <section className="panel" aria-labelledby="source-library-title">
      <div className="panel-header">
        <h2 id="source-library-title">Source Library</h2>
      </div>
      <div className="panel-body page-grid">
        <SourceImportForm workspaceId={workspaceId} />
        {sourcesQuery.isLoading ? <LoadingState label="Loading sources" /> : null}
        {sourcesQuery.error ? (
          <ApiErrorState title="Source library unavailable" error={sourcesQuery.error} onRetry={() => void sourcesQuery.refetch()} />
        ) : null}
        {removeSource.error ? <ApiErrorState title="Remove source failed" error={removeSource.error} /> : null}
        {sourcesQuery.data && sourcesQuery.data.length === 0 ? (
          <EmptyState title="No sources yet">Import a source before building workspace knowledge.</EmptyState>
        ) : null}
        {sourcesQuery.data && sourcesQuery.data.length > 0 ? (
          <div className="source-list">
            {sourcesQuery.data.map((source) => (
              <article className="source-card" key={source.source_id}>
                <div>
                  <div className="source-title-row">
                    <h3>{source.title}</h3>
                    <SourceStateBadge source={source} />
                  </div>
                  <dl className="source-meta-grid">
                    <div>
                      <dt>source_id</dt>
                      <dd>{source.source_id}</dd>
                    </div>
                    <div>
                      <dt>type</dt>
                      <dd>{source.source_type || 'service-defined'}</dd>
                    </div>
                    <div>
                      <dt>updated</dt>
                      <dd>{source.updated_at || 'unknown'}</dd>
                    </div>
                    <div>
                      <dt>artifact refs</dt>
                      <dd>{source.artifact_refs?.length ? `${source.artifact_refs.length} present` : 'none'}</dd>
                    </div>
                    <div>
                      <dt>trace</dt>
                      <dd>{source.trace_available ? 'available' : 'unavailable'}</dd>
                    </div>
                  </dl>
                </div>
                <div className="source-actions">
                  <button className="secondary-button" type="button" onClick={() => onTrace(source)} disabled={!source.trace_available}>
                    Trace
                  </button>
                  <button className="secondary-button" type="button" onClick={onAsk}>
                    Ask workspace
                  </button>
                  <button className="secondary-button" type="button" onClick={onRebuild}>
                    Rebuild workspace knowledge
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => removeSource.mutate(source.source_id)}
                    disabled={removeSource.isPending}
                  >
                    Remove
                  </button>
                </div>
              </article>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
}

function BuildPanel({ workspaceId, rebuildSignal }: { workspaceId: string; rebuildSignal: number }) {
  const queryClient = useQueryClient();
  const [activeOperationId, setActiveOperationId] = useState<string | null>(null);
  const startBuild = useStartBuildMutation(workspaceId);
  const lastRebuildSignalRef = useRef(0);

  const onCompleted = useCallback(
    async (operation: BuildOperation) => {
      if (operation.status === 'completed') {
        await queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) });
      }
    },
    [queryClient, workspaceId]
  );

  const polling = useOperationPolling({
    operationId: activeOperationId,
    scope: 'workspace',
    staleKey: workspaceId,
    getStatus: () => dataServiceClient.build.getOperation(workspaceId, activeOperationId ?? ''),
    cancel: () => dataServiceClient.build.cancel(workspaceId, activeOperationId ?? ''),
    onCompleted
  });

  const start = useCallback(() => {
    startBuild.mutate(
      { reason: 'workspace_rebuild' },
      {
        onSuccess: (response) => setActiveOperationId(response.operation_id)
      }
    );
  }, [startBuild]);

  useEffect(() => {
    if (rebuildSignal > 0 && rebuildSignal !== lastRebuildSignalRef.current) {
      lastRebuildSignalRef.current = rebuildSignal;
      start();
    }
  }, [rebuildSignal, start]);

  return (
    <section className="panel" aria-labelledby="build-panel-title">
      <div className="panel-header">
        <h2 id="build-panel-title">Workspace Build</h2>
      </div>
      <div className="panel-body page-grid">
        {startBuild.error ? <ApiErrorState title="Build start failed" error={startBuild.error} /> : null}
        <div className="toolbar-row">
          <div>
            <div className="workspace-meta">Active operation</div>
            <strong>{activeOperationId ?? 'none'}</strong>
          </div>
          <button className="primary-button" type="button" onClick={start} disabled={startBuild.isPending}>
            {startBuild.isPending ? 'Starting' : 'Rebuild workspace knowledge'}
          </button>
        </div>
        <StateBlock
          title={`Build status: ${polling.uiState}`}
          tone={polling.uiState === 'failed' || polling.uiState === 'operation_unavailable' ? 'error' : 'neutral'}
          action={
            polling.canCancel ? (
              <button className="secondary-button" type="button" onClick={() => void polling.cancelOperation()} disabled={polling.isCancelling}>
                {polling.isCancelling ? 'Cancelling' : 'Cancel'}
              </button>
            ) : null
          }
        >
          {polling.operation?.message || 'Workspace build status is shown for the active workspace operation only.'}
        </StateBlock>
      </div>
    </section>
  );
}

function WorkspaceQueryPanel({
  workspaceId,
  onTraceSourceId,
  focusSignal
}: {
  workspaceId: string;
  onTraceSourceId: (sourceId: string) => void;
  focusSignal: number;
}) {
  const questionId = useId();
  const [question, setQuestion] = useState('');
  const queryWorkspace = useWorkspaceQueryMutation(workspaceId);

  useEffect(() => {
    if (focusSignal > 0) {
      document.getElementById(questionId)?.focus();
    }
  }, [focusSignal, questionId]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    queryWorkspace.mutate({ question: trimmed });
  };

  return (
    <section className="panel" aria-labelledby="workspace-query-title">
      <div className="panel-header">
        <h2 id="workspace-query-title">Ask with Evidence</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label className="wide-field">
            <span className="field-label">Question</span>
            <textarea
              id={questionId}
              className="text-area"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Ask a question against this workspace."
            />
          </label>
          <button className="primary-button" type="submit" disabled={queryWorkspace.isPending || !question.trim()}>
            {queryWorkspace.isPending ? 'Asking' : 'Ask workspace'}
          </button>
        </form>
        {queryWorkspace.error ? <ApiErrorState title="Workspace query failed" error={queryWorkspace.error} /> : null}
        {queryWorkspace.data ? (
          <article className="answer-card">
            <h3>Answer</h3>
            <p>{queryWorkspace.data.answer}</p>
            <EvidenceList evidence={queryWorkspace.data.evidence} onTrace={onTraceSourceId} />
            <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'workspace_answer' }} />
          </article>
        ) : null}
      </div>
    </section>
  );
}

export function WorkspacePage() {
  const { workspaceId = '' } = useParams();
  const workspaceQuery = useWorkspaceQuery(workspaceId);
  const archiveWorkspace = useArchiveWorkspaceMutation(workspaceId);
  const [traceSourceId, setTraceSourceId] = useState<string | null>(null);
  const [rebuildSignal, setRebuildSignal] = useState(0);
  const [askFocusSignal, setAskFocusSignal] = useState(0);

  if (workspaceQuery.isLoading) {
    return <LoadingState label="Loading workspace" />;
  }

  if (workspaceQuery.error) {
    if (isNormalizedApiError(workspaceQuery.error)) {
      if (workspaceQuery.error.code === 'backend_unavailable' || workspaceQuery.error.code === 'request_timeout') {
        return <BackendUnavailableState onRetry={() => void workspaceQuery.refetch()} />;
      }
      if (workspaceQuery.error.code === 'version_or_schema_mismatch') {
        return <VersionMismatchState />;
      }
      return <StateBlock title="Workspace unavailable" tone="error">{workspaceQuery.error.message}</StateBlock>;
    }
    return <StateBlock title="Workspace unavailable" tone="error">The workspace could not be loaded.</StateBlock>;
  }

  const workspace = workspaceQuery.data;

  return (
    <div className="workspace-layout">
      <div className="workspace-main page-grid">
        <div className="toolbar-row">
          <div>
            <div className="eyebrow">Workspace</div>
            <h2 className="page-title">{workspace?.name ?? workspaceId}</h2>
          </div>
          <button
            className="secondary-button"
            type="button"
            onClick={() => archiveWorkspace.mutate()}
            disabled={archiveWorkspace.isPending || workspace?.archived}
          >
            {workspace?.archived ? 'Archived' : 'Archive'}
          </button>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/workbench`}>
            Workbench
          </Link>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/graph`}>
            Graph
          </Link>
        </div>

        {archiveWorkspace.error ? (
          <StateBlock title="Archive failed" tone="error">
            {isNormalizedApiError(archiveWorkspace.error)
              ? archiveWorkspace.error.message
              : 'The workspace could not be archived.'}
          </StateBlock>
        ) : null}

        <section className="panel">
          <div className="panel-header">
            <h2>Workspace overview</h2>
          </div>
          <div className="panel-body">
            <p className="workspace-meta">Stable ID: {workspace?.workspace_id}</p>
            <p>{workspace?.description || 'No description provided.'}</p>
          </div>
        </section>

        <BuildPanel workspaceId={workspaceId} rebuildSignal={rebuildSignal} />
        <SourceLibrary
          workspaceId={workspaceId}
          onTrace={(source) => setTraceSourceId(source.source_id)}
          onAsk={() => setAskFocusSignal((value) => value + 1)}
          onRebuild={() => setRebuildSignal((value) => value + 1)}
        />
        <WorkspaceQueryPanel workspaceId={workspaceId} onTraceSourceId={setTraceSourceId} focusSignal={askFocusSignal} />
      </div>
      <SourceTraceDrawer workspaceId={workspaceId} sourceId={traceSourceId} onClose={() => setTraceSourceId(null)} />
    </div>
  );
}
