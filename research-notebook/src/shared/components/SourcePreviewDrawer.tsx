import { KeyboardEvent, ReactNode, useEffect, useMemo, useRef, useState } from 'react';
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
const FOCUSABLE_SELECTOR =
  'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

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
    return { state: 'unavailable', reason: '证据片段缺少偏移基准、偏移范围、文本基准或单元 ID。', content: text };
  }
  if (evidence.offset_basis !== 'normalized_text' || evidence.offset_range !== 'half_open' || evidence.text_basis !== 'document_unit_text') {
    return { state: 'unavailable', reason: '当前前端高亮器不支持该证据片段的偏移合同。', content: text };
  }
  if (evidence.start_offset < 0 || evidence.end_offset <= evidence.start_offset || evidence.end_offset > text.length) {
    return { state: 'unavailable', reason: '证据片段偏移超出了当前渲染的单元文本。', content: text };
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
  const drawerRef = useRef<HTMLElement | null>(null);
  const closeButtonRef = useRef<globalThis.HTMLButtonElement | null>(null);
  const previousActiveElementRef = useRef<globalThis.Element | null>(null);
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
        ? `数据服务未声明来源类型“${effectiveSourceType}”支持来源级预览。`
        : '数据服务未声明该工作区支持来源级预览能力。'
      : null;
  const preview = previewQuery.data?.preview;
  const contentType = preview?.content_type ?? 'unknown';
  const rawPreviewText = preview?.text_preview ?? '';
  const renderedPreviewText =
    rawPreviewText.length > MAX_RENDERED_PREVIEW_CHARS ? rawPreviewText.slice(0, MAX_RENDERED_PREVIEW_CHARS) : rawPreviewText;
  const contentSafetyNotice =
    contentType === 'text/html' || contentType === 'text/markdown'
      ? `后端返回 ${contentType}，已按转义文本渲染。`
      : contentType === 'unknown'
        ? '内容类型未知，已按转义文本渲染。'
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

  useEffect(() => {
    if (!sourceId) return undefined;
    previousActiveElementRef.current = document.activeElement;
    closeButtonRef.current?.focus();
    return () => {
      const previous = previousActiveElementRef.current;
      if (previous instanceof HTMLElement) previous.focus();
    };
  }, [sourceId]);

  const onDialogKeyDown = (event: KeyboardEvent<HTMLElement>) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      onClose();
      return;
    }
    if (event.key !== 'Tab') return;
    const focusable = Array.from(drawerRef.current?.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR) ?? []).filter(
      (element) => element.offsetParent !== null
    );
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  };

  if (!sourceId) return null;

  return (
    <>
      <button className="drawer-backdrop" type="button" aria-label="关闭来源预览抽屉" onClick={onClose} />
      <aside
        ref={drawerRef}
        className="right-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="source-preview-drawer-title"
        data-testid="source-preview-drawer"
        onKeyDown={onDialogKeyDown}
      >
      <div className="drawer-header">
        <div>
          <div className="eyebrow">来源预览与证据定位</div>
          <h2 id="source-preview-drawer-title">来源预览</h2>
        </div>
        <button ref={closeButtonRef} className="secondary-button" type="button" onClick={onClose}>
          关闭
        </button>
      </div>
      <div className="drawer-body page-grid">
        {capabilitiesQuery.isLoading ? <LoadingState label="正在检查来源预览能力" /> : null}
        {capabilitiesQuery.error && isNormalizedApiError(capabilitiesQuery.error) && capabilitiesQuery.error.code === 'capability_missing' ? (
          <UnsupportedFeatureState title="缺少来源预览合同">
            数据服务没有暴露该工作区的能力清单，来源预览保持禁用状态。
          </UnsupportedFeatureState>
        ) : null}
        {capabilitiesQuery.error && (!isNormalizedApiError(capabilitiesQuery.error) || capabilitiesQuery.error.code !== 'capability_missing') ? (
          <ApiErrorState title="来源预览能力不可用" error={capabilitiesQuery.error} onRetry={() => void capabilitiesQuery.refetch()} />
        ) : null}
        {capabilityUnsupported ? (
          <UnsupportedFeatureState title="暂不支持来源预览">{capabilityUnsupported}</UnsupportedFeatureState>
        ) : null}
        {previewQuery.isLoading ? <LoadingState label="正在加载来源预览" /> : null}
        {previewQuery.error ? (
          <ApiErrorState title="来源预览不可用" error={previewQuery.error} onRetry={() => void previewQuery.refetch()} />
        ) : null}
        {preview ? (
          <section className="panel">
            <div className="panel-header">
              <h3>{preview.title ?? effectiveSourceTitle ?? sourceId}</h3>
            </div>
            <div className="panel-body page-grid">
              <dl className="source-meta-grid">
                <div>
                  <dt>来源 ID</dt>
                  <dd>{preview.source_id}</dd>
                </div>
                <div>
                  <dt>类型</dt>
                  <dd>{preview.source_type ?? effectiveSourceType ?? '服务定义'}</dd>
                </div>
                <div>
                  <dt>内容类型</dt>
                  <dd>{contentType}</dd>
                </div>
                <div>
                  <dt>工件引用</dt>
                  <dd>{preview.artifact_refs?.length ? `${preview.artifact_refs.length} 个` : '无'}</dd>
                </div>
              </dl>
              {preview.preview_available ? null : (
                <UnsupportedFeatureState title="预览不可用">
                  {preview.unsupported_reason ?? '数据服务可以识别该来源，但没有返回预览内容。'}
                </UnsupportedFeatureState>
              )}
              {preview.artifact_refs?.length ? (
                <StateBlock title="工件引用仅作为元数据展示">{preview.artifact_refs.join(', ')}</StateBlock>
              ) : null}
              {contentSafetyNotice ? <StateBlock title="内容安全">{contentSafetyNotice}</StateBlock> : null}
              {rawPreviewText.length > MAX_RENDERED_PREVIEW_CHARS || preview.preview_truncated ? (
                <StateBlock title="预览已截断">
                  当前显示前 {renderedPreviewText.length.toLocaleString()} 个字符。后端大小：{' '}
                  {preview.preview_size_bytes?.toLocaleString() ?? '未知'} 字节；上限：{' '}
                  {preview.max_preview_size_bytes?.toLocaleString() ?? '未知'} 字节。
                </StateBlock>
              ) : null}
              {renderedPreviewText ? (
                <pre className="text-preview" aria-label="来源预览文本">
                  {renderedPreviewText}
                </pre>
              ) : preview.preview_available ? (
                <StateBlock title="未返回文本预览">数据服务声明预览可用，但没有返回 text_preview。</StateBlock>
              ) : null}
            </div>
          </section>
        ) : null}
        <section className="panel" aria-labelledby="document-units-title">
          <div className="panel-header">
            <h3 id="document-units-title">文档单元</h3>
          </div>
          <div className="panel-body page-grid">
            {!capabilitiesQuery.data?.capabilities.document_units ? (
              <UnsupportedFeatureState title="暂不支持单元导航">
                数据服务未声明该工作区支持文档单元能力。
              </UnsupportedFeatureState>
            ) : null}
            {capabilitiesQuery.data?.capabilities.document_units && !unitNavigationSupported ? (
              <UnsupportedFeatureState title="已返回单元元数据，但导航未启用">
                可以展示文档单元元数据；只有能力清单声明该来源类型支持单元导航后，才会启用导航。
              </UnsupportedFeatureState>
            ) : null}
            {preview?.units?.length && !unitMetadataAllowed ? (
              <StateBlock title="已忽略文档单元">
                预览响应包含 units，但能力清单没有声明 document_units=true。
              </StateBlock>
            ) : null}
            {unitNavigationSupported && unitsQuery.isLoading ? <LoadingState label="正在加载文档单元" /> : null}
            {unitNavigationSupported && unitsQuery.error ? (
              <ApiErrorState title="文档单元不可用" error={unitsQuery.error} onRetry={() => void unitsQuery.refetch()} />
            ) : null}
            {unitListUnsupportedReason ? (
              <UnsupportedFeatureState title="文档单元不可用">{unitListUnsupportedReason}</UnsupportedFeatureState>
            ) : null}
            {unitNavigationSupported && !unitsQuery.isLoading && !unitsQuery.error && routeUnits.length === 0 && !unitListUnsupportedReason ? (
              <StateBlock title="未返回文档单元">数据服务为该来源返回了空的文档单元列表。</StateBlock>
            ) : null}
            {unitNavigationSupported && routeUnits.length > 0 ? (
              <div className="source-list" aria-label="文档单元大纲" data-testid="document-units-outline">
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
                        {unit.unit_type} / 顺序 {unit.order_index ?? '未知'} / {unit.unit_id}
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
                {unitsQuery.isFetchingNextPage ? '正在加载更多单元...' : '加载更多单元'}
              </button>
            ) : null}
            {unitNavigationSupported && unitsQuery.isFetchNextPageError ? (
              <ApiErrorState title="加载更多单元失败" error={unitsQuery.error} onRetry={() => void unitsQuery.fetchNextPage()} />
            ) : null}
            {!unitNavigationSupported && unitMetadataAllowed && previewUnits.length > 0 ? (
              <div className="source-list" aria-label="文档单元元数据">
                {previewUnits.map((unit) => (
                  <article className="source-card" key={unit.unit_id}>
                    <div>
                      <h4>{unit.title ?? unit.unit_id}</h4>
                      <dl className="source-meta-grid">
                        <div>
                          <dt>单元 ID</dt>
                          <dd>{unit.unit_id}</dd>
                        </div>
                        <div>
                          <dt>单元类型</dt>
                          <dd>{unit.unit_type}</dd>
                        </div>
                        <div>
                          <dt>顺序</dt>
                          <dd>{unit.order_index ?? '未知'}</dd>
                        </div>
                        <div>
                          <dt>定位信息</dt>
                          <dd>
                            {[
                              unit.page_no !== undefined ? `页码 ${unit.page_no}` : undefined,
                              unit.slide_no !== undefined ? `幻灯片 ${unit.slide_no}` : undefined,
                              unit.timestamp_start_ms !== undefined ? `${unit.timestamp_start_ms}ms` : undefined,
                              unit.json_path
                            ]
                              .filter(Boolean)
                              .join(' / ') || '无'}
                          </dd>
                        </div>
                      </dl>
                      {unit.artifact_ref ? <p className="workspace-meta">工件引用元数据：{unit.artifact_ref}</p> : null}
                      {unit.text_preview ? <p>{unit.text_preview}</p> : null}
                    </div>
                  </article>
                ))}
              </div>
            ) : null}
            {unitNavigationSupported && selectedUnitId ? (
              <section className="panel" aria-label="已选文档单元" data-testid="selected-document-unit">
                <div className="panel-header">
                  <h4>{selectedUnitDetail?.title ?? selectedUnitId}</h4>
                </div>
                <div className="panel-body page-grid">
                  {unitDetailQuery.isLoading ? <LoadingState label="正在加载已选单元" /> : null}
                  {unitDetailQuery.error ? (
                    <ApiErrorState title="文档单元不可用" error={unitDetailQuery.error} onRetry={() => void unitDetailQuery.refetch()} />
                  ) : null}
                  {selectedUnitDetail ? (
                    <>
                      <dl className="source-meta-grid">
                        <div>
                          <dt>单元 ID</dt>
                          <dd>{selectedUnitDetail.unit_id}</dd>
                        </div>
                        <div>
                          <dt>内容类型</dt>
                          <dd>{selectedContentType}</dd>
                        </div>
                        <div>
                          <dt>工件引用</dt>
                          <dd>{selectedUnitDetail.artifact_ref ?? '无'}</dd>
                        </div>
                        {requestedEvidenceId ? (
                          <div>
                            <dt>证据片段 ID</dt>
                            <dd>{requestedEvidenceId}</dd>
                          </div>
                        ) : null}
                      </dl>
                      {selectedContentType === 'text/html' || selectedContentType === 'text/markdown' ? (
                        <StateBlock title="内容安全">后端返回 {selectedContentType}，已按转义文本渲染。</StateBlock>
                      ) : null}
                      {requestedEvidenceId && evidenceNavigationSupported && evidenceSpanQuery.isLoading ? (
                        <LoadingState label="正在加载证据片段" />
                      ) : null}
                      {requestedEvidenceId && !evidenceNavigationSupported ? (
                        <UnsupportedFeatureState title="暂不支持证据片段导航">
                          数据服务能力清单未声明该工作区支持精确证据片段导航。
                        </UnsupportedFeatureState>
                      ) : null}
                      {requestedEvidenceId && evidenceSpanQuery.error ? (
                        <ApiErrorState
                          title="证据片段不可用"
                          error={evidenceSpanQuery.error}
                          onRetry={() => void evidenceSpanQuery.refetch()}
                        />
                      ) : null}
                      {highlightDisabledByTruncation ? (
                        <StateBlock title="高亮不可用" tone="warning">
                          已选单元文本在证据片段结束偏移前被截断，前端不会伪造高亮。
                        </StateBlock>
                      ) : null}
                      {highlightResult.state === 'unavailable' && !highlightDisabledByTruncation ? (
                        <StateBlock title="高亮不可用" tone="warning">{highlightResult.reason}</StateBlock>
                      ) : null}
                      {selectedUnitDetail.preview_truncated || selectedPreviewText.length > MAX_RENDERED_PREVIEW_CHARS ? (
                        <StateBlock title="单元预览已截断">
                          当前显示前 {renderedSelectedPreviewText.length.toLocaleString()} 个字符。后端大小：{' '}
                          {selectedUnitDetail.preview_size_bytes?.toLocaleString() ?? '未知'} 字节；上限：{' '}
                          {selectedUnitDetail.max_preview_size_bytes?.toLocaleString() ?? '未知'} 字节。
                        </StateBlock>
                      ) : null}
                      {renderedSelectedPreviewText ? (
                        <pre className="text-preview" aria-label="已选单元预览文本">
                          {highlightDisabledByTruncation ? renderedSelectedPreviewText : highlightResult.content}
                        </pre>
                      ) : (
                        <StateBlock title="未返回单元文本预览">数据服务返回了单元元数据，但没有返回 text_preview。</StateBlock>
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
    </>
  );
}
