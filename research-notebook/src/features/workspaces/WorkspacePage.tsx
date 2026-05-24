import { FormEvent, useCallback, useEffect, useId, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { isNormalizedApiError, dataServiceClient } from '../../shared/api/dataServiceClient';
import { useArchiveWorkspaceMutation, useWorkspaceQuery } from '../../shared/api/workspaceQueries';
import {
  useCreateSourceMutation,
  useCapabilitiesQuery,
  isSourceLevelPreviewSupported,
  useRemoveSourceMutation,
  useSourcesQuery,
  useStartBuildMutation,
  useWorkspaceQueryMutation
} from '../../shared/api/workspaceM2Queries';
import { queryKeys } from '../../app/routes/queryKeys';
import { useOperationPolling } from '../../shared/hooks/useOperationPolling';
import type { AnswerEvidence, BuildOperation, SourceSummary } from '../../shared/types/api';
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
import { SourcePreviewDrawer } from '../../shared/components/SourcePreviewDrawer';
import { LightweightFeedback } from '../../shared/components/LightweightFeedback';

function SourceStateBadge({ source }: { source: SourceSummary }) {
  const state = source.build_state ?? source.import_state ?? 'idle';
  const labels: Record<string, string> = {
    idle: '空闲',
    pending: '等待中',
    importing: '导入中',
    imported: '已导入',
    building: '构建中',
    ready: '就绪',
    failed: '失败',
    unsupported_type: '暂不支持'
  };
  return <span className={`state-pill state-${state}`}>{labels[state] ?? state}</span>;
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

function SourceImportForm({ workspaceId }: { workspaceId: string }) {
  const titleId = useId();
  const typeId = useId();
  const contentId = useId();
  const [title, setTitle] = useState('');
  const [sourceType, setSourceType] = useState('text');
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
          setSourceType('text');
          setContent('');
        }
      }
    );
  };

  return (
    <form className="source-import-form" onSubmit={submit} aria-label="导入来源">
      <label>
        <span className="field-label">来源标题</span>
        <input id={titleId} className="text-input" value={title} onChange={(event) => setTitle(event.target.value)} />
      </label>
      <label>
        <span className="field-label">来源类型</span>
        <select
          id={typeId}
          className="text-input"
          value={sourceType}
          onChange={(event) => setSourceType(event.target.value)}
        >
          <option value="text">文本：已验证</option>
          <option value="markdown">Markdown：已验证</option>
          <option value="json">JSON：已验证</option>
          <option value="pdf">PDF：后端合同待就绪</option>
          <option value="pptx">PPTX：后端合同待就绪</option>
          <option value="html">HTML：后端合同待就绪</option>
          <option value="video">视频：后端合同待就绪</option>
          <option value="audio">音频：后端合同待就绪</option>
        </select>
      </label>
      <label className="wide-field">
        <span className="field-label">文本或结构化内容</span>
        <textarea
          id={contentId}
          className="text-area"
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="当前支持最小文本内容。完整文件上传和更多格式支持仍是后续能力。"
        />
      </label>
      <StateBlock title="格式支持边界">
        当前已通过浏览器验收的来源类型是文本、Markdown 和 JSON。PDF、PPTX、HTML、视频、音频会作为来源类型元数据提交，但不能声明预览、文档单元或证据高亮 ready。
      </StateBlock>
      {createSource.error ? <ApiErrorState title="来源导入失败" error={createSource.error} /> : null}
      <button className="primary-button" type="submit" disabled={createSource.isPending || !title.trim()}>
        {createSource.isPending ? '导入中' : '导入来源'}
      </button>
    </form>
  );
}

function SourceLibrary({
  workspaceId,
  onTrace,
  onPreview,
  onAsk,
  onRebuild
}: {
  workspaceId: string;
  onTrace: (source: SourceSummary) => void;
  onPreview: (source: SourceSummary) => void;
  onAsk: () => void;
  onRebuild: () => void;
}) {
  const sourcesQuery = useSourcesQuery(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const removeSource = useRemoveSourceMutation(workspaceId);

  return (
    <section className="panel" aria-labelledby="source-library-title">
      <div className="panel-header">
        <h2 id="source-library-title">来源库</h2>
      </div>
      <div className="panel-body page-grid">
        <SourceImportForm workspaceId={workspaceId} />
        {sourcesQuery.isLoading ? <LoadingState label="正在加载来源" /> : null}
        {sourcesQuery.error ? (
          <ApiErrorState title="来源库不可用" error={sourcesQuery.error} onRetry={() => void sourcesQuery.refetch()} />
        ) : null}
        {removeSource.error ? <ApiErrorState title="移除来源失败" error={removeSource.error} /> : null}
        {sourcesQuery.data && sourcesQuery.data.length === 0 ? (
          <EmptyState title="暂无来源">请先导入来源，再构建工作区知识。</EmptyState>
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
                      <dt>来源 ID</dt>
                      <dd>{source.source_id}</dd>
                    </div>
                    <div>
                      <dt>类型</dt>
                      <dd>{source.source_type || '服务定义'}</dd>
                    </div>
                    <div>
                      <dt>更新时间</dt>
                      <dd>{source.updated_at || '未知'}</dd>
                    </div>
                    <div>
                      <dt>工件引用</dt>
                      <dd>{source.artifact_refs?.length ? `${source.artifact_refs.length} 个` : '无'}</dd>
                    </div>
                    <div>
                      <dt>来源溯源</dt>
                      <dd>{source.trace_available ? '可用' : '不可用'}</dd>
                    </div>
                  </dl>
                </div>
                <div className="source-actions">
                  <button className="secondary-button" type="button" onClick={() => onTrace(source)} disabled={!source.trace_available}>
                    溯源
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => onPreview(source)}
                    disabled={Boolean(
                      capabilitiesQuery.data && !isSourceLevelPreviewSupported(capabilitiesQuery.data, source.source_type)
                    )}
                    title={
                      capabilitiesQuery.data && !isSourceLevelPreviewSupported(capabilitiesQuery.data, source.source_type)
                        ? '该来源类型未声明支持预览。'
                        : undefined
                    }
                  >
                    预览
                  </button>
                  <button className="secondary-button" type="button" onClick={onAsk}>
                    提问
                  </button>
                  <button className="secondary-button" type="button" onClick={onRebuild}>
                    重建知识
                  </button>
                  <button
                    className="secondary-button"
                    type="button"
                    onClick={() => removeSource.mutate(source.source_id)}
                    disabled={removeSource.isPending}
                  >
                    移除
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
        <h2 id="build-panel-title">工作区构建</h2>
      </div>
      <div className="panel-body page-grid">
        {startBuild.error ? <ApiErrorState title="启动构建失败" error={startBuild.error} /> : null}
        <div className="toolbar-row">
          <div>
            <div className="workspace-meta">当前操作</div>
            <strong>{activeOperationId ?? '无'}</strong>
          </div>
          <button className="primary-button" type="button" onClick={start} disabled={startBuild.isPending}>
            {startBuild.isPending ? '启动中' : '重建工作区知识'}
          </button>
        </div>
        <StateBlock
          title={`构建状态：${operationStateLabel(polling.uiState)}`}
          tone={polling.uiState === 'failed' || polling.uiState === 'operation_unavailable' ? 'error' : 'neutral'}
          action={
            polling.canCancel ? (
              <button className="secondary-button" type="button" onClick={() => void polling.cancelOperation()} disabled={polling.isCancelling}>
                {polling.isCancelling ? '取消中' : '取消'}
              </button>
            ) : null
          }
        >
          {polling.operation?.message || '这里只显示当前工作区操作的构建状态。'}
        </StateBlock>
      </div>
    </section>
  );
}

function WorkspaceQueryPanel({
  workspaceId,
  onTraceSourceId,
  onNavigateEvidence,
  focusSignal
}: {
  workspaceId: string;
  onTraceSourceId: (sourceId: string) => void;
  onNavigateEvidence: (evidence: AnswerEvidence) => void;
  focusSignal: number;
}) {
  const questionId = useId();
  const [question, setQuestion] = useState('');
  const queryWorkspace = useWorkspaceQueryMutation(workspaceId);
  const sourcesQuery = useSourcesQuery(workspaceId);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const preciseNavigationEnabled = Boolean(
    capabilitiesQuery.data?.capabilities.evidence_spans &&
      capabilitiesQuery.data.capabilities.precise_span_highlight &&
      capabilitiesQuery.data.capabilities.citation_backjump &&
      capabilitiesQuery.data.capabilities.document_units &&
      capabilitiesQuery.data.capabilities.unit_level_navigation
  );

  useEffect(() => {
    if (focusSignal > 0) {
      document.getElementById(questionId)?.focus();
    }
  }, [focusSignal, questionId]);

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) return;
    queryWorkspace.mutate({
      question: trimmed,
      registrySourceIds: sourcesQuery.data?.map((source) => source.source_id)
    });
  };

  return (
    <section className="panel" aria-labelledby="workspace-query-title">
      <div className="panel-header">
        <h2 id="workspace-query-title">带证据提问</h2>
      </div>
      <div className="panel-body page-grid">
        <form className="ask-form" onSubmit={submit}>
          <label className="wide-field">
            <span className="field-label">问题</span>
            <textarea
              id={questionId}
              className="text-area"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="基于当前工作区提问。"
            />
          </label>
          <button className="primary-button" type="submit" disabled={queryWorkspace.isPending || !question.trim()}>
            {queryWorkspace.isPending ? '提问中' : '询问工作区'}
          </button>
        </form>
        {queryWorkspace.error ? <ApiErrorState title="工作区提问失败" error={queryWorkspace.error} /> : null}
        {queryWorkspace.data ? (
          <article className="answer-card">
            <h3>回答</h3>
            <p>{queryWorkspace.data.answer}</p>
            <EvidenceList
              evidence={queryWorkspace.data.evidence}
              onTrace={onTraceSourceId}
              onNavigateEvidence={onNavigateEvidence}
              preciseNavigationEnabled={preciseNavigationEnabled}
            />
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
  const [previewSource, setPreviewSource] = useState<{
    source_id: string;
    title?: string;
    source_type?: string;
    unitId?: string;
    evidenceId?: string;
    evidenceKey?: string;
  } | null>(null);
  const [rebuildSignal, setRebuildSignal] = useState(0);
  const [askFocusSignal, setAskFocusSignal] = useState(0);

  if (workspaceQuery.isLoading) {
    return <LoadingState label="正在加载工作区" />;
  }

  if (workspaceQuery.error) {
    if (isNormalizedApiError(workspaceQuery.error)) {
      if (workspaceQuery.error.code === 'backend_unavailable' || workspaceQuery.error.code === 'request_timeout') {
        return <BackendUnavailableState onRetry={() => void workspaceQuery.refetch()} />;
      }
      if (workspaceQuery.error.code === 'version_or_schema_mismatch') {
        return <VersionMismatchState />;
      }
      return <StateBlock title="工作区不可用" tone="error">{workspaceQuery.error.message}</StateBlock>;
    }
    return <StateBlock title="工作区不可用" tone="error">工作区无法加载。</StateBlock>;
  }

  const workspace = workspaceQuery.data;

  return (
    <div className="workspace-layout">
      <div className="workspace-main page-grid">
        <div className="toolbar-row">
          <div>
            <div className="eyebrow">工作区</div>
            <h2 className="page-title">{workspace?.name ?? workspaceId}</h2>
          </div>
          <button
            className="secondary-button"
            type="button"
            onClick={() => archiveWorkspace.mutate()}
            disabled={archiveWorkspace.isPending || workspace?.archived}
          >
            {workspace?.archived ? '已归档' : '归档'}
          </button>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/workbench`}>
            会话工作台
          </Link>
          <Link className="secondary-button" to={`/workspaces/${workspaceId}/graph`}>
            知识图谱
          </Link>
        </div>

        {archiveWorkspace.error ? (
          <StateBlock title="归档失败" tone="error">
            {isNormalizedApiError(archiveWorkspace.error)
              ? archiveWorkspace.error.message
              : '工作区无法归档。'}
          </StateBlock>
        ) : null}

        <section className="panel">
          <div className="panel-header">
            <h2>工作区概览</h2>
          </div>
          <div className="panel-body">
            <p className="workspace-meta">稳定 ID：{workspace?.workspace_id}</p>
            <p>{workspace?.description || '暂无描述。'}</p>
          </div>
        </section>

        <BuildPanel workspaceId={workspaceId} rebuildSignal={rebuildSignal} />
        <SourceLibrary
          workspaceId={workspaceId}
          onTrace={(source) => setTraceSourceId(source.source_id)}
          onPreview={(source) =>
            setPreviewSource({ source_id: source.source_id, title: source.title, source_type: source.source_type })
          }
          onAsk={() => setAskFocusSignal((value) => value + 1)}
          onRebuild={() => setRebuildSignal((value) => value + 1)}
        />
        <WorkspaceQueryPanel
          workspaceId={workspaceId}
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
          focusSignal={askFocusSignal}
        />
      </div>
      <SourceTraceDrawer workspaceId={workspaceId} sourceId={traceSourceId} onClose={() => setTraceSourceId(null)} />
      <SourcePreviewDrawer
        workspaceId={workspaceId}
        sourceId={previewSource?.source_id ?? null}
        sourceTitle={previewSource?.title}
        sourceType={previewSource?.source_type}
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
