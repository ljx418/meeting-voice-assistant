import type {
  AnswerEvidence,
  AgentWorkflowDraftRequest,
  AgentWorkflowDraftResponse,
  BuildOperation,
  BuildStartRequest,
  BuildStartResponse,
  CapabilityManifest,
  CreateWorkspaceRequest,
  CreateWorkspaceResponse,
  CreateSourceRequest,
  CreateSourceResponse,
  DocumentUnit,
  DocumentUnitListRequest,
  DocumentUnitListResponse,
  EvidenceNavigationResponse,
  EvidenceSpan,
  FolderCollection,
  FolderFile,
  FolderNode,
  FolderScanRequest,
  FolderScanResponse,
  FolderSummaryWorkflowRunRequest,
  FolderSummaryWorkflowRunResponse,
  GraphCommunitiesResponse,
  GraphCommunity,
  GraphEdge,
  GraphNeighbor,
  GraphNeighborsRequest,
  GraphNeighborsResponse,
  GraphNode,
  NormalizedErrorCode,
  NormalizedErrorEnvelope,
  NotebookGuide,
  QualityFeedbackRequest,
  QualityFeedbackResponse,
  RenameSourceRequest,
  RenameWorkspaceRequest,
  PermissionGrant,
  QueryRequest,
  QueryResponse,
  ResearchReport,
  ResearchRequest,
  CloseSessionResponse,
  CreateSessionRequest,
  CreateSessionResponse,
  SessionBuildStartRequest,
  SessionBuildStartResponse,
  SessionDetail,
  SessionIngestRequest,
  SessionIngestResponse,
  SessionQueryRequest,
  SessionQueryResponse,
  SessionGraphContextResponse,
  SessionState,
  SessionSummary,
  SourcePreviewRequest,
  SourcePreviewResponse,
  SourceBuildState,
  SourceDetail,
  SourceImportState,
  SourceSummary,
  SourceTrace,
  StudioArtifact,
  StudioArtifactRequest,
  SkippedFileReason,
  SummaryArtifact,
  Workflow,
  WorkflowRun,
  WorkflowStep,
  WorkspaceArchiveResult,
  WorkspaceDetail,
  WorkspaceSummary
} from '../types/api';

export class DataServiceError extends Error {
  readonly code: NormalizedErrorCode;
  readonly status?: number;
  readonly retryable: boolean;
  readonly details?: unknown;

  constructor(error: NormalizedErrorEnvelope) {
    super(error.message);
    this.name = 'DataServiceError';
    this.code = error.code;
    this.status = error.status;
    this.retryable = error.retryable;
    this.details = error.details;
  }
}

export function isNormalizedApiError(error: unknown): error is DataServiceError {
  return error instanceof DataServiceError;
}

type ClientOptions = {
  baseUrl?: string;
  timeoutMs?: number;
  fetchImpl?: typeof fetch;
};

type RequestOptions = {
  method?: 'GET' | 'POST';
  body?: unknown;
  signal?: AbortSignal;
  normalizeError?: (status: number, payload: unknown) => NormalizedErrorEnvelope;
};

const DEFAULT_TIMEOUT_MS = 60_000;

const defaultBaseUrl = import.meta.env.VITE_DATA_SERVICE_BASE_URL ?? '';

function normalizeStatusCode(status: number): NormalizedErrorCode {
  if (status === 404) return 'not_found';
  if (status === 400 || status === 422) return 'validation_error';
  if (status === 409) return 'conflict';
  if (status === 412 || status === 426) return 'version_or_schema_mismatch';
  return 'unknown_service_error';
}

function capabilityMissingError(message: string): DataServiceError {
  return new DataServiceError({
    code: 'capability_missing',
    message,
    retryable: false
  });
}

function agentWorkflowContractMissing(): DataServiceError {
  return capabilityMissingError(
    'V1.3 Agent Workflow contract is not implemented by data_service. Local folder access and workflow execution remain disabled.'
  );
}

function assertNoAbsolutePathLikeValue(value: string, context: string) {
  if (
    value.includes('/Users') ||
    value.includes('file://') ||
    value.includes('cache_path') ||
    value.includes('artifact_path') ||
    value.includes('physical_path') ||
    value.includes('/private/tmp') ||
    value.includes('/tmp/') ||
    /^[A-Za-z]:\\/.test(value)
  ) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: `${context} contains an internal path-like value.`,
      retryable: false
    });
  }
}

function normalizeUnknownError(error: unknown): NormalizedErrorEnvelope {
  if (error instanceof DataServiceError) {
    return {
      code: error.code,
      message: error.message,
      status: error.status,
      retryable: error.retryable,
      details: error.details
    };
  }

  if (error instanceof DOMException && error.name === 'AbortError') {
    return {
      code: 'request_timeout',
      message: 'The data service request timed out.',
      retryable: true
    };
  }

  if (error instanceof TypeError) {
    return {
      code: 'backend_unavailable',
      message: 'The data service is unavailable.',
      retryable: true
    };
  }

  return {
    code: 'unknown_service_error',
    message: 'The data service returned an unknown error.',
    retryable: false,
    details: error
  };
}

function readMessage(payload: unknown, fallback: string) {
  if (payload && typeof payload === 'object') {
    const candidate = payload as Record<string, unknown>;
    if (typeof candidate.message === 'string') return candidate.message;
    if (typeof candidate.error === 'string') return candidate.error;
  }
  return fallback;
}

function readString(value: unknown) {
  return typeof value === 'string' ? value : undefined;
}

function readBoolean(value: unknown) {
  return typeof value === 'boolean' ? value : undefined;
}

function readNumber(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined;
}

function readStringArray(value: unknown) {
  return Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string') : undefined;
}

function readArtifactRefs(value: unknown) {
  if (!Array.isArray(value)) return undefined;
  const refs = value
    .map((item) => {
      if (typeof item === 'string') return item;
      if (item && typeof item === 'object') return readString((item as Record<string, unknown>).artifact_ref);
      return undefined;
    })
    .filter((item): item is string => Boolean(item));
  return refs.length > 0 ? refs : undefined;
}

function asRecord(value: unknown) {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : undefined;
}

function unwrapData(payload: unknown) {
  const record = asRecord(payload);
  if (record && record.data && typeof record.data === 'object') return record.data;
  return payload;
}

function envelopeStatus(payload: unknown) {
  return readString(asRecord(payload)?.status);
}

function envelopeError(payload: unknown) {
  const data = asRecord(unwrapData(payload));
  return asRecord(data?.error);
}

function isBlockedEnvelope(payload: unknown) {
  const status = envelopeStatus(payload);
  return status === 'blocked' || status === 'disposed';
}

function normalizeBlockedEnvelope(payload: unknown): DataServiceError {
  const error = envelopeError(payload);
  const message =
    readString(error?.message) ??
    readString(asRecord(payload)?.message) ??
    readStringArray(asRecord(payload)?.warnings)?.[0] ??
    'The data service could not complete the request.';
  const code = readString(error?.code);
  let normalizedCode: NormalizedErrorCode = 'unknown_service_error';
  if (code?.includes('invalid')) normalizedCode = 'validation_error';
  if (code?.includes('unknown')) normalizedCode = 'not_found';
  if (code?.includes('graph') && (code.includes('artifact') || code.includes('unavailable'))) normalizedCode = 'missing_graph_artifact';
  if (code?.includes('archived')) normalizedCode = 'conflict';
  return new DataServiceError({
    code: normalizedCode,
    message,
    retryable: false,
    details: payload
  });
}

function payloadText(payload: unknown) {
  if (!payload) return '';
  if (typeof payload === 'string') return payload.toLowerCase();
  if (typeof payload === 'object') {
    const record = payload as Record<string, unknown>;
    return [record.code, record.reason, record.message, record.error]
      .filter((value): value is string => typeof value === 'string')
      .join(' ')
      .toLowerCase();
  }
  return '';
}

function isMissingGraphArtifact(status: number, payload: unknown) {
  const text = payloadText(payload);
  return (status === 404 || status === 409) && text.includes('graph') && (text.includes('artifact') || text.includes('no_artifact'));
}

function normalizeHttpError(status: number, payload: unknown): NormalizedErrorEnvelope {
  if (isMissingGraphArtifact(status, payload)) {
    return {
      code: 'missing_graph_artifact',
      message: readMessage(payload, 'Graph artifact is not available for this workspace.'),
      status,
      retryable: false,
      details: payload
    };
  }
  const code = normalizeStatusCode(status);
  return {
    code,
    message: readMessage(payload, `Data service request failed with status ${status}.`),
    status,
    retryable: code === 'backend_unavailable' || code === 'unknown_service_error',
    details: payload
  };
}

function normalizeCapabilityHttpError(status: number, payload: unknown): NormalizedErrorEnvelope {
  if (status === 404) {
    return {
      code: 'capability_missing',
      message: readMessage(payload, 'The data service capability manifest is not available.'),
      status,
      retryable: false,
      details: payload
    };
  }
  return normalizeHttpError(status, payload);
}

async function parseJson(response: Response) {
  const text = await response.text();
  if (!text) return null;
  try {
    return JSON.parse(text) as unknown;
  } catch {
    return text;
  }
}

function assertWorkspaceSummary(value: unknown): WorkspaceSummary {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Workspace summary response is not an object.',
      retryable: false,
      details: value
    });
  }
  const workspace = value as Record<string, unknown>;
  if (typeof workspace.workspace_id !== 'string' || typeof workspace.name !== 'string') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Workspace summary is missing workspace_id or name.',
      retryable: false,
      details: value
    });
  }
  const summary = workspace as WorkspaceSummary;
  const archived = readBoolean(workspace.archived) ?? (readString(workspace.status) ? readString(workspace.status) === 'archived' : undefined);
  return archived === undefined ? summary : { ...summary, archived };
}

function assertWorkspaceDetail(value: unknown): WorkspaceDetail {
  return assertWorkspaceSummary(value) as WorkspaceDetail;
}

function normalizeSourceImportState(value: unknown): SourceImportState {
  if (
    value === 'idle' ||
    value === 'selecting' ||
    value === 'uploading' ||
    value === 'importing' ||
    value === 'imported_not_built' ||
    value === 'ready' ||
    value === 'failed_import' ||
    value === 'removed' ||
    value === 'unsupported_type'
  ) {
    return value;
  }
  if (value === 'failed') return 'failed_import';
  if (value === 'imported') return 'imported_not_built';
  return 'idle';
}

function normalizeSourceBuildState(value: unknown): SourceBuildState {
  if (
    value === 'idle' ||
    value === 'imported_not_built' ||
    value === 'building' ||
    value === 'ready' ||
    value === 'failed_build' ||
    value === 'removed' ||
    value === 'unsupported_type'
  ) {
    return value;
  }
  if (value === 'failed') return 'failed_build';
  if (value === 'completed' || value === 'complete') return 'ready';
  return 'idle';
}

function assertSourceSummary(value: unknown, workspaceId?: string): SourceSummary {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source summary response is not an object.',
      retryable: false,
      details: value
    });
  }

  const source = value as Record<string, unknown>;
  const sourceId = readString(source.source_id);
  const title = readString(source.title) ?? readString(source.name);
  const resolvedWorkspaceId = readString(source.workspace_id) ?? workspaceId;

  if (!sourceId || !title || !resolvedWorkspaceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source summary is missing source_id, workspace_id, or title.',
      retryable: false,
      details: value
    });
  }

  return {
    source_id: sourceId,
    workspace_id: resolvedWorkspaceId,
    title,
    source_type: readString(source.source_type) ?? readString(source.type),
    import_state: normalizeSourceImportState(source.import_state ?? source.ingest_status ?? source.status),
    build_state: normalizeSourceBuildState(source.build_state ?? source.index_state),
    updated_at: readString(source.updated_at),
    trace_available: readBoolean(source.trace_available) ?? readBoolean(source.traceAvailable) ?? true,
    artifact_refs: readArtifactRefs(source.artifact_refs)
  };
}

function assertSourceDetail(value: unknown, workspaceId?: string): SourceDetail {
  const summary = assertSourceSummary(value, workspaceId);
  const source = value as Record<string, unknown>;
  return {
    ...summary,
    description: readString(source.description),
    metadata: source.metadata && typeof source.metadata === 'object' ? (source.metadata as Record<string, unknown>) : undefined
  };
}

function extractWorkspaceList(payload: unknown): WorkspaceSummary[] {
  const body = unwrapData(payload);
  const maybeObject = body as Record<string, unknown>;
  const list = Array.isArray(body)
    ? body
    : Array.isArray(maybeObject?.workspaces)
      ? maybeObject.workspaces
      : Array.isArray(maybeObject?.items)
        ? maybeObject.items
        : null;

  if (!list) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Workspace list response is missing workspaces.',
      retryable: false,
      details: payload
    });
  }

  return list.map(assertWorkspaceSummary);
}

function extractWorkspace(payload: unknown): WorkspaceDetail {
  const body = unwrapData(payload);
  if (body && typeof body === 'object' && 'workspace' in body) {
    return assertWorkspaceDetail((body as Record<string, unknown>).workspace);
  }
  return assertWorkspaceDetail(body);
}

function extractCreateWorkspace(payload: unknown): CreateWorkspaceResponse {
  return { workspace: extractWorkspace(payload) };
}

function extractArchiveResult(workspaceId: string, payload: unknown): WorkspaceArchiveResult {
  const body = unwrapData(payload);
  if (body && typeof body === 'object') {
    const result = body as Record<string, unknown>;
    if (typeof result.workspace_id === 'string' && typeof result.archived === 'boolean') {
      return result as WorkspaceArchiveResult;
    }
    const workspace = asRecord(result.workspace);
    if (typeof workspace?.workspace_id === 'string') {
      return {
        workspace_id: workspace.workspace_id,
        archived: readString(workspace.status) === 'archived' || readBoolean(workspace.archived) === true
      };
    }
  }
  return {
    workspace_id: workspaceId,
    archived: true
  };
}

function extractWorkspaceRename(payload: unknown): CreateWorkspaceResponse {
  return { workspace: extractWorkspace(payload) };
}

function extractSourceList(workspaceId: string, payload: unknown): SourceSummary[] {
  const body = unwrapData(payload);
  const maybeObject = body as Record<string, unknown>;
  const list = Array.isArray(body)
    ? body
    : Array.isArray(maybeObject?.sources)
      ? maybeObject.sources
      : Array.isArray(maybeObject?.items)
        ? maybeObject.items
        : null;

  if (!list) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source list response is missing sources.',
      retryable: false,
      details: payload
    });
  }

  return list.map((source) => assertSourceSummary(source, workspaceId));
}

function extractSource(workspaceId: string, payload: unknown): SourceDetail {
  const body = unwrapData(payload);
  if (body && typeof body === 'object' && 'source' in body) {
    return assertSourceDetail((body as Record<string, unknown>).source, workspaceId);
  }
  return assertSourceDetail(body, workspaceId);
}

function extractCreateSource(workspaceId: string, payload: unknown): CreateSourceResponse {
  const body = unwrapData(payload);
  if (body && typeof body === 'object' && Array.isArray((body as Record<string, unknown>).sources)) {
    const [first] = (body as Record<string, unknown>).sources as unknown[];
    return { source: assertSourceDetail(first, workspaceId) };
  }
  return { source: extractSource(workspaceId, payload) };
}

function extractSourceMutation(workspaceId: string, payload: unknown): CreateSourceResponse {
  return { source: extractSource(workspaceId, payload) };
}

function extractSourceTrace(sourceId: string, payload: unknown): SourceTrace {
  if (!payload || typeof payload !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source trace response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const trace = unwrapData(payload) as Record<string, unknown>;
  const wrapped = trace.trace && typeof trace.trace === 'object' ? (trace.trace as Record<string, unknown>) : trace;
  const source = asRecord(wrapped.source);
  const traceSummary = asRecord(wrapped.trace_summary);
  const returnedSourceId = readString(wrapped.source_id) ?? readString(source?.source_id);
  const traceAvailable = readBoolean(wrapped.trace_available);
  const unavailableReason = readString(wrapped.unavailable_reason);

  if (!returnedSourceId || returnedSourceId !== sourceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source trace response source_id does not match the requested source.',
      retryable: false,
      details: payload
    });
  }

  const provenanceRaw = Array.isArray(wrapped.provenance) ? wrapped.provenance : [];
  const provenance = provenanceRaw
    .map((item) => {
      if (item && typeof item === 'object') {
        const row = item as Record<string, unknown>;
        const label = readString(row.label) ?? readString(row.key);
        const value = readString(row.value) ?? readString(row.text);
        if (label && value) return { label, value };
      }
      if (typeof item === 'string') return { label: 'Provenance', value: item };
      return null;
    })
    .filter((item): item is { label: string; value: string } => item !== null);
  const artifactRefs = readArtifactRefs(wrapped.artifact_refs);
  const title = readString(wrapped.title) ?? readString(wrapped.name) ?? readString(traceSummary?.source_title) ?? readString(source?.title);
  const summary = readString(wrapped.summary) ?? readString(traceSummary?.source_title);
  const hasTraceContent = Boolean(summary || provenance.length);
  const explicitlyUnavailable = traceAvailable === false && Boolean(unavailableReason);

  if (!hasTraceContent && !explicitlyUnavailable) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source trace response is missing trace content or explicit unavailable state.',
      retryable: false,
      details: payload
    });
  }

  return {
    source_id: returnedSourceId,
    title,
    artifact_refs: artifactRefs,
    trace_available: traceAvailable ?? true,
    provenance,
    summary
  };
}

function extractCapabilityManifest(workspaceId: string, payload: unknown): CapabilityManifest {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const manifest = asRecord(raw?.manifest) ?? raw;
  const capabilities = asRecord(manifest?.capabilities);
  const supportedSourceTypesRaw = Array.isArray(manifest?.supported_source_types) ? manifest.supported_source_types : undefined;

  if (!manifest || !capabilities || !supportedSourceTypesRaw) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Capability manifest response is missing manifest, capabilities, or supported_source_types.',
      retryable: false,
      details: payload
    });
  }

  const requiredCapabilityKeys = [
    'source_preview',
    'document_units',
    'evidence_spans',
    'source_level_preview',
    'unit_level_navigation',
    'precise_span_highlight',
    'citation_backjump'
  ] as const;

  for (const key of requiredCapabilityKeys) {
    if (typeof capabilities[key] !== 'boolean') {
      throw new DataServiceError({
        code: 'version_or_schema_mismatch',
        message: `Capability manifest is missing ${key}.`,
        retryable: false,
        details: payload
      });
    }
  }

  const normalizedCapabilities: CapabilityManifest['capabilities'] = {
    source_preview: readBoolean(capabilities.source_preview) ?? false,
    document_units: readBoolean(capabilities.document_units) ?? false,
    evidence_spans: readBoolean(capabilities.evidence_spans) ?? false,
    source_level_preview: readBoolean(capabilities.source_level_preview) ?? false,
    unit_level_navigation: readBoolean(capabilities.unit_level_navigation) ?? false,
    precise_span_highlight: readBoolean(capabilities.precise_span_highlight) ?? false,
    citation_backjump: readBoolean(capabilities.citation_backjump) ?? false
  };
  const ocr = readBoolean(capabilities.ocr);
  if (ocr !== undefined) normalizedCapabilities.ocr = ocr;
  const scannedPdfOcr = readBoolean(capabilities.scanned_pdf_ocr);
  if (scannedPdfOcr !== undefined) normalizedCapabilities.scanned_pdf_ocr = scannedPdfOcr;

  return {
    workspace_id: readString(manifest.workspace_id) ?? workspaceId,
    service_version: readString(manifest.service_version),
    schema_version: readString(manifest.schema_version),
    generated_at: readString(manifest.generated_at),
    capabilities: normalizedCapabilities,
    supported_source_types: supportedSourceTypesRaw.map((item) => {
      const sourceType = asRecord(item);
      const preview = readString(sourceType?.preview);
      if (!sourceType || typeof sourceType.source_type !== 'string' || !['none', 'source', 'unit', 'span'].includes(preview ?? '')) {
        throw new DataServiceError({
          code: 'version_or_schema_mismatch',
          message: 'Capability manifest contains an invalid supported_source_types entry.',
          retryable: false,
          details: payload
        });
      }
      const locatorsRaw = Array.isArray(sourceType.locators) ? sourceType.locators : [];
      const locators = locatorsRaw.filter(
        (locator): locator is 'page_no' | 'slide_no' | 'timestamp' | 'json_path' | 'offset' =>
          locator === 'page_no' ||
          locator === 'slide_no' ||
          locator === 'timestamp' ||
          locator === 'json_path' ||
          locator === 'offset'
      );
      return {
        source_type: sourceType.source_type,
        preview: preview as 'none' | 'source' | 'unit' | 'span',
        locators
      };
    })
  };
}

function normalizeDocumentUnitType(value: unknown): DocumentUnit['unit_type'] {
  if (
    value === 'text' ||
    value === 'page' ||
    value === 'slide' ||
    value === 'section' ||
    value === 'transcript_segment' ||
    value === 'json_node'
  ) {
    return value;
  }
  return 'section';
}

function assertDocumentUnit(value: unknown, sourceId: string): DocumentUnit {
  const unit = asRecord(value);
  const unitId = readString(unit?.unit_id);
  const unitSourceId = readString(unit?.source_id) ?? sourceId;
  if (!unit || !unitId || !unitSourceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'DocumentUnit is missing unit_id or source_id.',
      retryable: false,
      details: value
    });
  }

  return {
    unit_id: unitId,
    source_id: unitSourceId,
    unit_type: normalizeDocumentUnitType(unit.unit_type),
    title: readString(unit.title),
    text_preview: readString(unit.text_preview),
    content_type:
      readString(unit.content_type) === 'text/plain' ||
      readString(unit.content_type) === 'text/markdown' ||
      readString(unit.content_type) === 'text/html'
        ? (readString(unit.content_type) as 'text/plain' | 'text/markdown' | 'text/html')
        : undefined,
    order_index: readNumber(unit.order_index),
    page_no: readNumber(unit.page_no),
    slide_no: readNumber(unit.slide_no),
    timestamp_start_ms: readNumber(unit.timestamp_start_ms),
    timestamp_end_ms: readNumber(unit.timestamp_end_ms),
    json_path: readString(unit.json_path),
    artifact_ref: readString(unit.artifact_ref),
    preview_available: readBoolean(unit.preview_available),
    preview_truncated: readBoolean(unit.preview_truncated),
    preview_size_bytes: readNumber(unit.preview_size_bytes),
    max_preview_size_bytes: readNumber(unit.max_preview_size_bytes)
  };
}

function extractDocumentUnitList(sourceId: string, payload: unknown): DocumentUnitListResponse {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const units = asRecord(raw?.units) ?? raw;
  const resolvedSourceId = readString(units?.source_id) ?? sourceId;
  const itemsRaw = Array.isArray(units?.items) ? units.items : undefined;
  const limit = readNumber(units?.limit);
  const hasMore = readBoolean(units?.has_more);

  if (!units || !resolvedSourceId || !itemsRaw || limit === undefined || hasMore === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'DocumentUnit list response is missing source_id, items, limit, or has_more.',
      retryable: false,
      details: payload
    });
  }

  if (hasMore && !readString(units.next_cursor)) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'DocumentUnit list response has has_more=true without next_cursor.',
      retryable: false,
      details: payload
    });
  }

  return {
    source_id: resolvedSourceId,
    items: itemsRaw.map((item) => assertDocumentUnit(item, resolvedSourceId)),
    next_cursor: readString(units.next_cursor) ?? null,
    limit,
    has_more: hasMore,
    unsupported_reason: readString(units.unsupported_reason)
  };
}

function extractSourcePreview(sourceId: string, payload: unknown): SourcePreviewResponse {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const preview = asRecord(raw?.preview) ?? raw;
  const sourcePreviewId = readString(preview?.source_id);
  const previewAvailable = readBoolean(preview?.preview_available);

  if (!preview || !sourcePreviewId || previewAvailable === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Source preview response is missing source_id or preview_available.',
      retryable: false,
      details: payload
    });
  }

  const contentType = readString(preview.content_type);
  const safeContentType =
    contentType === 'text/plain' || contentType === 'text/markdown' || contentType === 'text/html' ? contentType : undefined;

  return {
    preview: {
      source_id: sourcePreviewId || sourceId,
      title: readString(preview.title),
      source_type: readString(preview.source_type),
      preview_available: previewAvailable,
      content_type: safeContentType,
      text_preview: readString(preview.text_preview),
      units: Array.isArray(preview.units) ? preview.units.map((unit) => assertDocumentUnit(unit, sourcePreviewId)) : undefined,
      next_cursor: readString(preview.next_cursor),
      artifact_refs: readArtifactRefs(preview.artifact_refs),
      unsupported_reason: readString(preview.unsupported_reason),
      preview_truncated: readBoolean(preview.preview_truncated),
      preview_size_bytes: readNumber(preview.preview_size_bytes),
      max_preview_size_bytes: readNumber(preview.max_preview_size_bytes)
    }
  };
}

function extractNotebookGuide(payload: unknown): NotebookGuide {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const guide = asRecord(raw?.guide) ?? raw;
  const guideAvailable = readBoolean(guide?.guide_available);
  const sourceCount = readNumber(guide?.source_count);
  if (!guide || guideAvailable === undefined || sourceCount === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Notebook Guide response is missing guide_available or source_count.',
      retryable: false,
      details: payload
    });
  }
  const topicsRaw = Array.isArray(guide.key_topics) ? guide.key_topics : [];
  const metadata = asRecord(guide.generation_metadata) ?? asRecord(guide.generationMetadata);
  return {
    guide_available: guideAvailable,
    source_count: sourceCount,
    overview: readString(guide.overview) ?? '',
    key_topics: topicsRaw
      .map((topic) => asRecord(topic))
      .filter((topic): topic is Record<string, unknown> => Boolean(topic))
      .map((topic) => ({
        title: readString(topic.title) ?? '主题',
        summary: readString(topic.summary) ?? '',
        ...(Array.isArray(topic.evidence_refs)
          ? { evidence_refs: topic.evidence_refs.map((item, index) => normalizeEvidence(item, index)) }
          : {})
      }))
      .filter((topic) => topic.summary),
    suggested_questions: readStringArray(guide.suggested_questions) ?? [],
    evidence_refs: Array.isArray(guide.evidence_refs)
      ? guide.evidence_refs.map((item, index) => normalizeEvidence(item, index))
      : [],
    unavailable_reason: readString(guide.unavailable_reason),
    generation_metadata: metadata
      ? {
          provider: readString(metadata.provider),
          provider_name: readString(metadata.provider_name),
          model: readString(metadata.model),
          prompt_version: readString(metadata.prompt_version),
          evidence_ref_count: readNumber(metadata.evidence_ref_count),
          fallback_mode: readBoolean(metadata.fallback_mode),
          latency_ms: readNumber(metadata.latency_ms),
          response_schema: readString(metadata.response_schema),
          error_code: readString(metadata.error_code)
        }
      : undefined
  };
}

function extractStudioArtifact(payload: unknown): StudioArtifact {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const artifact = asRecord(raw?.artifact) ?? raw;
  const artifactId = readString(artifact?.artifact_id) ?? readString(artifact?.artifactId);
  const artifactType = readString(artifact?.artifact_type) ?? readString(artifact?.artifactType);
  const title = readString(artifact?.title);
  const artifactAvailable = readBoolean(artifact?.artifact_available) ?? readBoolean(artifact?.artifactAvailable);
  if (!artifact || !artifactId || !artifactType || !title || artifactAvailable === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Studio artifact response is missing required fields.',
      retryable: false,
      details: payload
    });
  }
  const sectionsRaw = Array.isArray(artifact.sections) ? artifact.sections : [];
  const metadata = asRecord(artifact.generation_metadata) ?? asRecord(artifact.generationMetadata);
  return {
    artifact_id: artifactId,
    artifact_type: artifactType,
    title,
    artifact_available: artifactAvailable,
    summary: readString(artifact.summary) ?? '',
    sections: sectionsRaw
      .map((section) => asRecord(section))
      .filter((section): section is Record<string, unknown> => Boolean(section))
      .map((section) => ({
        title: readString(section.title) ?? '未命名段落',
        content: readString(section.content) ?? '',
        ...(Array.isArray(section.evidence_refs)
          ? { evidence_refs: section.evidence_refs.map((item, index) => normalizeEvidence(item, index)) }
          : {})
      })),
    evidence_refs: Array.isArray(artifact.evidence_refs)
      ? artifact.evidence_refs.map((item, index) => normalizeEvidence(item, index))
      : [],
    unsupported_reason: readString(artifact.unsupported_reason) ?? readString(artifact.unsupportedReason),
    generation_metadata: metadata
      ? {
          provider: readString(metadata.provider),
          provider_name: readString(metadata.provider_name),
          model: readString(metadata.model),
          prompt_version: readString(metadata.prompt_version),
          artifact_type: readString(metadata.artifact_type),
          evidence_ref_count: readNumber(metadata.evidence_ref_count),
          fallback_mode: readBoolean(metadata.fallback_mode),
          latency_ms: readNumber(metadata.latency_ms),
          response_schema: readString(metadata.response_schema),
          error_code: readString(metadata.error_code)
        }
      : undefined
  };
}

function extractResearchReport(payload: unknown): ResearchReport {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  const report = asRecord(raw?.research) ?? raw;
  const available = readBoolean(report?.research_available) ?? readBoolean(report?.researchAvailable);
  const question = readString(report?.question);
  if (!report || available === undefined || !question) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Research response is missing required fields.',
      retryable: false,
      details: payload
    });
  }
  const mapEvidenceArray = (value: unknown) => (Array.isArray(value) ? value.map((item, index) => normalizeEvidence(item, index)) : []);
  const conclusionsRaw = Array.isArray(report.supported_conclusions) ? report.supported_conclusions : [];
  const inferencesRaw = Array.isArray(report.inferences) ? report.inferences : [];
  const conflictsRaw = Array.isArray(report.conflicts) ? report.conflicts : [];
  const metadata = asRecord(report.generation_metadata) ?? asRecord(report.generationMetadata);
  return {
    research_available: available,
    question,
    coverage_status: readString(report.coverage_status) ?? 'unknown',
    answer_basis: readString(report.answer_basis) ?? 'unknown',
    answer: readString(report.answer) ?? '',
    supported_conclusions: conclusionsRaw
      .map((item) => asRecord(item))
      .filter((item): item is Record<string, unknown> => Boolean(item))
      .map((item) => ({
        claim: readString(item.claim) ?? '',
        evidence_refs: mapEvidenceArray(item.evidence_refs)
      })),
    inferences: inferencesRaw
      .map((item) => asRecord(item))
      .filter((item): item is Record<string, unknown> => Boolean(item))
      .map((item) => ({
        inference: readString(item.inference) ?? '',
        inference_notice: readString(item.inference_notice),
        evidence_refs: mapEvidenceArray(item.evidence_refs)
      })),
    conflicts: conflictsRaw
      .map((item) => asRecord(item))
      .filter((item): item is Record<string, unknown> => Boolean(item))
      .map((item) => ({
        topic: readString(item.topic) ?? '',
        positions: Array.isArray(item.positions)
          ? item.positions
              .map((position) => asRecord(position))
              .filter((position): position is Record<string, unknown> => Boolean(position))
              .map((position) => ({
                claim: readString(position.claim) ?? '',
                evidence_refs: mapEvidenceArray(position.evidence_refs)
              }))
          : []
      })),
    missing_evidence: readStringArray(report.missing_evidence) ?? [],
    suggested_source_actions: readStringArray(report.suggested_source_actions) ?? [],
    evidence_refs: mapEvidenceArray(report.evidence_refs),
    generation_metadata: metadata
      ? {
          provider: readString(metadata.provider),
          provider_name: readString(metadata.provider_name),
          model: readString(metadata.model),
          prompt_version: readString(metadata.prompt_version),
          evidence_ref_count: readNumber(metadata.evidence_ref_count),
          fallback_mode: readBoolean(metadata.fallback_mode)
        }
      : undefined
  };
}

function assertPreviewSourceId(sourceId: string) {
  if (
    !sourceId ||
    sourceId.includes('://') ||
    sourceId.includes('/') ||
    sourceId.includes('\\') ||
    /^[A-Za-z]:/.test(sourceId) ||
    sourceId.startsWith('source-')
  ) {
    throw new DataServiceError({
      code: 'validation_error',
      message: 'Source preview requires a registry source_id.',
      retryable: false
    });
  }
}

function assertDocumentUnitRouteIds(sourceId: string, unitId?: string) {
  assertPreviewSourceId(sourceId);
  if (unitId !== undefined && (!unitId || unitId.includes('://') || unitId.includes('/') || unitId.startsWith('source-') || /^\d+$/.test(unitId))) {
    throw new DataServiceError({
      code: 'validation_error',
      message: 'DocumentUnit detail requires a backend DocumentUnit unit_id.',
      retryable: false
    });
  }
}

function assertEvidenceSpanRouteIds(sourceId: string, unitId: string, evidenceId: string) {
  assertDocumentUnitRouteIds(sourceId, unitId);
  if (
    !evidenceId ||
    evidenceId.includes('://') ||
    evidenceId.includes('/') ||
    evidenceId.startsWith('source-') ||
    /^\d+$/.test(evidenceId)
  ) {
    throw new DataServiceError({
      code: 'validation_error',
      message: 'EvidenceSpan detail requires a backend EvidenceSpan evidence_id.',
      retryable: false
    });
  }
}

function normalizeOffsetBasis(value: unknown): EvidenceSpan['offset_basis'] | undefined {
  if (value === 'utf8_bytes' || value === 'unicode_codepoints' || value === 'utf16_code_units' || value === 'normalized_text') {
    return value;
  }
  return undefined;
}

function normalizeOffsetRange(value: unknown): EvidenceSpan['offset_range'] | undefined {
  if (value === 'half_open' || value === 'closed') return value;
  return undefined;
}

function normalizeTextBasis(value: unknown): EvidenceSpan['text_basis'] | undefined {
  if (value === 'document_unit_text' || value === 'normalized_source_text') return value;
  return undefined;
}

function assertEvidenceSpan(value: unknown, sourceId: string, unitId: string, evidenceId: string): EvidenceSpan {
  const span = asRecord(value);
  const spanId = readString(span?.evidence_id);
  const spanSourceId = readString(span?.source_id);
  const spanUnitId = readString(span?.unit_id);
  if (!span || !spanId || !spanSourceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'EvidenceSpan response is missing evidence_id or source_id.',
      retryable: false,
      details: value
    });
  }
  if (spanId !== evidenceId || spanSourceId !== sourceId || (spanUnitId && spanUnitId !== unitId)) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'EvidenceSpan response ids do not match the requested source/unit/evidence ids.',
      retryable: false,
      details: value
    });
  }
  const locator = asRecord(span.locator);
  return {
    evidence_id: spanId,
    source_id: spanSourceId,
    unit_id: spanUnitId,
    start_offset: readNumber(span.start_offset),
    end_offset: readNumber(span.end_offset),
    offset_basis: normalizeOffsetBasis(span.offset_basis),
    offset_range: normalizeOffsetRange(span.offset_range),
    text_basis: normalizeTextBasis(span.text_basis),
    snippet: readString(span.snippet),
    locator: locator
      ? {
          page_no: readNumber(locator.page_no),
          slide_no: readNumber(locator.slide_no),
          timestamp_start_ms: readNumber(locator.timestamp_start_ms),
          timestamp_end_ms: readNumber(locator.timestamp_end_ms),
          json_path: readString(locator.json_path)
        }
      : undefined,
    preview_available: readBoolean(span.preview_available)
  };
}

function documentUnitListQuery(input?: DocumentUnitListRequest) {
  const params = new window.URLSearchParams();
  if (input?.limit !== undefined) params.set('limit', String(input.limit));
  if (input?.cursor) params.set('cursor', input.cursor);
  const query = params.toString();
  return query ? `?${query}` : '';
}

function normalizeFolderExtractionStatus(value: unknown): FolderFile['extraction_status'] {
  if (value === 'extracted' || value === 'skipped' || value === 'unsupported' || value === 'failed') return value;
  return 'skipped';
}

function assertFolderNode(value: unknown): FolderNode {
  const node = asRecord(value);
  const folderId = readString(node?.folder_id);
  const relativePath = readString(node?.relative_path);
  const depth = readNumber(node?.depth);
  const fileCount = readNumber(node?.file_count);
  const childFolderCount = readNumber(node?.child_folder_count);
  if (!node || !folderId || !relativePath || depth === undefined || fileCount === undefined || childFolderCount === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'FolderNode is missing folder_id, relative_path, depth, file_count, or child_folder_count.',
      retryable: false,
      details: value
    });
  }
  assertNoAbsolutePathLikeValue(relativePath, 'FolderNode.relative_path');
  return {
    folder_id: folderId,
    parent_folder_id: readString(node.parent_folder_id),
    relative_path: relativePath,
    depth,
    file_count: fileCount,
    child_folder_count: childFolderCount
  };
}

function assertFolderFile(value: unknown): FolderFile {
  const file = asRecord(value);
  const fileId = readString(file?.file_id);
  const relativePath = readString(file?.relative_path);
  const extension = readString(file?.extension);
  const sizeBytes = readNumber(file?.size_bytes);
  if (!file || !fileId || !relativePath || !extension || sizeBytes === undefined) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'FolderFile is missing file_id, relative_path, extension, or size_bytes.',
      retryable: false,
      details: value
    });
  }
  assertNoAbsolutePathLikeValue(relativePath, 'FolderFile.relative_path');
  if (extension !== '.md' && extension !== '.txt') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'V1.3-B folder files must be limited to md/txt.',
      retryable: false,
      details: value
    });
  }
  return {
    file_id: fileId,
    folder_id: readString(file.folder_id),
    relative_path: relativePath,
    extension,
    size_bytes: sizeBytes,
    extraction_status: normalizeFolderExtractionStatus(file.extraction_status),
    text_preview: readString(file.text_preview)
  };
}

function normalizeSkippedFileReason(value: unknown): SkippedFileReason | undefined {
  const allowed: ReadonlySet<SkippedFileReason> = new Set([
    'hidden_file',
    'hidden_dir',
    'excluded_dir',
    'unsupported_extension',
    'secret_like_file',
    'max_file_size_exceeded',
    'binary_file',
    'symlink_skipped',
    'extract_failed',
    'permission_denied'
  ]);
  return typeof value === 'string' && allowed.has(value as SkippedFileReason) ? (value as SkippedFileReason) : undefined;
}

function assertFolderCollection(workspaceId: string, value: unknown): FolderCollection {
  const collection = asRecord(value);
  const collectionId = readString(collection?.collection_id);
  const returnedWorkspaceId = readString(collection?.workspace_id);
  const rootLabel = readString(collection?.root_label);
  const folders = Array.isArray(collection?.folders) ? collection.folders.map(assertFolderNode) : undefined;
  const files = Array.isArray(collection?.files) ? collection.files.map(assertFolderFile) : undefined;
  const skippedRaw = Array.isArray(collection?.skipped_files) ? collection.skipped_files : undefined;
  if (!collection || !collectionId || !returnedWorkspaceId || !rootLabel || !folders || !files || !skippedRaw) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'FolderCollection response is missing collection_id, workspace_id, root_label, folders, files, or skipped_files.',
      retryable: false,
      details: value
    });
  }
  if (returnedWorkspaceId !== workspaceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'FolderCollection workspace_id does not match the requested workspace.',
      retryable: false,
      details: value
    });
  }
  assertNoAbsolutePathLikeValue(rootLabel, 'FolderCollection.root_label');
  return {
    collection_id: collectionId,
    workspace_id: returnedWorkspaceId,
    root_label: rootLabel,
    folders,
    files,
    skipped_files: skippedRaw.map((item) => {
      const skipped = asRecord(item);
      const relativePath = readString(skipped?.relative_path);
      const skippedReason = normalizeSkippedFileReason(skipped?.skipped_reason);
      if (!relativePath || !skippedReason) {
        throw new DataServiceError({
          code: 'version_or_schema_mismatch',
          message: 'SkippedFile is missing relative_path or skipped_reason.',
          retryable: false,
          details: item
        });
      }
      assertNoAbsolutePathLikeValue(relativePath, 'SkippedFile.relative_path');
      return { relative_path: relativePath, skipped_reason: skippedReason };
    })
  };
}

function assertPermissionGrant(workspaceId: string, value: unknown): PermissionGrant {
  const grant = asRecord(value);
  const permissionGrantId = readString(grant?.permission_grant_id);
  const returnedWorkspaceId = readString(grant?.workspace_id);
  const rootLabel = readString(grant?.root_label);
  const status = readString(grant?.status);
  const scopes = readStringArray(grant?.scopes);
  if (!grant || !permissionGrantId || !returnedWorkspaceId || !rootLabel || !status || !scopes) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'PermissionGrant is missing permission_grant_id, workspace_id, root_label, status, or scopes.',
      retryable: false,
      details: value
    });
  }
  if (returnedWorkspaceId !== workspaceId || !['active', 'expired', 'revoked'].includes(status)) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'PermissionGrant has invalid workspace_id or status.',
      retryable: false,
      details: value
    });
  }
  assertNoAbsolutePathLikeValue(rootLabel, 'PermissionGrant.root_label');
  return {
    permission_grant_id: permissionGrantId,
    workspace_id: returnedWorkspaceId,
    root_label: rootLabel,
    scopes,
    status: status as PermissionGrant['status'],
    created_at: readString(grant.created_at),
    expires_at: readString(grant.expires_at) ?? null
  };
}

function extractFolderScanResponse(workspaceId: string, payload: unknown): FolderScanResponse {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  return {
    collection: assertFolderCollection(workspaceId, raw?.collection),
    permission_grant: assertPermissionGrant(workspaceId, raw?.permission_grant)
  };
}

function normalizeWorkflowStepStatus(value: unknown): WorkflowStep['status'] {
  if (value === 'pending' || value === 'running' || value === 'completed' || value === 'failed' || value === 'skipped') return value;
  return 'failed';
}

function assertWorkflowStep(value: unknown): WorkflowStep {
  const step = asRecord(value);
  const stepId = readString(step?.step_id);
  const name = readString(step?.name);
  if (!step || !stepId || !name) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'WorkflowStep is missing step_id or name.',
      retryable: false,
      details: value
    });
  }
  const logs = readStringArray(step.logs) ?? [];
  logs.forEach((log) => assertNoAbsolutePathLikeValue(log, 'WorkflowStep.logs'));
  return {
    step_id: stepId,
    name,
    status: normalizeWorkflowStepStatus(step.status),
    input_ref: readString(step.input_ref),
    output_ref: readString(step.output_ref),
    logs,
    started_at: readString(step.started_at),
    finished_at: readString(step.finished_at),
    error_code: readString(step.error_code),
    error_message: readString(step.error_message),
    retry_count: readNumber(step.retry_count) ?? 0,
    artifact_refs: readStringArray(step.artifact_refs) ?? []
  };
}

function normalizeWorkflowStatus(value: unknown): Workflow['status'] {
  if (value === 'draft' || value === 'ready' || value === 'disabled') return value;
  return 'disabled';
}

function assertWorkflow(value: unknown): Workflow {
  const workflow = asRecord(value);
  const workflowId = readString(workflow?.workflow_id);
  const name = readString(workflow?.name);
  const templateId = readString(workflow?.template_id);
  const steps = Array.isArray(workflow?.steps) ? workflow.steps.map(assertWorkflowStep) : undefined;
  if (!workflow || !workflowId || !name || !templateId || !steps) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Workflow is missing workflow_id, name, template_id, or steps.',
      retryable: false,
      details: value
    });
  }
  return {
    workflow_id: workflowId,
    name,
    template_id: templateId,
    status: normalizeWorkflowStatus(workflow.status),
    required_permissions: readStringArray(workflow.required_permissions) ?? [],
    draft_parameters: normalizeWorkflowDraftParameters(workflow.draft_parameters),
    steps
  };
}

function normalizeWorkflowDraftParameters(value: unknown): Workflow['draft_parameters'] {
  const params = asRecord(value);
  if (!params) return undefined;
  const authorizedRootHint = readString(params.authorized_root_hint);
  if (authorizedRootHint) assertNoAbsolutePathLikeValue(authorizedRootHint, 'Workflow.draft_parameters.authorized_root_hint');
  return {
    authorized_root_hint: authorizedRootHint,
    include_extensions: readStringArray(params.include_extensions) ?? [],
    exclude_globs: readStringArray(params.exclude_globs) ?? [],
    follow_symlinks: readBoolean(params.follow_symlinks) ?? false,
    requires_user_confirmation: readBoolean(params.requires_user_confirmation) ?? true
  };
}

function assertAgentTask(workspaceId: string, value: unknown): AgentWorkflowDraftResponse['task'] {
  const task = asRecord(value);
  const taskId = readString(task?.task_id);
  const taskWorkspaceId = readString(task?.workspace_id);
  const userGoal = readString(task?.user_goal);
  const status = readString(task?.status);
  if (!task || !taskId || !taskWorkspaceId || !userGoal || !status) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'AgentTask is missing task_id, workspace_id, user_goal, or status.',
      retryable: false,
      details: value
    });
  }
  if (taskWorkspaceId !== workspaceId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'AgentTask workspace_id does not match the requested workspace.',
      retryable: false,
      details: value
    });
  }
  return {
    task_id: taskId,
    workspace_id: taskWorkspaceId,
    user_goal: userGoal,
    status: status === 'draft' || status === 'awaiting_approval' || status === 'running' || status === 'completed' || status === 'failed'
      ? status
      : 'failed',
    workflow_id: readString(task.workflow_id)
  };
}

function normalizeWorkflowRunStatus(value: unknown): WorkflowRun['status'] {
  if (value === 'pending' || value === 'running' || value === 'completed' || value === 'failed' || value === 'cancelled') return value;
  return 'failed';
}

function assertWorkflowRun(value: unknown): FolderSummaryWorkflowRunResponse['run'] {
  const run = asRecord(value);
  const runId = readString(run?.run_id);
  const workflowId = readString(run?.workflow_id);
  const createdAt = readString(run?.created_at);
  const report = asRecord(run?.run_report);
  if (!run || !runId || !workflowId || !createdAt || !report) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'WorkflowRun is missing run_id, workflow_id, created_at, or run_report.',
      retryable: false,
      details: value
    });
  }
  return {
    run_id: runId,
    workflow_id: workflowId,
    status: normalizeWorkflowRunStatus(run.status),
    created_at: createdAt,
    finished_at: readString(run.finished_at),
    dry_run: readBoolean(run.dry_run) ?? true,
    run_report: {
      scanned_file_count: readNumber(report.scanned_file_count) ?? 0,
      manifest_file_count: readNumber(report.manifest_file_count),
      extracted_file_count: readNumber(report.extracted_file_count) ?? 0,
      skipped_file_count: readNumber(report.skipped_file_count) ?? 0,
      folder_count: readNumber(report.folder_count),
      generated_artifact_count: readNumber(report.generated_artifact_count) ?? 0
    },
    artifacts: Array.isArray(run.artifacts) ? run.artifacts.map(assertSummaryArtifact) : []
  };
}

function assertSummaryArtifact(value: unknown): SummaryArtifact {
  const artifact = asRecord(value);
  const artifactId = readString(artifact?.artifact_id);
  const title = readString(artifact?.title);
  const artifactType = readString(artifact?.artifact_type);
  const collectionId = readString(artifact?.collection_id);
  const status = readString(artifact?.status);
  const schemaVersion = readString(artifact?.schema_version);
  const coverage = asRecord(artifact?.coverage);
  const markdown = readString(artifact?.markdown);
  if (!artifact || !artifactId || !title || !collectionId || !schemaVersion || !coverage || !markdown) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'SummaryArtifact is missing required fields.',
      retryable: false,
      details: value
    });
  }
  const evidenceRefsRaw = Array.isArray(artifact.evidence_refs) ? artifact.evidence_refs : [];
  return {
    artifact_id: artifactId,
    title,
    artifact_type: artifactType === 'folder_summary' ? 'folder_summary' : 'root_summary',
    folder_id: readString(artifact.folder_id),
    collection_id: collectionId,
    status:
      status === 'draft' || status === 'ready' || status === 'failed' || status === 'skipped'
        ? status
        : 'failed',
    schema_version: schemaVersion,
    coverage: {
      file_count: readNumber(coverage.file_count) ?? 0,
      extracted_file_count: readNumber(coverage.extracted_file_count) ?? 0,
      skipped_file_count: readNumber(coverage.skipped_file_count) ?? 0,
      evidence_ref_count: readNumber(coverage.evidence_ref_count) ?? 0
    },
    markdown,
    evidence_refs: evidenceRefsRaw.map((item) => {
      const ref = asRecord(item);
      const relativePath = readString(ref?.relative_path);
      if (relativePath) assertNoAbsolutePathLikeValue(relativePath, 'EvidenceRef.relative_path');
      const evidenceStatus = readString(ref?.evidence_status);
      const normalizedRef: SummaryArtifact['evidence_refs'][number] = {
        evidence_status: evidenceStatus === 'source_unit_span' ? 'source_unit_span' : 'relative_path_only'
      };
      const sourceId = readString(ref?.source_id);
      const sourceTitle = readString(ref?.source_title) ?? readString(ref?.sourceTitle) ?? readString(ref?.title);
      const unitId = readString(ref?.unit_id);
      const evidenceId = readString(ref?.evidence_id);
      const fileId = readString(ref?.file_id);
      const snippet = readString(ref?.snippet) ?? readString(ref?.text);
      if (sourceId) normalizedRef.source_id = sourceId;
      if (sourceTitle) normalizedRef.source_title = sourceTitle;
      if (unitId) normalizedRef.unit_id = unitId;
      if (evidenceId) normalizedRef.evidence_id = evidenceId;
      if (fileId) normalizedRef.file_id = fileId;
      if (relativePath) normalizedRef.relative_path = relativePath;
      if (snippet) normalizedRef.snippet = snippet;
      return normalizedRef;
    })
  };
}

function extractFolderSummaryWorkflowRunResponse(workspaceId: string, payload: unknown): FolderSummaryWorkflowRunResponse {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  return {
    workflow: assertWorkflow(raw?.workflow),
    run: assertWorkflowRun(raw?.run),
    collection: assertFolderCollection(workspaceId, raw?.collection),
    permission_grant: assertPermissionGrant(workspaceId, raw?.permission_grant)
  };
}

function extractAgentWorkflowDraftResponse(workspaceId: string, payload: unknown): AgentWorkflowDraftResponse {
  const body = unwrapData(payload);
  const raw = asRecord(body);
  return {
    task: assertAgentTask(workspaceId, raw?.task),
    workflow: raw?.workflow ? assertWorkflow(raw.workflow) : undefined
  };
}

function extractBuildStart(payload: unknown): BuildStartResponse {
  if (!payload || typeof payload !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Build start response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const response = payload as Record<string, unknown>;
  const operationId = readString(response.operation_id);
  if (!operationId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Build start response is missing operation_id.',
      retryable: false,
      details: payload
    });
  }
  return { operation_id: operationId };
}

function normalizeOperationStatus(value: unknown): BuildOperation['status'] {
  if (value === 'queued' || value === 'running' || value === 'completed' || value === 'failed' || value === 'cancelled') {
    return value;
  }
  if (value === 'canceled') return 'cancelled';
  if (value === 'succeeded' || value === 'success' || value === 'done') return 'completed';
  return 'operation_unavailable';
}

function extractBuildOperation(operationId: string, payload: unknown): BuildOperation {
  if (!payload || typeof payload !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Build operation response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const maybeOperation = payload as Record<string, unknown>;
  const operation =
    maybeOperation.operation && typeof maybeOperation.operation === 'object'
      ? (maybeOperation.operation as Record<string, unknown>)
      : asRecord(maybeOperation.data) ?? maybeOperation;
  const status = normalizeOperationStatus(operation.status ?? maybeOperation.status ?? operation.state);
  return {
    operation_id: readString(operation.operation_id) ?? readString(maybeOperation.operation_id) ?? operationId,
    status,
    cancellable:
      readBoolean(operation.cancellable) ??
      readBoolean(operation.can_cancel) ??
      (status === 'queued' || status === 'running'),
    message: readString(operation.message),
    started_at: readString(operation.started_at),
    completed_at: readString(operation.completed_at)
  };
}

function normalizeEvidence(rawEvidence: unknown, index: number, registrySourceIds = new Set<string>()): AnswerEvidence {
  if (!rawEvidence || typeof rawEvidence !== 'object') {
    return {
      evidenceKey: `evidence-${index}`,
      traceAvailable: false,
      traceUnavailableReason: 'missing_source_id',
      snippet: typeof rawEvidence === 'string' ? rawEvidence : undefined
    };
  }

  const evidence = rawEvidence as Record<string, unknown>;
  const meta = asRecord(evidence.meta) ?? asRecord(evidence.metadata);
  const explicitSourceId = readString(evidence.source_id) ?? readString(evidence.sourceId);
  const rawSourceRef = readString(evidence.source) ?? readString(meta?.slug) ?? readString(evidence.slug);
  const artifactRefs =
    readArtifactRefs(evidence.artifact_refs) ?? readArtifactRefs(evidence.artifactRefs) ?? readArtifactRefs(evidence.source_refs);
  const locatorRaw = asRecord(evidence.locator);
  const locator = locatorRaw
    ? {
        pageNo: readNumber(locatorRaw.page_no),
        slideNo: readNumber(locatorRaw.slide_no),
        timestampStartMs: readNumber(locatorRaw.timestamp_start_ms),
        timestampEndMs: readNumber(locatorRaw.timestamp_end_ms),
        jsonPath: readString(locatorRaw.json_path)
      }
    : undefined;
  const registryKnown = registrySourceIds.size > 0;
  const resolvedSourceId =
    explicitSourceId && (!registryKnown || registrySourceIds.has(explicitSourceId))
      ? explicitSourceId
      : rawSourceRef && registrySourceIds.has(rawSourceRef)
        ? rawSourceRef
        : undefined;
  const sourceRef = resolvedSourceId ? undefined : explicitSourceId ?? rawSourceRef;
  const explicitlyTraceable = readBoolean(evidence.trace_available) ?? readBoolean(evidence.traceAvailable);
  const traceAvailable = Boolean(resolvedSourceId && (explicitlyTraceable ?? true));
  const traceUnavailableReason = traceAvailable
    ? undefined
    : sourceRef
      ? 'source_ref_not_traceable'
      : 'missing_source_id';
  return {
    evidenceKey: readString(evidence.evidence_key) ?? readString(evidence.evidenceKey) ?? `${resolvedSourceId ?? sourceRef ?? 'artifact'}-${index}`,
    sourceId: resolvedSourceId,
    sourceRef,
    sourceTitle: readString(evidence.source_title) ?? readString(evidence.sourceTitle) ?? readString(evidence.title),
    traceAvailable,
    artifactRefs,
    snippet: readString(evidence.snippet) ?? readString(evidence.text),
    confidence: readNumber(evidence.confidence) ?? readNumber(evidence.score),
    traceUnavailableReason,
    unitId: readString(evidence.unit_id) ?? readString(evidence.unitId),
    evidenceId: readString(evidence.evidence_id) ?? readString(evidence.evidenceId),
    locator:
      locator &&
      (locator.pageNo !== undefined ||
        locator.slideNo !== undefined ||
        locator.timestampStartMs !== undefined ||
        locator.timestampEndMs !== undefined ||
        locator.jsonPath)
        ? locator
        : undefined,
    previewAvailable: readBoolean(evidence.preview_available) ?? readBoolean(evidence.previewAvailable)
  };
}

function extractQueryResponse(payload: unknown, registrySourceIds?: string[]): QueryResponse {
  if (!payload || typeof payload !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Query response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const raw = unwrapData(payload) as Record<string, unknown>;
  const answer =
    readString(raw.answer) ??
    readString(raw.text) ??
    readString(raw.response) ??
    readString((raw.result as Record<string, unknown> | undefined)?.answer);
  if (!answer) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Query response is missing answer text.',
      retryable: false,
      details: payload
    });
  }
  const rawEvidence =
    (Array.isArray(raw.evidence) && raw.evidence) ||
    (Array.isArray(raw.evidence_refs) && raw.evidence_refs) ||
    (Array.isArray(raw.sources) && raw.sources) ||
    (Array.isArray(raw.hits) && raw.hits) ||
    (Array.isArray(raw.items) && raw.items) ||
    (Array.isArray(raw.results) && raw.results) ||
    [];
  const sourceIdSet = new Set(registrySourceIds?.filter(Boolean) ?? []);
  const evidence = rawEvidence.map((item, index) => normalizeEvidence(item, index, sourceIdSet));
  const usefulEvidence = evidence.filter((item) => item.sourceId || item.sourceRef || (item.artifactRefs && item.artifactRefs.length > 0));
  const suggestedSourceActions = readStringArray(raw.suggested_source_actions) ?? readStringArray(raw.suggestedSourceActions) ?? [];
  return {
    answer,
    evidence: usefulEvidence,
    noEvidence: readBoolean(raw.no_evidence) ?? readBoolean(raw.noEvidence) ?? usefulEvidence.length === 0,
    coverageStatus: readString(raw.coverage_status) ?? readString(raw.coverageStatus),
    answerBasis: readString(raw.answer_basis) ?? readString(raw.answerBasis),
    unsupportedReason: readString(raw.unsupported_reason) ?? readString(raw.unsupportedReason),
    suggestedSourceActions,
    inferenceNotice: readString(raw.inference_notice) ?? readString(raw.inferenceNotice)
  };
}

function normalizeSessionState(value: unknown): SessionState {
  if (
    value === 'idle' ||
    value === 'creating' ||
    value === 'active' ||
    value === 'ingesting' ||
    value === 'ingested_not_built' ||
    value === 'building' ||
    value === 'ready' ||
    value === 'failed_ingest' ||
    value === 'failed_build' ||
    value === 'closed'
  ) {
    return value;
  }
  if (value === 'failed') return 'failed_build';
  if (value === 'complete' || value === 'completed') return 'ready';
  return 'active';
}

function assertSessionSummary(value: unknown, workspaceId?: string): SessionSummary {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Session summary response is not an object.',
      retryable: false,
      details: value
    });
  }

  const session = value as Record<string, unknown>;
  const sessionId = readString(session.session_id);
  const resolvedWorkspaceId = readString(session.workspace_id) ?? workspaceId;
  const title = readString(session.title) ?? readString(session.name) ?? sessionId;

  if (!sessionId || !resolvedWorkspaceId || !title) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Session summary is missing session_id, workspace_id, or title.',
      retryable: false,
      details: value
    });
  }

  return {
    session_id: sessionId,
    workspace_id: resolvedWorkspaceId,
    title,
    state: normalizeSessionState(session.state ?? session.status),
    created_at: readString(session.created_at),
    updated_at: readString(session.updated_at),
    closed_at: readString(session.closed_at)
  };
}

function assertSessionDetail(value: unknown, workspaceId?: string): SessionDetail {
  const summary = assertSessionSummary(value, workspaceId);
  const session = value as Record<string, unknown>;
  const lastAnswer = session.last_answer && typeof session.last_answer === 'object' ? extractQueryResponse(session.last_answer) : undefined;
  return {
    ...summary,
    context_summary: readString(session.context_summary) ?? readString(session.summary),
    artifact_refs: readArtifactRefs(session.artifact_refs),
    source_ids: readStringArray(session.source_ids),
    last_answer: lastAnswer,
    metadata: session.metadata && typeof session.metadata === 'object' ? (session.metadata as Record<string, unknown>) : undefined
  };
}

function extractSessionList(workspaceId: string, payload: unknown): SessionSummary[] {
  const body = unwrapData(payload);
  const maybeObject = body as Record<string, unknown>;
  const list = Array.isArray(body)
    ? body
    : Array.isArray(maybeObject?.sessions)
      ? maybeObject.sessions
      : Array.isArray(maybeObject?.items)
        ? maybeObject.items
        : null;
  if (!list) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Session list response is missing sessions.',
      retryable: false,
      details: payload
    });
  }
  return list.map((session) => assertSessionSummary(session, workspaceId));
}

function extractSession(workspaceId: string, payload: unknown): SessionDetail {
  const body = unwrapData(payload);
  if (body && typeof body === 'object' && 'session' in body) {
    return assertSessionDetail((body as Record<string, unknown>).session, workspaceId);
  }
  return assertSessionDetail(body, workspaceId);
}

function extractCreateSession(workspaceId: string, payload: unknown): CreateSessionResponse {
  return { session: extractSession(workspaceId, payload) };
}

function extractCloseSession(sessionId: string, payload: unknown): CloseSessionResponse {
  const body = unwrapData(payload);
  if (body && typeof body === 'object') {
    const response = body as Record<string, unknown>;
    const resolvedSessionId = readString(response.session_id) ?? readString((response.session as Record<string, unknown> | undefined)?.session_id);
    const closed = readBoolean(response.closed) ?? normalizeSessionState((response.session as Record<string, unknown> | undefined)?.state) === 'closed';
    if (resolvedSessionId) return { session_id: resolvedSessionId, closed };
  }
  return { session_id: sessionId, closed: true };
}

function extractSessionIngest(workspaceId: string, payload: unknown): SessionIngestResponse {
  return { session: extractSession(workspaceId, payload) };
}

function normalizeGraphStatus(value: unknown): 'ready' | 'missing_artifact' | 'unavailable' {
  if (value === 'ready' || value === 'missing_artifact' || value === 'unavailable') return value;
  if (value === 'missing' || value === 'no_artifact') return 'missing_artifact';
  return 'ready';
}

function assertGraphNode(value: unknown, index: number): GraphNode {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph node response is not an object.',
      retryable: false,
      details: value
    });
  }
  const node = value as Record<string, unknown>;
  const nodeId = readString(node.node_id) ?? readString(node.id) ?? `node-${index}`;
  const label = readString(node.label) ?? readString(node.title) ?? readString(node.name) ?? nodeId;
  return {
    node_id: nodeId,
    entity_id: readString(node.entity_id) ?? readString(node.entityId),
    label,
    node_type: readString(node.node_type) ?? readString(node.type),
    weight: readNumber(node.weight) ?? readNumber(node.score),
    source_ids: readStringArray(node.source_ids),
    artifact_refs: readArtifactRefs(node.artifact_refs)
  };
}

function assertGraphEdge(value: unknown, index: number): GraphEdge {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph edge response is not an object.',
      retryable: false,
      details: value
    });
  }
  const edge = value as Record<string, unknown>;
  const sourceNodeId = readString(edge.source_node_id) ?? readString(edge.source) ?? readString(edge.from);
  const targetNodeId = readString(edge.target_node_id) ?? readString(edge.target) ?? readString(edge.to);
  if (!sourceNodeId || !targetNodeId) {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph edge is missing source or target node id.',
      retryable: false,
      details: value
    });
  }
  return {
    edge_id: readString(edge.edge_id) ?? readString(edge.id) ?? `edge-${index}`,
    source_node_id: sourceNodeId,
    target_node_id: targetNodeId,
    label: readString(edge.label) ?? readString(edge.relationship),
    weight: readNumber(edge.weight) ?? readNumber(edge.score)
  };
}

function assertGraphNeighbor(value: unknown, index: number): GraphNeighbor {
  const node = assertGraphNode(value, index);
  const raw = value as Record<string, unknown>;
  return {
    ...node,
    relationship: readString(raw.relationship) ?? readString(raw.relation)
  };
}

function assertGraphCommunity(value: unknown, index: number): GraphCommunity {
  if (!value || typeof value !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph community response is not an object.',
      retryable: false,
      details: value
    });
  }
  const community = value as Record<string, unknown>;
  const communityId = readString(community.community_id) ?? readString(community.id) ?? `community-${index}`;
  return {
    community_id: communityId,
    title: readString(community.title) ?? readString(community.name) ?? communityId,
    summary: readString(community.summary) ?? readString(community.description),
    node_count: readNumber(community.node_count) ?? readNumber(community.entity_count),
    relationship_count: readNumber(community.relationship_count) ?? readNumber(community.edge_count),
    score: readNumber(community.score),
    artifact_refs: readStringArray(community.artifact_refs),
    members: Array.isArray(community.members) ? community.members.map(assertGraphNode) : undefined
  };
}

function extractGraphNeighbors(workspaceId: string, payload: unknown): GraphNeighborsResponse {
  if (isBlockedEnvelope(payload)) throw normalizeBlockedEnvelope(payload);
  const body = unwrapData(payload);
  if (!body || typeof body !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph neighbors response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const raw = body as Record<string, unknown>;
  const nodesRaw = Array.isArray(raw.nodes) ? raw.nodes : [];
  const edgesRaw = Array.isArray(raw.edges) ? raw.edges : [];
  const neighborsRaw = Array.isArray(raw.neighbors) ? raw.neighbors : nodesRaw;
  return {
    workspace_id: readString(raw.workspace_id) ?? workspaceId,
    status: normalizeGraphStatus(raw.status),
    nodes: nodesRaw.map(assertGraphNode),
    edges: edgesRaw.map(assertGraphEdge),
    neighbors: neighborsRaw.map(assertGraphNeighbor),
    artifact_refs: readArtifactRefs(raw.artifact_refs) ?? readArtifactRefs(asRecord(payload)?.artifact_refs),
    summary: readString(raw.summary)
  };
}

function extractGraphCommunities(workspaceId: string, payload: unknown): GraphCommunitiesResponse {
  if (isBlockedEnvelope(payload)) throw normalizeBlockedEnvelope(payload);
  const body = unwrapData(payload);
  if (!body || typeof body !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Graph communities response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const raw = body as Record<string, unknown>;
  const communitiesRaw = Array.isArray(raw.communities)
    ? raw.communities
    : Array.isArray(raw.community)
      ? raw.community
      : Array.isArray(raw.items)
        ? raw.items
        : [];
  return {
    workspace_id: readString(raw.workspace_id) ?? workspaceId,
    status: normalizeGraphStatus(raw.status),
    communities: communitiesRaw.map(assertGraphCommunity),
    artifact_refs: readArtifactRefs(raw.artifact_refs) ?? readArtifactRefs(asRecord(payload)?.artifact_refs),
    summary: readString(raw.summary)
  };
}

function extractSessionGraph(workspaceId: string, sessionId: string, payload: unknown): SessionGraphContextResponse {
  if (isBlockedEnvelope(payload)) throw normalizeBlockedEnvelope(payload);
  const body = unwrapData(payload);
  if (!body || typeof body !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Session graph response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const raw = body as Record<string, unknown>;
  const nodesRaw = Array.isArray(raw.related_nodes) ? raw.related_nodes : Array.isArray(raw.nodes) ? raw.nodes : [];
  const communitiesRaw = Array.isArray(raw.related_communities)
    ? raw.related_communities
    : Array.isArray(raw.communities)
      ? raw.communities
      : [];
  return {
    workspace_id: readString(raw.workspace_id) ?? workspaceId,
    session_id: readString(raw.session_id) ?? sessionId,
    status: normalizeGraphStatus(raw.status),
    related_nodes: nodesRaw.map(assertGraphNode),
    related_communities: communitiesRaw.map(assertGraphCommunity),
    artifact_refs: readArtifactRefs(raw.artifact_refs) ?? readArtifactRefs(asRecord(payload)?.artifact_refs),
    summary: readString(raw.summary)
  };
}

function extractQualityFeedback(workspaceId: string, payload: unknown): QualityFeedbackResponse {
  if (isBlockedEnvelope(payload)) throw normalizeBlockedEnvelope(payload);
  const body = unwrapData(payload);
  if (!body || typeof body !== 'object') {
    throw new DataServiceError({
      code: 'version_or_schema_mismatch',
      message: 'Quality feedback response is not an object.',
      retryable: false,
      details: payload
    });
  }
  const raw = body as Record<string, unknown>;
  const feedback = asRecord(raw.feedback) ?? raw;
  const accepted = readBoolean(feedback.accepted) ?? readBoolean(raw.accepted) ?? readBoolean(raw.ok) ?? (readString(feedback.status) === 'recorded' ? true : undefined);
  return {
    feedback_id: readString(feedback.feedback_id) ?? readString(feedback.id) ?? 'feedback-accepted',
    workspace_id: readString(feedback.workspace_id) ?? readString(raw.workspace_id) ?? workspaceId,
    accepted: accepted ?? true,
    message: readString(feedback.message) ?? readString(raw.message)
  };
}

function sourceCreateBody(input: CreateSourceRequest) {
  if (input.file) {
    const sourceType = input.file.source_type ?? input.source_type;
    return {
      files: [
        {
          title: input.title,
          file_name: input.file.file_name,
          content_base64: input.file.content_base64,
          content_type: input.file.content_type,
          source_type: sourceType,
          metadata: input.metadata ?? {}
        }
      ],
      metadata: input.metadata ?? {}
    };
  }
  if (input.url) {
    return {
      urls: [
        {
          title: input.title,
          url: input.url,
          metadata: input.metadata ?? {}
        }
      ],
      metadata: input.metadata ?? {}
    };
  }
  if (input.content) {
    const metadata = {
      ...(input.metadata ?? {}),
      source_type: input.source_type
    };
    return {
      texts: [
        {
          title: input.title,
          content: input.content,
          metadata
        }
      ],
      metadata: input.metadata ?? {}
    };
  }
  throw new DataServiceError({
    code: 'validation_error',
    message: 'Source creation requires a file, public URL, or text content.',
    status: 422,
    retryable: false,
    details: { title: input.title, source_type: input.source_type }
  });
}

function buildStartBody(input?: BuildStartRequest | SessionBuildStartRequest) {
  const mode = readString((input as Record<string, unknown> | undefined)?.mode);
  return mode ? { mode } : {};
}

function sessionIngestBody(input: SessionIngestRequest) {
  return {
    content: input.content,
    title: input.label ?? 'Session context',
    content_format: 'text',
    source_type: 'text'
  };
}

function feedbackBody(input: QualityFeedbackRequest) {
  return {
    target_type: input.target_type,
    target_id: input.evidence_key ?? input.session_id ?? input.source_id ?? input.target_type,
    action: input.rating === 'up' ? 'mark_helpful' : 'mark_issue',
    label: input.rating,
    reason: input.comment ?? '',
    metadata: {
      session_id: input.session_id,
      source_id: input.source_id,
      evidence_key: input.evidence_key
    }
  };
}

export function createDataServiceClient(options: ClientOptions = {}) {
  const baseUrl = options.baseUrl ?? defaultBaseUrl;
  const timeoutMs = options.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const fetchImpl = options.fetchImpl;

  async function request<T>(path: string, requestOptions: RequestOptions = {}): Promise<T> {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), timeoutMs);
    const signal = requestOptions.signal ?? controller.signal;

    try {
      const response = await (fetchImpl ?? fetch)(`${baseUrl}${path}`, {
        method: requestOptions.method ?? 'GET',
        headers: {
          'Content-Type': 'application/json'
        },
        body: requestOptions.body === undefined ? undefined : JSON.stringify(requestOptions.body),
        signal
      });

      const payload = await parseJson(response);
      if (!response.ok) {
        throw new DataServiceError((requestOptions.normalizeError ?? normalizeHttpError)(response.status, payload));
      }
      return payload as T;
    } catch (error) {
      throw new DataServiceError(normalizeUnknownError(error));
    } finally {
      window.clearTimeout(timeout);
    }
  }

  return {
    capabilities: {
      async get(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/capabilities`, {
          normalizeError: normalizeCapabilityHttpError
        });
        return extractCapabilityManifest(workspaceId, payload);
      }
    },
    guide: {
      async get(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/guide`);
        return extractNotebookGuide(payload);
      }
    },
    studio: {
      async createArtifact(workspaceId: string, input: StudioArtifactRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/studio/artifacts`, {
          method: 'POST',
          body: { artifact_type: input.artifact_type }
        });
        return extractStudioArtifact(payload);
      }
    },
    research: {
      async createReport(workspaceId: string, input: ResearchRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/research`, {
          method: 'POST',
          body: { question: input.question, top_k: input.top_k }
        });
        return extractResearchReport(payload);
      }
    },
    workspaces: {
      async list() {
        const payload = await request<unknown>('/api/workspaces');
        return extractWorkspaceList(payload);
      },
      async create(input: CreateWorkspaceRequest) {
        const payload = await request<unknown>('/api/workspaces', {
          method: 'POST',
          body: { name: input.name }
        });
        return extractCreateWorkspace(payload);
      },
      async rename(workspaceId: string, input: RenameWorkspaceRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/rename`, {
          method: 'POST',
          body: { name: input.name }
        });
        return extractWorkspaceRename(payload);
      },
      async get(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}`);
        return extractWorkspace(payload);
      },
      async archive(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
          method: 'POST',
          body: {}
        });
        return extractArchiveResult(workspaceId, payload);
      }
    },
    sources: {
      async list(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
        return extractSourceList(workspaceId, payload);
      },
      async create(workspaceId: string, input: CreateSourceRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
          method: 'POST',
          body: sourceCreateBody(input)
        });
        return extractCreateSource(workspaceId, payload);
      },
      async get(workspaceId: string, sourceId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}`
        );
        return extractSource(workspaceId, payload);
      },
      async remove(workspaceId: string, sourceId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/remove`,
          {
            method: 'POST',
            body: {}
          }
        );
        return extractSource(workspaceId, payload);
      },
      async rename(workspaceId: string, sourceId: string, input: RenameSourceRequest) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/rename`,
          {
            method: 'POST',
            body: { title: input.title }
          }
        );
        return extractSourceMutation(workspaceId, payload);
      },
      async trace(workspaceId: string, sourceId: string) {
        assertPreviewSourceId(sourceId);
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/trace`
        );
        return extractSourceTrace(sourceId, payload);
      },
      async preview(workspaceId: string, sourceId: string, input?: SourcePreviewRequest): Promise<SourcePreviewResponse> {
        assertPreviewSourceId(sourceId);
        const query = input?.limit ? `?limit=${encodeURIComponent(String(input.limit))}` : '';
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/preview${query}`
        );
        return extractSourcePreview(sourceId, payload);
      },
      async listUnits(workspaceId: string, sourceId: string, input?: DocumentUnitListRequest): Promise<DocumentUnitListResponse> {
        assertDocumentUnitRouteIds(sourceId);
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units${documentUnitListQuery(input)}`
        );
        return extractDocumentUnitList(sourceId, payload);
      },
      async search(workspaceId: string, query: string, typeFilter?: string, limit = 20): Promise<{ sources: SourceSummary[]; total: number; query: string }> {
        const params = new globalThis.URLSearchParams({ q: query });
        if (typeFilter) params.set('type_filter', typeFilter);
        params.set('limit', String(limit));
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/search?${params.toString()}`
        );
        const body = unwrapData(payload);
        const raw = asRecord(body);
        const sourcesRaw = Array.isArray(raw?.sources) ? raw.sources : [];
        return {
          sources: sourcesRaw.map((s: unknown) => assertSourceSummary(s, workspaceId)).filter((s: SourceSummary) => s.source_id),
          total: readNumber(raw?.total) ?? sourcesRaw.length,
          query: readString(raw?.query) ?? query
        };
      },
      async getUnit(workspaceId: string, sourceId: string, unitId: string): Promise<DocumentUnit> {
        assertDocumentUnitRouteIds(sourceId, unitId);
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units/${encodeURIComponent(unitId)}`
        );
        const body = unwrapData(payload);
        const raw = asRecord(body);
        return assertDocumentUnit(asRecord(raw?.unit) ?? raw, sourceId);
      },
      async getEvidenceSpan(workspaceId: string, sourceId: string, unitId: string, evidenceId: string): Promise<EvidenceSpan> {
        assertEvidenceSpanRouteIds(sourceId, unitId, evidenceId);
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units/${encodeURIComponent(
            unitId
          )}/evidence/${encodeURIComponent(evidenceId)}`
        );
        const body = unwrapData(payload);
        const raw = asRecord(body);
        return assertEvidenceSpan(asRecord(raw?.evidence_span) ?? raw, sourceId, unitId, evidenceId);
      },
      async navigateEvidence(
        _workspaceId: string,
        _sourceId: string,
        input: { unit_id?: string; evidence_id?: string }
      ): Promise<EvidenceNavigationResponse> {
        if (input.evidence_id || input.unit_id) {
          throw capabilityMissingError('Evidence navigation route is not declared by the data_service capability manifest.');
        }
        return { fallback: 'source' };
      }
    },
    build: {
      async start(workspaceId: string, input?: BuildStartRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
          method: 'POST',
          body: buildStartBody(input)
        });
        return extractBuildStart(payload);
      },
      async getOperation(workspaceId: string, operationId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`
        );
        return extractBuildOperation(operationId, payload);
      },
      async cancel(workspaceId: string, operationId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}/cancel`,
          {
            method: 'POST',
            body: {}
          }
        );
        return extractBuildOperation(operationId, payload);
      }
    },
    query: {
      async workspace(workspaceId: string, input: QueryRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
          method: 'POST',
          body: { query: input.question }
        });
        return extractQueryResponse(payload, input.registrySourceIds);
      }
    },
    agentWorkflows: {
      async createDraft(workspaceId: string, input: AgentWorkflowDraftRequest): Promise<AgentWorkflowDraftResponse> {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/agent-workflows/draft`, {
          method: 'POST',
          body: { user_goal: input.user_goal }
        });
        return extractAgentWorkflowDraftResponse(workspaceId, payload);
      },
      async getDraft(workspaceId: string, taskId: string): Promise<AgentWorkflowDraftResponse> {
        void workspaceId;
        void taskId;
        throw agentWorkflowContractMissing();
      },
      async startRun(workspaceId: string, workflowId: string): Promise<never> {
        void workspaceId;
        void workflowId;
        throw agentWorkflowContractMissing();
      }
    },
    folderCollections: {
      async scan(workspaceId: string, input: FolderScanRequest): Promise<FolderScanResponse> {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/folder-collections/scan`, {
          method: 'POST',
          body: {
            authorized_root: input.authorized_root,
            permission_grant_id: input.permission_grant_id,
            dry_run: true,
            recursive: input.recursive ?? true,
            include_extensions: input.include_extensions ?? ['.md', '.txt'],
            exclude_globs: input.exclude_globs ?? [],
            max_depth: input.max_depth,
            max_file_size_bytes: input.max_file_size_bytes,
            follow_symlinks: false
          }
        });
        return extractFolderScanResponse(workspaceId, payload);
      }
    },
    folderSummaryWorkflows: {
      async startRun(workspaceId: string, input: FolderSummaryWorkflowRunRequest): Promise<FolderSummaryWorkflowRunResponse> {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflows/folder-summary/runs`, {
          method: 'POST',
          body: {
            authorized_root: input.authorized_root,
            permission_grant_id: input.permission_grant_id,
            dry_run: input.dry_run,
            confirm_extract: input.confirm_extract ?? false,
            recursive: input.recursive ?? true,
            include_extensions: input.include_extensions ?? ['.md', '.txt'],
            exclude_globs: input.exclude_globs ?? [],
            max_depth: input.max_depth,
            max_file_size_bytes: input.max_file_size_bytes,
            follow_symlinks: false
          }
        });
        return extractFolderSummaryWorkflowRunResponse(workspaceId, payload);
      }
    },
    sessions: {
      async list(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions`);
        return extractSessionList(workspaceId, payload);
      },
      async create(workspaceId: string, input: CreateSessionRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions`, {
          method: 'POST',
          body: input
        });
        return extractCreateSession(workspaceId, payload);
      },
      async get(workspaceId: string, sessionId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}`
        );
        return extractSession(workspaceId, payload);
      },
      async close(workspaceId: string, sessionId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/close`,
          {
            method: 'POST'
          }
        );
        return extractCloseSession(sessionId, payload);
      },
      async ingest(workspaceId: string, sessionId: string, input: SessionIngestRequest) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/ingest`,
          {
            method: 'POST',
            body: sessionIngestBody(input)
          }
        );
        return extractSessionIngest(workspaceId, payload);
      },
      build: {
        async start(workspaceId: string, sessionId: string, input?: SessionBuildStartRequest): Promise<SessionBuildStartResponse> {
          const payload = await request<unknown>(
            `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/start`,
            {
              method: 'POST',
              body: buildStartBody(input)
            }
          );
          return extractBuildStart(payload);
        },
        async getOperation(workspaceId: string, sessionId: string, operationId: string) {
          const payload = await request<unknown>(
            `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/operations/${encodeURIComponent(operationId)}`
          );
          return extractBuildOperation(operationId, payload);
        },
        async cancel(workspaceId: string, sessionId: string, operationId: string) {
          const payload = await request<unknown>(
            `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/operations/${encodeURIComponent(operationId)}/cancel`,
            {
              method: 'POST',
              body: {}
            }
          );
          return extractBuildOperation(operationId, payload);
        }
      },
      async query(workspaceId: string, sessionId: string, input: SessionQueryRequest): Promise<SessionQueryResponse> {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/query`,
          {
            method: 'POST',
            body: { query: input.question }
          }
        );
        return extractQueryResponse(payload, input.registrySourceIds);
      }
    },
    graph: {
      async neighbors(workspaceId: string, input: GraphNeighborsRequest) {
        const candidate = asRecord(input);
        const nodeId = readString(candidate?.nodeId);
        const entityId = readString(candidate?.entityId);
        if (!nodeId && !entityId) {
          throw new DataServiceError({
            code: 'validation_error',
            message: 'Graph neighbors requires nodeId or entityId.',
            retryable: false
          });
        }
        const query = nodeId ? `node_id=${encodeURIComponent(nodeId)}` : `entity_id=${encodeURIComponent(entityId ?? '')}`;
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/neighbors?${query}`);
        return extractGraphNeighbors(workspaceId, payload);
      },
      async communities(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/community?include_members=true`);
        return extractGraphCommunities(workspaceId, payload);
      },
      async session(workspaceId: string, sessionId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/graph/session?session_id=${encodeURIComponent(sessionId)}`
        );
        return extractSessionGraph(workspaceId, sessionId, payload);
      }
    },
    quality: {
      async feedback(workspaceId: string, input: QualityFeedbackRequest) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/quality/feedback`, {
          method: 'POST',
          body: feedbackBody(input)
        });
        return extractQualityFeedback(workspaceId, payload);
      }
    }
  };
}

export const dataServiceClient = createDataServiceClient();
