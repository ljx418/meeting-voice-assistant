import { useSourceTraceQuery } from '../api/workspaceM2Queries';
import { LoadingState } from './StateBlock';
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
  if (!sourceId) return null;

  return (
    <aside className="trace-drawer" aria-label="Source trace drawer">
      <div className="toolbar-row">
        <div>
          <div className="eyebrow">Source Trace</div>
          <h2>Provenance</h2>
        </div>
        <button className="secondary-button" type="button" onClick={onClose}>
          Close
        </button>
      </div>
      {traceQuery.isLoading ? <LoadingState label="Loading trace" /> : null}
      {traceQuery.error ? (
        <ApiErrorState title="Trace unavailable" error={traceQuery.error} onRetry={() => void traceQuery.refetch()} />
      ) : null}
      {traceQuery.data ? (
        <div className="trace-content">
          <p className="workspace-meta">source_id: {traceQuery.data.source_id}</p>
          <h3>{traceQuery.data.title || sourceId}</h3>
          {traceQuery.data.summary ? <p>{traceQuery.data.summary}</p> : null}
          <div className="trace-section">
            <h4>Artifact refs</h4>
            {traceQuery.data.artifact_refs?.length ? (
              <ul>
                {traceQuery.data.artifact_refs.map((ref) => (
                  <li key={ref}>{ref}</li>
                ))}
              </ul>
            ) : (
              <p className="workspace-meta">No artifact refs returned.</p>
            )}
          </div>
          <div className="trace-section">
            <h4>Provenance</h4>
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
              <p className="workspace-meta">Trace route returned no provenance rows.</p>
            )}
          </div>
        </div>
      ) : null}
    </aside>
  );
}
