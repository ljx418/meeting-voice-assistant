import type {
  AnswerEvidence,
  BuildOperation,
  BuildStartRequest,
  BuildStartResponse,
  CreateWorkspaceRequest,
  CreateWorkspaceResponse,
  CreateSourceRequest,
  CreateSourceResponse,
  GraphCommunitiesResponse,
  GraphCommunity,
  GraphEdge,
  GraphNeighbor,
  GraphNeighborsResponse,
  GraphNode,
  NormalizedErrorCode,
  NormalizedErrorEnvelope,
  QualityFeedbackRequest,
  QualityFeedbackResponse,
  QueryRequest,
  QueryResponse,
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
  SourceBuildState,
  SourceDetail,
  SourceImportState,
  SourceSummary,
  SourceTrace,
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
};

const DEFAULT_TIMEOUT_MS = 12_000;

const defaultBaseUrl = import.meta.env.VITE_DATA_SERVICE_BASE_URL ?? '';

function normalizeStatusCode(status: number): NormalizedErrorCode {
  if (status === 404) return 'not_found';
  if (status === 400 || status === 422) return 'validation_error';
  if (status === 409) return 'conflict';
  if (status === 412 || status === 426) return 'version_or_schema_mismatch';
  return 'unknown_service_error';
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
    trace_available: readBoolean(source.trace_available) ?? Boolean(source.trace || source.provenance),
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

  return {
    source_id: readString(wrapped.source_id) ?? readString(source?.source_id) ?? sourceId,
    title: readString(wrapped.title) ?? readString(wrapped.name) ?? readString(traceSummary?.source_title) ?? readString(source?.title),
    artifact_refs: readArtifactRefs(wrapped.artifact_refs),
    trace_available: readBoolean(wrapped.trace_available) ?? true,
    provenance,
    summary: readString(wrapped.summary) ?? readString(traceSummary?.source_title)
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

function normalizeEvidence(rawEvidence: unknown, index: number): AnswerEvidence {
  if (!rawEvidence || typeof rawEvidence !== 'object') {
    return {
      evidenceKey: `evidence-${index}`,
      traceAvailable: false,
      snippet: typeof rawEvidence === 'string' ? rawEvidence : undefined
    };
  }

  const evidence = rawEvidence as Record<string, unknown>;
  const sourceId = readString(evidence.source_id) ?? readString(evidence.sourceId) ?? readString(evidence.source);
  const artifactRefs = readArtifactRefs(evidence.artifact_refs) ?? readArtifactRefs(evidence.artifactRefs) ?? readArtifactRefs(evidence.source_refs);
  const traceAvailable = readBoolean(evidence.trace_available) ?? readBoolean(evidence.traceAvailable) ?? Boolean(sourceId);
  return {
    evidenceKey: readString(evidence.evidence_key) ?? readString(evidence.evidenceKey) ?? `${sourceId ?? 'artifact'}-${index}`,
    sourceId,
    sourceTitle: readString(evidence.source_title) ?? readString(evidence.sourceTitle) ?? readString(evidence.title),
    traceAvailable,
    artifactRefs,
    snippet: readString(evidence.snippet) ?? readString(evidence.text),
    confidence: readNumber(evidence.confidence) ?? readNumber(evidence.score)
  };
}

function extractQueryResponse(payload: unknown): QueryResponse {
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
  const evidence = rawEvidence.map(normalizeEvidence);
  const usefulEvidence = evidence.filter((item) => item.sourceId || (item.artifactRefs && item.artifactRefs.length > 0));
  return {
    answer,
    evidence: usefulEvidence,
    noEvidence: usefulEvidence.length === 0
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
    artifact_refs: readStringArray(community.artifact_refs)
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
  if (input.content) {
    return {
      texts: [
        {
          title: input.title,
          content: input.content,
          metadata: input.metadata ?? {}
        }
      ],
      metadata: input.metadata ?? {}
    };
  }
  return {
    texts: [],
    metadata: {
      ...(input.metadata ?? {}),
      title: input.title,
      source_type: input.source_type
    }
  };
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
        throw new DataServiceError(normalizeHttpError(response.status, payload));
      }
      return payload as T;
    } catch (error) {
      throw new DataServiceError(normalizeUnknownError(error));
    } finally {
      window.clearTimeout(timeout);
    }
  }

  return {
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
      async trace(workspaceId: string, sourceId: string) {
        const payload = await request<unknown>(
          `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/trace`
        );
        return extractSourceTrace(sourceId, payload);
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
        return extractQueryResponse(payload);
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
        return extractQueryResponse(payload);
      }
    },
    graph: {
      async neighbors(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/neighbors`);
        return extractGraphNeighbors(workspaceId, payload);
      },
      async communities(workspaceId: string) {
        const payload = await request<unknown>(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/community`);
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
