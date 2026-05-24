import { isNormalizedApiError } from '../api/dataServiceClient';
import { useSourceQuery, useSourceTraceQuery } from '../api/workspaceM2Queries';
import { LoadingState, StateBlock } from './StateBlock';
import { ApiErrorState } from './ApiErrorState';

export function SourceTraceDrawer({
  workspaceId,
  sourceId,
  onClose
}: {
  workspaceId: string;
  sourceId: string | null;
  onClose: () => void;
}) {
  const traceQuery = useSourceTraceQuery(workspaceId, sourceId);
  const sourceQuery = useSourceQuery(workspaceId, sourceId);
  if (!sourceId) return null;
  const traceNotFound = isNormalizedApiError(traceQuery.error) && traceQuery.error.code === 'not_found';

  return (
    <aside className="trace-drawer" aria-label="来源溯源抽屉">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">来源溯源</div>
          <h2>来源与出处</h2>
        </div>
        <button className="secondary-button" type="button" onClick={onClose}>
          关闭
        </button>
      </div>
      {traceQuery.isLoading ? <LoadingState label="正在加载溯源" /> : null}
      {traceQuery.error && !traceNotFound ? (
        <ApiErrorState title="溯源不可用" error={traceQuery.error} onRetry={() => void traceQuery.refetch()} />
      ) : null}
      {traceNotFound && sourceQuery.isLoading ? <LoadingState label="正在加载来源元数据" /> : null}
      {traceNotFound && sourceQuery.data ? (
        <div className="trace-content">
          <StateBlock title="溯源不可用" tone="warning">
            后端可以识别该来源，但当前来源溯源路由没有返回出处信息。
          </StateBlock>
          <p className="workspace-meta">来源 ID：{sourceQuery.data.source_id}</p>
          <h3>{sourceQuery.data.title || sourceId}</h3>
          <div className="trace-section">
            <h4>工件引用</h4>
            {sourceQuery.data.artifact_refs?.length ? (
              <ul>
                {sourceQuery.data.artifact_refs.map((ref) => (
                  <li key={ref}>{ref}</li>
                ))}
              </ul>
            ) : (
              <p className="workspace-meta">未返回工件引用。</p>
            )}
          </div>
          <button className="secondary-button" type="button" onClick={() => void traceQuery.refetch()}>
            重试溯源
          </button>
        </div>
      ) : null}
      {traceNotFound && sourceQuery.error ? (
        <ApiErrorState title="未找到来源" error={sourceQuery.error} onRetry={() => void sourceQuery.refetch()} />
      ) : null}
      {traceQuery.data ? (
        <div className="trace-content">
          <p className="workspace-meta">来源 ID：{traceQuery.data.source_id}</p>
          <h3>{traceQuery.data.title || sourceId}</h3>
          {traceQuery.data.summary ? <p>{traceQuery.data.summary}</p> : null}
          <div className="trace-section">
            <h4>工件引用</h4>
            {traceQuery.data.artifact_refs?.length ? (
              <ul>
                {traceQuery.data.artifact_refs.map((ref) => (
                  <li key={ref}>{ref}</li>
                ))}
              </ul>
            ) : (
              <p className="workspace-meta">未返回工件引用。</p>
            )}
          </div>
          <div className="trace-section">
            <h4>出处信息</h4>
            {traceQuery.data.provenance?.length ? (
              <dl>
                {traceQuery.data.provenance.map((item) => (
                  <div key={`${item.label}-${item.value}`}>
                    <dt>{item.label}</dt>
                    <dd>{item.value}</dd>
                  </div>
                ))}
              </dl>
            ) : (
              <p className="workspace-meta">溯源路由没有返回出处行。</p>
            )}
          </div>
        </div>
      ) : null}
    </aside>
  );
}
