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
import { isEvidenceSpanNavigationSupported, useCapabilitiesQuery } from '../../shared/api/workspaceM2Queries';
import { queryKeys } from '../../app/routes/queryKeys';
import { useOperationPolling } from '../../shared/hooks/useOperationPolling';
import type { AnswerEvidence, BuildOperation, SessionDetail, SessionState, SessionSummary } from '../../shared/types/api';
import { ApiErrorState } from '../../shared/components/ApiErrorState';
import { EvidenceList } from '../../shared/components/EvidenceList';
import { SourceTraceDrawer } from '../../shared/components/SourceTraceDrawer';
import { SourcePreviewDrawer } from '../../shared/components/SourcePreviewDrawer';
import { EmptyState, LoadingState, StateBlock, UnsupportedFeatureState } from '../../shared/components/StateBlock';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';
import { SessionGraphContext } from '../../shared/components/GraphContextPanel';

function visibleSessionState(state?: SessionState) {
  if (state === 'closed') return '已关闭';
  if (state === 'building') return '构建中';
  if (state === 'ready') return '就绪';
  if (state === 'ingested_not_built') return '需要构建';
  if (state === 'failed_build' || state === 'failed_ingest') return '失败';
  return '活跃';
}

function operationStateLabel(state: string) {
  const labels: Record<string, string> = {
    idle: '空闲',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelling: '取消中',
    cancelled: '已取消',
    backend_unavailable: '后端不可用',
    request_timeout: '请求超时',
    operation_unavailable: '操作不可用'
  };
  return labels[state] ?? state;
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
    <form className="session-create-form" onSubmit={submit} aria-label="创建会话">
      <label>
        <span className="field-label">会话标题</span>
        <input id={titleId} className="text-input" value={title} onChange={(event) => setTitle(event.target.value)} />
      </label>
      {createSession.error ? <ApiErrorState title="创建会话失败" error={createSession.error} /> : null}
      <button className="primary-button" type="submit" disabled={createSession.isPending || !title.trim()}>
        {createSession.isPending ? '创建中' : '创建会话'}
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
        <h2 id="session-list-title">会话列表</h2>
      </div>
      <div className="panel-body page-grid">
        <SessionCreateForm workspaceId={workspaceId} onCreated={onSelect} />
        {sessionsQuery.isLoading ? <LoadingState label="正在加载会话" /> : null}
        {sessionsQuery.error ? (
          <ApiErrorState title="会话列表不可用" error={sessionsQuery.error} onRetry={() => void sessionsQuery.refetch()} />
        ) : null}
        {sessionsQuery.data && sessionsQuery.data.length === 0 ? (
          <EmptyState title="暂无会话">创建一个会话，开始专注工作台流程。</EmptyState>
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
        <h2 id="session-summary-title">会话上下文</h2>
      </div>
      <div className="panel-body page-grid">
        <div className="toolbar-row">
          <div>
            <div className="eyebrow">当前会话</div>
            <h3>{session.title}</h3>
          </div>
          <span className={`state-pill state-${session.state}`}>{visibleSessionState(session.state)}</span>
        </div>
        <dl className="source-meta-grid">
          <div>
            <dt>会话 ID</dt>
            <dd>{session.session_id}</dd>
          </div>
          <div>
            <dt>工件引用</dt>
            <dd>{session.artifact_refs?.length ? `${session.artifact_refs.length} 个` : '无'}</dd>
          </div>
          <div>
            <dt>来源上下文</dt>
            <dd>{session.source_ids?.length ? `${session.source_ids.length} 个来源` : '无'}</dd>
          </div>
        </dl>
        <p>{session.context_summary || '尚未返回会话上下文摘要。'}</p>
        {closeSession.error ? <ApiErrorState title="关闭会话失败" error={closeSession.error} /> : null}
        <button className="secondary-button" type="button" onClick={close} disabled={isClosed || closeSession.isPending}>
          {isClosed ? '已关闭' : closeSession.isPending ? '关闭中' : '关闭会话'}
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
        <h2 id="session-ingest-title">片段导入</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label>
            <span className="field-label">上下文标签</span>
            <input id={labelId} className="text-input" value={label} onChange={(event) => setLabel(event.target.value)} disabled={isClosed} />
          </label>
          <label className="wide-field">
            <span className="field-label">片段或上下文</span>
            <textarea
              id={contentId}
              className="text-area"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              disabled={isClosed}
              placeholder="这里只导入会话范围内的文本或上下文；来源导入和文件上传请在来源库处理。"
            />
          </label>
          {ingest.error ? <ApiErrorState title="会话片段导入失败" error={ingest.error} /> : null}
          <button className="primary-button" type="submit" disabled={isClosed || ingest.isPending || !content.trim()}>
            {isClosed ? '会话已关闭' : ingest.isPending ? '导入中' : '导入片段'}
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
        <h2 id="session-build-title">会话构建</h2>
      </div>
      <div className="panel-body page-grid">
        {startBuild.error ? <ApiErrorState title="启动会话构建失败" error={startBuild.error} /> : null}
        <div className="toolbar-row">
          <div>
            <div className="workspace-meta">当前会话操作</div>
            <strong>{activeOperationId ?? '无'}</strong>
          </div>
          <button className="primary-button" type="button" onClick={start} disabled={isClosed || startBuild.isPending}>
            {isClosed ? '会话已关闭' : startBuild.isPending ? '启动中' : '构建会话'}
          </button>
        </div>
        <StateBlock
          title={`会话构建状态：${operationStateLabel(polling.uiState)}`}
          tone={polling.uiState === 'failed' || polling.uiState === 'operation_unavailable' ? 'error' : 'neutral'}
          action={
            polling.canCancel ? (
              <button className="secondary-button" type="button" onClick={() => void polling.cancelOperation()} disabled={polling.isCancelling}>
                {polling.isCancelling ? '取消中' : '取消'}
              </button>
            ) : null
          }
        >
          {polling.operation?.message || '这里只显示当前选中会话的构建状态。'}
        </StateBlock>
      </div>
    </section>
  );
}

function SessionAskPanel({
  workspaceId,
  session,
  onTraceSourceId,
  onNavigateEvidence
}: {
  workspaceId: string;
  session: SessionSummary;
  onTraceSourceId: (sourceId: string) => void;
  onNavigateEvidence: (evidence: AnswerEvidence) => void;
}) {
  const questionId = useId();
  const [question, setQuestion] = useState('');
  const isClosed = session.state === 'closed';
  const querySession = useSessionQueryMutation(workspaceId, session.session_id);
  const sourcesQuery = useSourcesQuery(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const preciseNavigationEnabled = isEvidenceSpanNavigationSupported(capabilitiesQuery.data);

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
        <h2 id="session-query-title">会话提问</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label className="wide-field">
            <span className="field-label">会话问题</span>
            <textarea
              id={questionId}
              className="text-area"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              disabled={isClosed}
              placeholder="基于当前会话上下文提问。"
            />
          </label>
          <button className="primary-button" type="submit" disabled={isClosed || querySession.isPending || !question.trim()}>
            {isClosed ? '会话已关闭' : querySession.isPending ? '提问中' : '询问会话'}
          </button>
        </form>
        {querySession.error ? <ApiErrorState title="会话提问失败" error={querySession.error} /> : null}
        {querySession.data ? (
          <article className="answer-card">
            <h3>会话回答</h3>
            <p>{querySession.data.answer}</p>
            <EvidenceList
              evidence={querySession.data.evidence}
              onTrace={onTraceSourceId}
              onNavigateEvidence={onNavigateEvidence}
              preciseNavigationEnabled={preciseNavigationEnabled}
            />
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
        <h2 id="session-graph-title">只读会话图谱</h2>
      </div>
      <div className="panel-body page-grid">
        {graphQuery.isLoading ? <LoadingState label="正在加载会话图谱" /> : null}
        {graphQuery.error ? (
          <ApiErrorState title="会话图谱不可用" error={graphQuery.error} onRetry={() => void graphQuery.refetch()} />
        ) : null}
        {graphQuery.data ? <SessionGraphContext graph={graphQuery.data} /> : null}
      </div>
    </section>
  );
}

function SessionWorkbench({ workspaceId, activeSessionId, onSessionClosed }: { workspaceId: string; activeSessionId: string | null; onSessionClosed: () => void }) {
  const [traceSourceId, setTraceSourceId] = useState<string | null>(null);
  const [previewSource, setPreviewSource] = useState<{
    source_id: string;
    title?: string;
    unitId?: string;
    evidenceId?: string;
    evidenceKey?: string;
  } | null>(null);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const preciseNavigationEnabled = isEvidenceSpanNavigationSupported(capabilitiesQuery.data);
  const sessionQuery = useSessionQuery(workspaceId, activeSessionId);

  if (!activeSessionId) {
    return <EmptyState title="暂无活跃会话">请选择或创建一个会话后再使用工作台。</EmptyState>;
  }
  if (sessionQuery.isLoading) return <LoadingState label="正在加载会话" />;
  if (sessionQuery.error) {
    return <ApiErrorState title="会话不可用" error={sessionQuery.error} onRetry={() => void sessionQuery.refetch()} />;
  }
  if (!sessionQuery.data) return <EmptyState title="会话不可用">选中的会话没有返回详情。</EmptyState>;

  const session = sessionQuery.data;

  return (
    <div className="session-workbench-main page-grid">
      <SessionSummaryPanel workspaceId={workspaceId} session={session} onClosed={onSessionClosed} />
      <SessionIngestPanel workspaceId={workspaceId} session={session} />
      <SessionBuildPanel workspaceId={workspaceId} session={session} />
      <SessionGraphPanel workspaceId={workspaceId} sessionId={session.session_id} />
      <SessionAskPanel
        workspaceId={workspaceId}
        session={session}
        onTraceSourceId={setTraceSourceId}
        onNavigateEvidence={(evidence) => {
          if (!evidence.sourceId) return;
          setPreviewSource({
            source_id: evidence.sourceId,
            title: evidence.sourceTitle,
            unitId: evidence.unitId,
            evidenceId: evidence.evidenceId,
            evidenceKey: evidence.evidenceKey
          });
        }}
      />
      {session.last_answer ? (
        <article className="answer-card">
          <h3>上次回答</h3>
          <p>{session.last_answer.answer}</p>
          <EvidenceList
            evidence={session.last_answer.evidence}
            onTrace={setTraceSourceId}
            onNavigateEvidence={(evidence) => {
              if (!evidence.sourceId) return;
              setPreviewSource({
                source_id: evidence.sourceId,
                title: evidence.sourceTitle,
                unitId: evidence.unitId,
                evidenceId: evidence.evidenceId,
                evidenceKey: evidence.evidenceKey
              });
            }}
            preciseNavigationEnabled={preciseNavigationEnabled}
          />
          <LightweightFeedback workspaceId={workspaceId} target={{ target_type: 'session_answer', session_id: session.session_id }} />
        </article>
      ) : null}
      <SourceTraceDrawer workspaceId={workspaceId} sourceId={traceSourceId} onClose={() => setTraceSourceId(null)} />
      <SourcePreviewDrawer
        workspaceId={workspaceId}
        sourceId={previewSource?.source_id ?? null}
        sourceTitle={previewSource?.title}
        initialEvidence={
          previewSource?.unitId || previewSource?.evidenceId
            ? { unitId: previewSource.unitId, evidenceId: previewSource.evidenceId, evidenceKey: previewSource.evidenceKey }
            : null
        }
        onClose={() => setPreviewSource(null)}
      />
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
      <UnsupportedFeatureState title="请先从工作区打开会话工作台">
        会话工作台属于具体工作区。请先打开一个工作区，再进入会话工作台。
      </UnsupportedFeatureState>
    );
  }

  return (
    <div className="session-workbench">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">会话</div>
          <h2 className="page-title">会话工作台</h2>
        </div>
        <Link className="secondary-button" to={`/workspaces/${workspaceId}`}>
          返回工作区
        </Link>
      </div>
      <div className="session-workbench-grid">
        <SessionList workspaceId={workspaceId} activeSessionId={activeSessionId} onSelect={setActiveSessionId} />
        <SessionWorkbench workspaceId={workspaceId} activeSessionId={activeSessionId} onSessionClosed={() => undefined} />
      </div>
    </div>
  );
}
