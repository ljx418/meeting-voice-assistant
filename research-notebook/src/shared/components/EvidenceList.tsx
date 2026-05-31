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
    return <StateBlock title="暂无可用证据" tone="warning">本次回答没有返回来源级证据。</StateBlock>;
  }

  return (
    <div className="evidence-list" aria-label="回答证据">
      {evidence.map((item) => {
        const canOpenTrace = Boolean(item.sourceId && item.traceAvailable);
        const canOpenPreciseEvidence = Boolean(
          preciseNavigationEnabled && onNavigateEvidence && item.sourceId && item.unitId && item.evidenceId
        );
        const label = item.sourceTitle || item.sourceRef || '来源片段';
        const disabledTitle = item.sourceRef
          ? '来源引用不可溯源'
          : item.artifactRefs?.length
            ? '证据元数据缺少注册来源 ID'
            : '溯源不可用';
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
            title={canOpenPreciseEvidence ? '定位到原文片段' : !canOpenTrace ? disabledTitle : '查看来源溯源'}
          >
            <span>{label}</span>
            {item.snippet ? <small>{item.snippet}</small> : null}
            {canOpenPreciseEvidence ? <small>可定位到原文片段</small> : null}
            {item.locator?.pageNo ? <small>页码 {item.locator.pageNo}</small> : null}
            {!item.sourceId && item.sourceRef ? <small>仅有来源名称，暂不能定位</small> : null}
            {!item.sourceId && item.artifactRefs?.length ? <small>{item.artifactRefs.length} 条来源元数据，暂不能定位</small> : null}
            {!item.traceAvailable && item.traceUnavailableReason ? <small>{item.traceUnavailableReason}</small> : null}
          </button>
        );
      })}
    </div>
  );
}
