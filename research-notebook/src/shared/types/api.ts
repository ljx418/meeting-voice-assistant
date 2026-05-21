export type WorkspaceSummary = {
  workspace_id: string;
  name: string;
  description?: string;
  archived?: boolean;
  created_at?: string;
  updated_at?: string;
  source_count?: number;
};

export type WorkspaceDetail = WorkspaceSummary & {
  artifact_refs?: string[];
  metadata?: Record<string, unknown>;
};

export type CreateWorkspaceRequest = {
  name: string;
  description?: string;
};

export type CreateWorkspaceResponse = {
  workspace: WorkspaceDetail;
};

export type WorkspaceArchiveResult = {
  workspace_id: string;
  archived: boolean;
};

export type SourceSummary = {
  source_id: string;
  workspace_id: string;
  title: string;
  source_type?: string;
  import_state?: SourceImportState;
  build_state?: SourceBuildState;
  updated_at?: string;
  trace_available?: boolean;
  artifact_refs?: string[];
};

export type SourceImportState =
  | 'idle'
  | 'selecting'
  | 'uploading'
  | 'importing'
  | 'imported_not_built'
  | 'ready'
  | 'failed_import'
  | 'removed'
  | 'unsupported_type';

export type SourceBuildState =
  | 'idle'
  | 'imported_not_built'
  | 'building'
  | 'ready'
  | 'failed_build'
  | 'removed'
  | 'unsupported_type';

export type SourceDetail = SourceSummary & {
  description?: string;
  metadata?: Record<string, unknown>;
};

export type CreateSourceRequest = {
  title: string;
  content?: string;
  source_type?: string;
  metadata?: Record<string, unknown>;
};

export type CreateSourceResponse = {
  source: SourceDetail;
};

export type SourceTrace = {
  source_id: string;
  title?: string;
  artifact_refs?: string[];
  trace_available: boolean;
  provenance?: Array<{
    label: string;
    value: string;
  }>;
  summary?: string;
};

export type BuildOperationStatus =
  | 'queued'
  | 'running'
  | 'completed'
  | 'failed'
  | 'cancelled'
  | 'operation_unavailable';

export type BuildStartRequest = {
  reason?: string;
};

export type BuildStartResponse = {
  operation_id: string;
};

export type BuildOperation = {
  operation_id: string;
  status: BuildOperationStatus;
  cancellable: boolean;
  message?: string;
  started_at?: string;
  completed_at?: string;
};

export type QueryRequest = {
  question: string;
  registrySourceIds?: string[];
};

export type TraceUnavailableReason = 'missing_source_id' | 'source_ref_not_traceable' | 'trace_route_failed';

export type SourcePreviewLocator = {
  pageNo?: number;
  slideNo?: number;
  timestampStartMs?: number;
  timestampEndMs?: number;
  jsonPath?: string;
};

export type AnswerEvidence = {
  evidenceKey: string;
  // Only registry source_id values that can be sent to sources.trace.
  sourceId?: string;
  // Backend hit/page/slug/source ref that is display-only unless resolved to sourceId.
  sourceRef?: string;
  sourceTitle?: string;
  traceAvailable: boolean;
  artifactRefs?: string[];
  snippet?: string;
  confidence?: number;
  traceUnavailableReason?: TraceUnavailableReason;
  unitId?: string;
  evidenceId?: string;
  locator?: SourcePreviewLocator;
  previewAvailable?: boolean;
};

export type QueryResponse = {
  answer: string;
  evidence: AnswerEvidence[];
  noEvidence: boolean;
};

export type SessionState =
  | 'idle'
  | 'creating'
  | 'active'
  | 'ingesting'
  | 'ingested_not_built'
  | 'building'
  | 'ready'
  | 'failed_ingest'
  | 'failed_build'
  | 'closed';

export type SessionSummary = {
  session_id: string;
  workspace_id: string;
  title: string;
  state: SessionState;
  created_at?: string;
  updated_at?: string;
  closed_at?: string;
};

export type SessionDetail = SessionSummary & {
  context_summary?: string;
  artifact_refs?: string[];
  source_ids?: string[];
  last_answer?: QueryResponse;
  metadata?: Record<string, unknown>;
};

export type CreateSessionRequest = {
  title: string;
};

export type CreateSessionResponse = {
  session: SessionDetail;
};

export type CloseSessionResponse = {
  session_id: string;
  closed: boolean;
};

export type SessionIngestRequest = {
  content: string;
  label?: string;
};

export type SessionIngestResponse = {
  session: SessionDetail;
};

export type SessionBuildStartRequest = {
  reason?: string;
};

export type SessionBuildStartResponse = BuildStartResponse;

export type SessionQueryRequest = QueryRequest;

export type SessionQueryResponse = QueryResponse;

export type GraphNode = {
  node_id: string;
  entity_id?: string;
  label: string;
  node_type?: string;
  weight?: number;
  source_ids?: string[];
  artifact_refs?: string[];
};

export type GraphEdge = {
  edge_id: string;
  source_node_id: string;
  target_node_id: string;
  label?: string;
  weight?: number;
};

export type GraphNeighbor = GraphNode & {
  relationship?: string;
};

export type GraphNeighborsResponse = {
  workspace_id: string;
  status: 'ready' | 'missing_artifact' | 'unavailable';
  nodes: GraphNode[];
  edges: GraphEdge[];
  neighbors: GraphNeighbor[];
  artifact_refs?: string[];
  summary?: string;
};

export type GraphNeighborsRequest =
  | {
      nodeId: string;
      entityId?: never;
    }
  | {
      entityId: string;
      nodeId?: never;
    };

export type GraphCommunity = {
  community_id: string;
  title: string;
  summary?: string;
  node_count?: number;
  relationship_count?: number;
  score?: number;
  artifact_refs?: string[];
  members?: GraphNode[];
};

export type GraphCommunitiesResponse = {
  workspace_id: string;
  status: 'ready' | 'missing_artifact' | 'unavailable';
  communities: GraphCommunity[];
  artifact_refs?: string[];
  summary?: string;
};

export type SessionGraphContextResponse = {
  workspace_id: string;
  session_id: string;
  status: 'ready' | 'missing_artifact' | 'unavailable';
  related_nodes: GraphNode[];
  related_communities: GraphCommunity[];
  artifact_refs?: string[];
  summary?: string;
};

export type QualityFeedbackRequest = {
  target_type: 'workspace_answer' | 'session_answer' | 'source' | 'graph_context';
  rating: 'up' | 'down';
  comment?: string;
  session_id?: string;
  source_id?: string;
  evidence_key?: string;
};

export type QualityFeedbackResponse = {
  feedback_id: string;
  workspace_id: string;
  accepted: boolean;
  message?: string;
};

export type PreviewDepth = 'none' | 'source' | 'unit' | 'span';

export type CapabilityManifest = {
  workspace_id?: string;
  service_version?: string;
  schema_version?: string;
  generated_at?: string;
  capabilities: {
    source_preview: boolean;
    document_units: boolean;
    evidence_spans: boolean;
    source_level_preview: boolean;
    unit_level_navigation: boolean;
    precise_span_highlight: boolean;
    citation_backjump: boolean;
  };
  supported_source_types: Array<{
    source_type: string;
    preview: PreviewDepth;
    locators: Array<'page_no' | 'slide_no' | 'timestamp' | 'json_path' | 'offset'>;
  }>;
};

export type DocumentUnit = {
  unit_id: string;
  source_id: string;
  unit_type: 'text' | 'page' | 'slide' | 'section' | 'transcript_segment' | 'json_node';
  title?: string;
  text_preview?: string;
  content_type?: 'text/plain' | 'text/markdown' | 'text/html';
  order_index?: number;
  page_no?: number;
  slide_no?: number;
  timestamp_start_ms?: number;
  timestamp_end_ms?: number;
  json_path?: string;
  artifact_ref?: string;
  preview_available?: boolean;
  preview_truncated?: boolean;
  preview_size_bytes?: number;
  max_preview_size_bytes?: number;
};

export type DocumentUnitListRequest = {
  limit?: number;
  cursor?: string;
};

export type DocumentUnitListResponse = {
  source_id: string;
  items: DocumentUnit[];
  next_cursor?: string | null;
  limit: number;
  has_more: boolean;
  unsupported_reason?: string;
};

export type EvidenceSpan = {
  evidence_id: string;
  source_id: string;
  unit_id?: string;
  start_offset?: number;
  end_offset?: number;
  offset_basis?: 'utf8_bytes' | 'unicode_codepoints' | 'utf16_code_units' | 'normalized_text';
  offset_range?: 'half_open' | 'closed';
  text_basis?: 'document_unit_text' | 'normalized_source_text';
  snippet?: string;
  locator?: {
    page_no?: number;
    slide_no?: number;
    timestamp_start_ms?: number;
    timestamp_end_ms?: number;
    json_path?: string;
  };
  preview_available?: boolean;
};

export type SourcePreviewRequest = {
  unit_id?: string;
  evidence_id?: string;
  limit?: number;
  cursor?: string;
};

export type SourcePreview = {
  source_id: string;
  title?: string;
  source_type?: string;
  preview_available: boolean;
  content_type?: 'text/plain' | 'text/markdown' | 'text/html';
  text_preview?: string;
  units?: DocumentUnit[];
  next_cursor?: string;
  artifact_refs?: string[];
  unsupported_reason?: string;
  preview_truncated?: boolean;
  preview_size_bytes?: number;
  max_preview_size_bytes?: number;
};

export type SourcePreviewResponse = {
  preview: SourcePreview;
};

export type EvidenceNavigationRequest = {
  unit_id?: string;
  evidence_id?: string;
};

export type EvidenceNavigationResponse = {
  unit?: DocumentUnit;
  evidence_span?: EvidenceSpan;
  fallback: 'span' | 'unit' | 'source' | 'unavailable';
};

export type NormalizedErrorCode =
  | 'backend_unavailable'
  | 'request_timeout'
  | 'capability_missing'
  | 'missing_graph_artifact'
  | 'not_found'
  | 'validation_error'
  | 'conflict'
  | 'version_or_schema_mismatch'
  | 'unknown_service_error';

export type NormalizedErrorEnvelope = {
  code: NormalizedErrorCode;
  message: string;
  status?: number;
  retryable: boolean;
  details?: unknown;
};
