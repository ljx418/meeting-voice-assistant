import type { AnswerEvidence } from '../types/api';
import { StateBlock } from './StateBlock';

export function EvidenceList({
  evidence,
  onTrace,
  onNavigateEvidence,
  preciseNavigationEnabled = false
}: {
  evidence: AnswerEvidence[];
  onTrace: (sourceId: string) => void;
  onNavigateEvidence?: (evidence: AnswerEvidence) => void;
  preciseNavigationEnabled?: boolean;
}) {
  if (evidence.length === 0) {
    return <StateBlock title="No evidence available" tone="warning">The answer returned without source-level evidence.</StateBlock>;
  }

  return (
    <div className="evidence-list" aria-label="Answer evidence">
      {evidence.map((item) => {
        const canOpenTrace = Boolean(item.sourceId && item.traceAvailable);
        const canOpenPreciseEvidence = Boolean(
          preciseNavigationEnabled && onNavigateEvidence && item.sourceId && item.unitId && item.evidenceId
        );
        const label = item.sourceTitle || item.sourceId || item.sourceRef || 'Artifact evidence';
        const disabledTitle = item.sourceRef
          ? 'Source reference is not traceable'
          : item.artifactRefs?.length
            ? 'Evidence metadata has no registry source_id'
            : 'Trace unavailable';
        const onClick = () => {
          if (canOpenPreciseEvidence) {
            onNavigateEvidence?.(item);
            return;
          }
          if (item.sourceId) onTrace(item.sourceId);
        };
        return (
          <button
            className="evidence-chip"
            key={item.evidenceKey}
            data-testid={canOpenPreciseEvidence ? 'jumpable-evidence-citation' : undefined}
            type="button"
            disabled={!canOpenTrace && !canOpenPreciseEvidence}
            onClick={onClick}
            title={canOpenPreciseEvidence ? 'Open evidence span' : !canOpenTrace ? disabledTitle : 'Open trace'}
          >
            <span>{label}</span>
            {item.snippet ? <small>{item.snippet}</small> : null}
            {item.unitId ? <small>unit_id: {item.unitId}</small> : null}
            {item.evidenceId ? <small>evidence_id: {item.evidenceId}</small> : null}
            {canOpenPreciseEvidence ? <small>precise evidence navigation available</small> : null}
            {item.locator?.pageNo ? <small>page {item.locator.pageNo}</small> : null}
            {!item.sourceId && item.sourceRef ? <small>source_ref: {item.sourceRef}</small> : null}
            {!item.sourceId && item.artifactRefs?.length ? <small>{item.artifactRefs.length} artifact refs</small> : null}
            {!item.traceAvailable && item.traceUnavailableReason ? <small>{item.traceUnavailableReason}</small> : null}
          </button>
        );
      })}
    </div>
  );
}
