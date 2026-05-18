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
        return (
          <button
            className="evidence-chip"
            key={item.evidenceKey}
            type="button"
            disabled={!canOpenTrace}
            onClick={() => item.sourceId && onTrace(item.sourceId)}
            title={!item.sourceId ? 'Evidence metadata has no source_id' : item.traceAvailable ? 'Open trace' : 'Trace unavailable'}
          >
            <span>{item.sourceTitle || item.sourceId || 'Artifact evidence'}</span>
            {item.snippet ? <small>{item.snippet}</small> : null}
            {!item.sourceId && item.artifactRefs?.length ? <small>{item.artifactRefs.length} artifact refs</small> : null}
          </button>
        );
      })}
    </div>
  );
}
