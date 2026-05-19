import type { AnswerEvidence } from '../types/api';
import { StateBlock } from './StateBlock';

export function EvidenceList({ evidence, onTrace }: { evidence: AnswerEvidence[]; onTrace: (sourceId: string) => void }) {
  if (evidence.length === 0) {
    return <StateBlock title="No evidence available" tone="warning">The answer returned without source-level evidence.</StateBlock>;
  }

  return (
    <div className="evidence-list" aria-label="Answer evidence">
      {evidence.map((item) => {
        const canOpenTrace = Boolean(item.sourceId && item.traceAvailable);
        const label = item.sourceTitle || item.sourceId || item.sourceRef || 'Artifact evidence';
        const disabledTitle = item.sourceRef
          ? 'Source reference is not traceable'
          : item.artifactRefs?.length
            ? 'Evidence metadata has no registry source_id'
            : 'Trace unavailable';
        return (
          <button
            className="evidence-chip"
            key={item.evidenceKey}
            type="button"
            disabled={!canOpenTrace}
            onClick={() => item.sourceId && onTrace(item.sourceId)}
            title={!canOpenTrace ? disabledTitle : 'Open trace'}
          >
            <span>{label}</span>
            {item.snippet ? <small>{item.snippet}</small> : null}
            {!item.sourceId && item.sourceRef ? <small>source_ref: {item.sourceRef}</small> : null}
            {!item.sourceId && item.artifactRefs?.length ? <small>{item.artifactRefs.length} artifact refs</small> : null}
            {!item.traceAvailable && item.traceUnavailableReason ? <small>{item.traceUnavailableReason}</small> : null}
          </button>
        );
      })}
    </div>
  );
}
