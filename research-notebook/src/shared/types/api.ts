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
};

export type AnswerEvidence = {
  evidenceKey: string;
  sourceId?: string;
  sourceTitle?: string;
  traceAvailable: boolean;
  artifactRefs?: string[];
  snippet?: string;
  confidence?: number;
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

export type GraphCommunity = {
  community_id: string;
  title: string;
  summary?: string;
  node_count?: number;
  relationship_count?: number;
  score?: number;
  artifact_refs?: string[];
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

export type NormalizedErrorCode =
  | 'backend_unavailable'
  | 'request_timeout'
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
