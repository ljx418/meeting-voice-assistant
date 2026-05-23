import { ReactNode, useMemo, useState } from 'react';
import { isNormalizedApiError } from '../api/dataServiceClient';
import {
  isEvidenceSpanNavigationSupported,
  isSourceLevelPreviewSupported,
  isUnitLevelNavigationSupported,
  useCapabilitiesQuery,
  useSourceEvidenceSpanQuery,
  useSourcePreviewQuery,
  useSourceQuery,
  useSourceUnitQuery,
  useSourceUnitsQuery
} from '../api/workspaceM2Queries';
import { ApiErrorState } from './ApiErrorState';
import { LoadingState, StateBlock, UnsupportedFeatureState } from './StateBlock';

const MAX_RENDERED_PREVIEW_CHARS = 20_000;

type InitialEvidenceNavigation = {
  unitId?: string;
  evidenceId?: string;
  evidenceKey?: string;
};

type HighlightResult =
  | { state: 'none'; content: string | ReactNode }
  | { state: 'ready'; content: ReactNode }
  | { state: 'unavailable'; reason: string; content: string };

function highlightedUnitText(text: string, evidence: ReturnType<typeof useSourceEvidenceSpanQuery>['data']): HighlightResult {
  if (!evidence) return { state: 'none', content: text };
  if (
    evidence.start_offset === undefined ||
    evidence.end_offset === undefined ||
    evidence.offset_basis === undefined ||
    evidence.offset_range === undefined ||
    evidence.text_basis === undefined ||
    evidence.unit_id === undefined
  ) {
    return { state: 'unavailable', reason: 'EvidenceSpan is missing offset basis, offset range, text basis, or unit_id.', content: text };
  }
  if (evidence.offset_basis !== 'normalized_text' || evidence.offset_range !== 'half_open' || evidence.text_basis !== 'document_unit_text') {
    return { state: 'unavailable', reason: 'EvidenceSpan offset contract is not supported by the frontend highlighter.', content: text };
  }
  if (evidence.start_offset < 0 || evidence.end_offset <= evidence.start_offset || evidence.end_offset > text.length) {
    return { state: 'unavailable', reason: 'EvidenceSpan offsets are outside the rendered unit text.', content: text };
  }

  return {
    state: 'ready',
    content: (
      <>
        {text.slice(0, evidence.start_offset)}
        <mark className="evidence-highlight" data-testid="evidence-highlight">
          {text.slice(evidence.start_offset, evidence.end_offset)}
        </mark>
        {text.slice(evidence.end_offset)}
      </>
    )
  };
}

export function SourcePreviewDrawer({
  workspaceId,
  sourceId,
  sourceTitle,
  sourceType,
  initialEvidence,
  onClose
}: {
  workspaceId: string;
  sourceId: string | null;
  sourceTitle?: string;
  sourceType?: string;
  initialEvidence?: InitialEvidenceNavigation | null;
  onClose: () => void;
}) {
  const [selectedUnit, setSelectedUnit] = useState<{ sourceId: string; unitId: string; navigationKey: string } | null>(null);
  const capabilitiesQuery = useCapabilitiesQuery(workspaceId);
  const sourceQuery = useSourceQuery(workspaceId, sourceId);
  const effectiveSourceType = sourceType ?? sourceQuery.data?.source_type;
  const effectiveSourceTitle = sourceTitle ?? sourceQuery.data?.title;
  const evidenceNavigationSupported = isEvidenceSpanNavigationSupported(capabilitiesQuery.data);
  const previewSupported = isSourceLevelPreviewSupported(capabilitiesQuery.data, effectiveSourceType);
  const unitNavigationSupported = isUnitLevelNavigationSupported(capabilitiesQuery.data, effectiveSourceType);
  const navigationKey = `${initialEvidence?.unitId ?? ''}:${initialEvidence?.evidenceId ?? ''}:${initialEvidence?.evidenceKey ?? ''}`;
  const selectedUnitId =
    unitNavigationSupported && sourceId
      ? selectedUnit?.sourceId === sourceId && selectedUnit.navigationKey === navigationKey
        ? selectedUnit.unitId
        : (initialEvidence?.unitId ?? null)
      : null;
  const previewQuery = useSourcePreviewQuery(workspaceId, sourceId, Boolean(capabilitiesQuery.data && previewSupported));
  const unitsQuery = useSourceUnitsQuery(workspaceId, sourceId, Boolean(capabilitiesQuery.data && unitNavigationSupported));
  const unitDetailQuery = useSourceUnitQuery(workspaceId, sourceId, selectedUnitId, Boolean(unitNavigationSupported));
  const requestedEvidenceId = initialEvidence?.unitId === selectedUnitId ? (initialEvidence.evidenceId ?? null) : null;
  const evidenceSpanQuery = useSourceEvidenceSpanQuery(
    workspaceId,
    sourceId,
    selectedUnitId,
    requestedEvidenceId,
    Boolean(evidenceNavigationSupported)
  );

  const capabilityUnsupported =
    capabilitiesQuery.data && !previewSupported
      ? sourceType
        ? `data_service does not advertise source-level preview for source type "${effectiveSourceType}".`
        : 'data_service does not advertise any source-level preview capability for this workspace.'
      : null;
  const preview = previewQuery.data?.preview;
  const contentType = preview?.content_type ?? 'unknown';
  const rawPreviewText = preview?.text_preview ?? '';
  const renderedPreviewText =
    rawPreviewText.length > MAX_RENDERED_PREVIEW_CHARS ? rawPreviewText.slice(0, MAX_RENDERED_PREVIEW_CHARS) : rawPreviewText;
  const contentSafetyNotice =
    contentType === 'text/html' || contentType === 'text/markdown'
      ? `${contentType} returned by backend; rendered as escaped text.`
      : contentType === 'unknown'
        ? 'Unknown content_type; rendered as escaped text.'
        : null;
  const unitMetadataAllowed = Boolean(capabilitiesQuery.data?.capabilities.document_units);
  const previewUnits = unitMetadataAllowed ? (preview?.units ?? []) : [];
  const unitPages = useMemo(() => unitsQuery.data?.pages ?? [], [unitsQuery.data?.pages]);
  const routeUnits = useMemo(() => {
    const seen = new Set<string>();
    return unitPages.flatMap((page) =>
      page.items.filter((unit) => {
        if (seen.has(unit.unit_id)) return false;
        seen.add(unit.unit_id);
        return true;
      })
    );
  }, [unitPages]);
  const unitListUnsupportedReason = unitPages.find((page) => page.unsupported_reason)?.unsupported_reason;
  const selectedUnitDetail = unitDetailQuery.data;
  const selectedContentType = selectedUnitDetail?.content_type ?? 'unknown';
  const selectedPreviewText = selectedUnitDetail?.text_preview ?? '';
  const renderedSelectedPreviewText =
    selectedPreviewText.length > MAX_RENDERED_PREVIEW_CHARS
      ? selectedPreviewText.slice(0, MAX_RENDERED_PREVIEW_CHARS)
      : selectedPreviewText;
  const highlightResult = highlightedUnitText(renderedSelectedPreviewText, evidenceSpanQuery.data);
  const highlightDisabledByTruncation =
    Boolean(evidenceSpanQuery.data && selectedUnitDetail?.preview_truncated && evidenceSpanQuery.data.end_offset !== undefined) &&
    evidenceSpanQuery.data!.end_offset! > renderedSelectedPreviewText.length;

  if (!sourceId) return null;

  return (
    <aside className="right-drawer" aria-label="Source preview drawer" data-testid="source-preview-drawer">
      <div className="drawer-header">
        <div>
          <div className="eyebrow">V1.1-D Source Preview / Evidence Navigation</div>
          <h2>Source Preview</h2>
        </div>
        <button className="secondary-button" type="button" onClick={onClose}>
          Close
        </button>
      </div>
      <div className="drawer-body page-grid">
        {capabilitiesQuery.isLoading ? <LoadingState label="Checking source preview capability" /> : null}
        {capabilitiesQuery.error && isNormalizedApiError(capabilitiesQuery.error) && capabilitiesQuery.error.code === 'capability_missing' ? (
          <UnsupportedFeatureState title="Source preview contract missing">
            data_service did not expose the capability manifest for this workspace. Source Preview remains disabled and is not claimed ready.
          </UnsupportedFeatureState>
        ) : null}
        {capabilitiesQuery.error && (!isNormalizedApiError(capabilitiesQuery.error) || capabilitiesQuery.error.code !== 'capability_missing') ? (
          <ApiErrorState title="Source preview capability unavailable" error={capabilitiesQuery.error} onRetry={() => void capabilitiesQuery.refetch()} />
        ) : null}
        {capabilityUnsupported ? (
          <UnsupportedFeatureState title="Source preview unsupported">{capabilityUnsupported}</UnsupportedFeatureState>
        ) : null}
        {previewQuery.isLoading ? <LoadingState label="Loading source preview" /> : null}
        {previewQuery.error ? (
          <ApiErrorState title="Source preview unavailable" error={previewQuery.error} onRetry={() => void previewQuery.refetch()} />
        ) : null}
        {preview ? (
          <section className="panel">
            <div className="panel-header">
              <h3>{preview.title ?? effectiveSourceTitle ?? sourceId}</h3>
            </div>
            <div className="panel-body page-grid">
              <dl className="source-meta-grid">
                <div>
                  <dt>source_id</dt>
                  <dd>{preview.source_id}</dd>
                </div>
                <div>
                  <dt>type</dt>
                  <dd>{preview.source_type ?? effectiveSourceType ?? 'service-defined'}</dd>
                </div>
                <div>
                  <dt>content_type</dt>
                  <dd>{contentType}</dd>
                </div>
                <div>
                  <dt>artifact refs</dt>
                  <dd>{preview.artifact_refs?.length ? `${preview.artifact_refs.length} present` : 'none'}</dd>
                </div>
              </dl>
              {preview.preview_available ? null : (
                <UnsupportedFeatureState title="Preview unavailable">
                  {preview.unsupported_reason ?? 'data_service recognizes this source but did not return a preview.'}
                </UnsupportedFeatureState>
              )}
              {preview.artifact_refs?.length ? (
                <StateBlock title="Artifact refs are metadata only">{preview.artifact_refs.join(', ')}</StateBlock>
              ) : null}
              {contentSafetyNotice ? <StateBlock title="Content safety">{contentSafetyNotice}</StateBlock> : null}
              {rawPreviewText.length > MAX_RENDERED_PREVIEW_CHARS || preview.preview_truncated ? (
                <StateBlock title="Preview truncated">
                  Showing the first {renderedPreviewText.length.toLocaleString()} characters. Backend size:{' '}
                  {preview.preview_size_bytes?.toLocaleString() ?? 'unknown'} bytes; max:{' '}
                  {preview.max_preview_size_bytes?.toLocaleString() ?? 'unknown'} bytes.
                </StateBlock>
              ) : null}
              {renderedPreviewText ? (
                <pre className="text-preview" aria-label="Source preview text">
                  {renderedPreviewText}
                </pre>
              ) : preview.preview_available ? (
                <StateBlock title="No text preview returned">data_service returned preview_available=true without text_preview.</StateBlock>
              ) : null}
            </div>
          </section>
        ) : null}
        <section className="panel" aria-labelledby="document-units-title">
          <div className="panel-header">
            <h3 id="document-units-title">Document Units</h3>
          </div>
          <div className="panel-body page-grid">
            {!capabilitiesQuery.data?.capabilities.document_units ? (
              <UnsupportedFeatureState title="Unit navigation unsupported">
                data_service does not advertise document_units for this workspace. Unit-level navigation remains NOT_READY.
              </UnsupportedFeatureState>
            ) : null}
            {capabilitiesQuery.data?.capabilities.document_units && !unitNavigationSupported ? (
              <UnsupportedFeatureState title="Units metadata returned but navigation disabled">
                DocumentUnit metadata can be displayed, but unit navigation is disabled until the manifest advertises unit-level navigation for
                this source type.
              </UnsupportedFeatureState>
            ) : null}
            {preview?.units?.length && !unitMetadataAllowed ? (
              <StateBlock title="Document units ignored">
                Preview response included units, but capability manifest does not advertise document_units=true.
              </StateBlock>
            ) : null}
            {unitNavigationSupported && unitsQuery.isLoading ? <LoadingState label="Loading document units" /> : null}
            {unitNavigationSupported && unitsQuery.error ? (
              <ApiErrorState title="Document units unavailable" error={unitsQuery.error} onRetry={() => void unitsQuery.refetch()} />
            ) : null}
            {unitListUnsupportedReason ? (
              <UnsupportedFeatureState title="Document units unavailable">{unitListUnsupportedReason}</UnsupportedFeatureState>
            ) : null}
            {unitNavigationSupported && !unitsQuery.isLoading && !unitsQuery.error && routeUnits.length === 0 && !unitListUnsupportedReason ? (
              <StateBlock title="No DocumentUnits returned">data_service returned an empty DocumentUnit list for this source.</StateBlock>
            ) : null}
            {unitNavigationSupported && routeUnits.length > 0 ? (
              <div className="source-list" aria-label="Document units outline" data-testid="document-units-outline">
                {routeUnits.map((unit) => (
                  <button
                    className="source-card"
                    type="button"
                    key={unit.unit_id}
                    aria-pressed={selectedUnitId === unit.unit_id}
                    onClick={() => setSelectedUnit({ sourceId, unitId: unit.unit_id, navigationKey })}
                  >
                    <span>
                      <strong>{unit.title ?? unit.unit_id}</strong>
                      <span className="workspace-meta">
                        {unit.unit_type} / order {unit.order_index ?? 'unknown'} / {unit.unit_id}
                      </span>
                    </span>
                  </button>
                ))}
              </div>
            ) : null}
            {unitNavigationSupported && unitsQuery.hasNextPage ? (
              <button
                className="secondary-button"
                type="button"
                disabled={unitsQuery.isFetchingNextPage}
                onClick={() => void unitsQuery.fetchNextPage()}
              >
                {unitsQuery.isFetchingNextPage ? 'Loading more units...' : 'Load more units'}
              </button>
            ) : null}
            {unitNavigationSupported && unitsQuery.isFetchNextPageError ? (
              <ApiErrorState title="Load more units failed" error={unitsQuery.error} onRetry={() => void unitsQuery.fetchNextPage()} />
            ) : null}
            {!unitNavigationSupported && unitMetadataAllowed && previewUnits.length > 0 ? (
              <div className="source-list" aria-label="Document units metadata">
                {previewUnits.map((unit) => (
                  <article className="source-card" key={unit.unit_id}>
                    <div>
                      <h4>{unit.title ?? unit.unit_id}</h4>
                      <dl className="source-meta-grid">
                        <div>
                          <dt>unit_id</dt>
                          <dd>{unit.unit_id}</dd>
                        </div>
                        <div>
                          <dt>unit_type</dt>
                          <dd>{unit.unit_type}</dd>
                        </div>
                        <div>
                          <dt>order</dt>
                          <dd>{unit.order_index ?? 'unknown'}</dd>
                        </div>
                        <div>
                          <dt>locator</dt>
                          <dd>
                            {[
                              unit.page_no !== undefined ? `page ${unit.page_no}` : undefined,
                              unit.slide_no !== undefined ? `slide ${unit.slide_no}` : undefined,
                              unit.timestamp_start_ms !== undefined ? `${unit.timestamp_start_ms}ms` : undefined,
                              unit.json_path
                            ]
                              .filter(Boolean)
                              .join(' / ') || 'none'}
                          </dd>
                        </div>
                      </dl>
                      {unit.artifact_ref ? <p className="workspace-meta">artifact_ref metadata: {unit.artifact_ref}</p> : null}
                      {unit.text_preview ? <p>{unit.text_preview}</p> : null}
                    </div>
                  </article>
                ))}
              </div>
            ) : null}
            {unitNavigationSupported && selectedUnitId ? (
              <section className="panel" aria-label="Selected document unit" data-testid="selected-document-unit">
                <div className="panel-header">
                  <h4>{selectedUnitDetail?.title ?? selectedUnitId}</h4>
                </div>
                <div className="panel-body page-grid">
                  {unitDetailQuery.isLoading ? <LoadingState label="Loading selected unit" /> : null}
                  {unitDetailQuery.error ? (
                    <ApiErrorState title="Document unit unavailable" error={unitDetailQuery.error} onRetry={() => void unitDetailQuery.refetch()} />
                  ) : null}
                  {selectedUnitDetail ? (
                    <>
                      <dl className="source-meta-grid">
                        <div>
                          <dt>unit_id</dt>
                          <dd>{selectedUnitDetail.unit_id}</dd>
                        </div>
                        <div>
                          <dt>content_type</dt>
                          <dd>{selectedContentType}</dd>
                        </div>
                        <div>
                          <dt>artifact_ref</dt>
                          <dd>{selectedUnitDetail.artifact_ref ?? 'none'}</dd>
                        </div>
                        {requestedEvidenceId ? (
                          <div>
                            <dt>evidence_id</dt>
                            <dd>{requestedEvidenceId}</dd>
                          </div>
                        ) : null}
                      </dl>
                      {selectedContentType === 'text/html' || selectedContentType === 'text/markdown' ? (
                        <StateBlock title="Content safety">{selectedContentType} returned by backend; rendered as escaped text.</StateBlock>
                      ) : null}
                      {requestedEvidenceId && evidenceNavigationSupported && evidenceSpanQuery.isLoading ? (
                        <LoadingState label="Loading EvidenceSpan" />
                      ) : null}
                      {requestedEvidenceId && !evidenceNavigationSupported ? (
                        <UnsupportedFeatureState title="EvidenceSpan navigation unsupported">
                          data_service capability manifest does not advertise precise EvidenceSpan navigation for this workspace.
                        </UnsupportedFeatureState>
                      ) : null}
                      {requestedEvidenceId && evidenceSpanQuery.error ? (
                        <ApiErrorState
                          title="EvidenceSpan unavailable"
                          error={evidenceSpanQuery.error}
                          onRetry={() => void evidenceSpanQuery.refetch()}
                        />
                      ) : null}
                      {highlightDisabledByTruncation ? (
                        <StateBlock title="Highlight unavailable" tone="warning">
                          The selected unit text is truncated before the EvidenceSpan end offset. The frontend will not fabricate a highlight.
                        </StateBlock>
                      ) : null}
                      {highlightResult.state === 'unavailable' && !highlightDisabledByTruncation ? (
                        <StateBlock title="Highlight unavailable" tone="warning">{highlightResult.reason}</StateBlock>
                      ) : null}
                      {selectedUnitDetail.preview_truncated || selectedPreviewText.length > MAX_RENDERED_PREVIEW_CHARS ? (
                        <StateBlock title="Unit preview truncated">
                          Showing the first {renderedSelectedPreviewText.length.toLocaleString()} characters. Backend size:{' '}
                          {selectedUnitDetail.preview_size_bytes?.toLocaleString() ?? 'unknown'} bytes; max:{' '}
                          {selectedUnitDetail.max_preview_size_bytes?.toLocaleString() ?? 'unknown'} bytes.
                        </StateBlock>
                      ) : null}
                      {renderedSelectedPreviewText ? (
                        <pre className="text-preview" aria-label="Selected unit preview text">
                          {highlightDisabledByTruncation ? renderedSelectedPreviewText : highlightResult.content}
                        </pre>
                      ) : (
                        <StateBlock title="No unit text preview returned">data_service returned unit metadata without text_preview.</StateBlock>
                      )}
                    </>
                  ) : null}
                </div>
              </section>
            ) : null}
          </div>
        </section>
      </div>
    </aside>
  );
}
