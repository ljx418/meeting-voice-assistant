const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
const BASE_URL = `${API_BASE_URL}/api/v1/knowledge`
const KNOWLEDGE_API_KEY = import.meta.env.VITE_DATA_SERVICE_API_KEY || ''

export type QueryMode = 'llmwiki' | 'graphrag' | 'hybrid'

export interface KnowledgeSummaryResponse {
  workspace: string
  summary_markdown: string
  summary_json: Record<string, any>
  quality: Record<string, any>
  quality_feedback: KnowledgeFeedbackRecord[]
  quality_correction_rules: KnowledgeCorrectionRule[]
  quality_correction_plan?: KnowledgeCorrectionPlan
  llmwiki_pages: Array<{
    slug: string
    title: string
    path: string
    updated_at: number
  }>
  graph_stats: {
    entity_count: number
    relationship_count: number
    community_count: number
    document_count: number
  }
  graph_preview: {
    communities: any[]
    nodes: any[]
    edges: any[]
  }
}

export interface KnowledgeGraphResponse {
  scope?: string
  session_id?: string
  workspace_id?: string
  status?: string
  nodes: any[]
  edges: any[]
  communities: any[]
  stats: {
    entity_count: number
    relationship_count: number
    community_count: number
    document_count: number
    node_count?: number
    edge_count?: number
    source_count?: number
  }
  db_path: string
  quality_plan?: Record<string, any>
  quality_diagnostics?: Record<string, any>
}

export interface KnowledgeQueryResponse {
  mode: QueryMode
  query: string
  answer: string
  hits: Array<{
    title: string
    snippet: string
    source: string
    score: number
    meta: Record<string, any>
  }>
  engine_payloads: Record<string, any>
}

export interface KnowledgePageResponse {
  page: Record<string, any> | null
  sources: Record<string, any>[]
  citations: Record<string, any>[]
  backlinks: Record<string, any>[]
}

export interface KnowledgeDistillResponse {
  workspace: string
  schema_version: string
  manifest: Record<string, any>
  schema: Record<string, any>
  sources: Array<Record<string, any>>
  source: Record<string, any> | null
  units: Array<Record<string, any>>
  available_source_count: number
}

export interface KnowledgeSourceTraceResponse {
  workspace: string
  source_id: string
  source: Record<string, any>
  distill: {
    units: Array<Record<string, any>>
    unit_count: number
    provenance_summary?: Record<string, any>
    profile_debug?: Record<string, any>
  }
  llmwiki: {
    pages: Array<Record<string, any>>
    page_count: number
  }
  graphrag: {
    nodes: Array<Record<string, any>>
    edges: Array<Record<string, any>>
    communities: Array<Record<string, any>>
    node_count: number
    edge_count: number
    community_count: number
    graph_model_version?: string
  }
  trace_summary: Record<string, any>
}

export interface KnowledgeDirectoryScan {
  workspace: string
  scanned_at: string
  roots: string[]
  supported_suffixes: string[]
  limit: number
  truncated: boolean
  summary: {
    current_file_count: number
    new_count: number
    modified_count: number
    deleted_count: number
    unchanged_count: number
    unreadable_count: number
    pending_count: number
  }
  changes: {
    new: Array<Record<string, any>>
    modified: Array<Record<string, any>>
    deleted: Array<Record<string, any>>
    unreadable: Array<Record<string, any>>
  }
  files?: Record<string, Record<string, any>>
}

export interface KnowledgeLowSignalAuditResponse {
  workspace: string
  audited_at: string
  overall_status: string
  checks: Array<{
    check_id: string
    label: string
    status: string
    actual: number
    expected: number
    allowed_kinds?: string[]
  }>
  metrics: Record<string, any>
  samples: {
    title_derived?: Array<Record<string, any>>
    disallowed_title_derived?: Array<Record<string, any>>
    llmwiki_title_leaks?: Array<Record<string, any>>
    graphrag_title_leaks?: Array<Record<string, any>>
  }
  recommendations: string[]
}

export interface KnowledgeFeedbackRecord {
  feedback_id: string
  created_at: string
  workspace: string
  target_type: string
  target_id: string
  action: string
  label: string
  suggested_value: string
  reason: string
  metadata: Record<string, any>
}

export interface KnowledgeFeedbackResponse {
  workspace: string
  feedback_path?: string
  items?: KnowledgeFeedbackRecord[]
  total_count?: number
  filtered_count?: number
  summary: Record<string, any>
  feedback?: KnowledgeFeedbackRecord
}

export interface KnowledgeCorrectionRule {
  rule_id: string
  rule_type: string
  status: string
  target_type: string
  target_id: string
  current_label: string
  proposed_value: string
  reason: string
  source_feedback_id: string
  created_at: string
  reviewer?: string
  reviewed_at?: string
  review_note?: string
  metadata: Record<string, any>
}

export interface KnowledgeCorrectionRulesResponse {
  workspace: string
  rules_path?: string
  items?: KnowledgeCorrectionRule[]
  rules?: KnowledgeCorrectionRule[]
  total_count?: number
  filtered_count?: number
  summary: Record<string, any>
  generated_at?: string
  schema_version?: string
}

export interface KnowledgeCorrectionPlan {
  schema_version: string
  workspace: string
  generated_at: string
  source_rule_count: number
  actions: Array<Record<string, any>>
  summary: Record<string, any>
  notes?: string[]
}

export interface KnowledgeCorrectionReviewResponse {
  workspace: string
  rules_path?: string
  rule: KnowledgeCorrectionRule
  summary: Record<string, any>
  correction_plan?: KnowledgeCorrectionPlan
}

export interface KnowledgeLifecycleEnvelope<T = Record<string, any>> {
  workspace_id: string
  operation_id: string | null
  status: string
  warnings: string[]
  artifact_refs: Array<Record<string, any>>
  next_actions: string[]
  data: T
}

export interface KnowledgeBuildOperation {
  mode?: string
  stage?: string
  progress?: number
  started_at?: string | null
  completed_at?: string | null
  created_at?: string
  updated_at?: string
  error?: Record<string, any> | null
  retryable?: boolean
  artifacts?: Array<string | Record<string, any>>
  results?: Array<Record<string, any>>
}

export interface KnowledgeWorkspaceRecord {
  workspace_id: string
  name: string
  workspace_path: string
  status: string
  updated_at?: string
  created_at?: string
  tags?: string[]
  bound_paths?: string[]
}

export interface KnowledgeSourceRecord {
  source_id: string
  sha256?: string | null
  title: string
  status: string
  ingest_status?: string
  low_signal?: Record<string, any>
  path?: string
  original_path?: string
  imported_at?: string
  ingest_updated_at?: string
  unit_count?: number
  source_weight?: number
  source_density_score?: number
  source_format?: string
  extractor_name?: string
  extractor_available?: boolean
}

async function postJson<T>(endpoint: string, body: Record<string, any>): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (KNOWLEDGE_API_KEY) {
    headers['X-API-Key'] = KNOWLEDGE_API_KEY
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  return response.json() as Promise<T>
}

export function fetchKnowledgeSummary(workspace: string) {
  return postJson<KnowledgeSummaryResponse>('/summary', { workspace })
}

export function createKnowledgeWorkspace(payload: {
  name: string
  root?: string
  owner?: string
  tags?: string[]
  bound_paths?: string[]
}) {
  return postJson<KnowledgeLifecycleEnvelope<{ workspace: KnowledgeWorkspaceRecord }>>('/workspaces/create', payload)
}

export function listKnowledgeWorkspaces(options: { root?: string; limit?: number; owner?: string; tag?: string } = {}) {
  return postJson<KnowledgeLifecycleEnvelope<{ items: KnowledgeWorkspaceRecord[] }>>('/workspaces/list', {
    root: options.root || undefined,
    limit: options.limit || 50,
    owner: options.owner || '',
    tag: options.tag || '',
  })
}

export function describeKnowledgeWorkspace(payload: { workspace?: string; workspace_id?: string }) {
  return postJson<KnowledgeLifecycleEnvelope<{
    workspace: KnowledgeWorkspaceRecord
    source_summary: Record<string, any>
    summary: Record<string, any>
    engines: Record<string, any>
    quality: Record<string, any>
  }>>('/workspaces/describe', payload)
}

export function importKnowledgeSources(workspace: string, paths: string[], metadata: Record<string, any> = {}) {
  return postJson<KnowledgeLifecycleEnvelope<{ sources: KnowledgeSourceRecord[] }>>('/sources/import', {
    workspace,
    paths,
    metadata,
  })
}

export function listKnowledgeSources(workspace: string, options: { limit?: number; status?: string } = {}) {
  return postJson<KnowledgeLifecycleEnvelope<{ items: KnowledgeSourceRecord[] }>>('/sources/list', {
    workspace,
    limit: options.limit || 100,
    status: options.status || undefined,
  })
}

export function removeKnowledgeSource(workspace: string, sourceId: string, reason = '') {
  return postJson<KnowledgeLifecycleEnvelope<{ source: KnowledgeSourceRecord }>>('/sources/remove', {
    workspace,
    source_id: sourceId,
    reason,
  })
}

export function startKnowledgeBuild(workspace: string, mode = 'full', paths: string[] = []) {
  return postJson<KnowledgeLifecycleEnvelope<KnowledgeBuildOperation>>('/build/start', {
    workspace,
    mode,
    paths,
  })
}

export function fetchKnowledgeBuildStatus(workspace: string, operationId: string) {
  return postJson<KnowledgeLifecycleEnvelope<KnowledgeBuildOperation>>('/build/status', {
    workspace,
    operation_id: operationId,
  })
}

export function cancelKnowledgeBuild(workspace: string, operationId: string, reason = '') {
  return postJson<KnowledgeLifecycleEnvelope<KnowledgeBuildOperation>>('/build/cancel', {
    workspace,
    operation_id: operationId,
    reason,
  })
}

export function fetchKnowledgeGraph(workspace: string, maxNodes = 120) {
  return postJson<KnowledgeGraphResponse>('/graph', { workspace, max_nodes: maxNodes })
}

export function fetchKnowledgeSessionGraph(workspaceId: string, sessionId: string, maxNodes = 160) {
  return postJson<KnowledgeGraphResponse>('/graph', {
    workspace_id: workspaceId,
    session_id: sessionId,
    scope: 'session',
    max_nodes: maxNodes,
  })
}

export function queryKnowledge(workspace: string, query: string, mode: QueryMode, topK = 8) {
  return postJson<KnowledgeQueryResponse>('/query', {
    workspace,
    query,
    mode,
    top_k: topK,
  })
}

export function fetchKnowledgePage(workspace: string, slug: string) {
  return postJson<KnowledgePageResponse>('/page', { workspace, slug })
}

export function fetchKnowledgeDistill(workspace: string, sourceId?: string | null, limit = 20) {
  return postJson<KnowledgeDistillResponse>('/distill', {
    workspace,
    source_id: sourceId || undefined,
    limit,
  })
}

export function fetchKnowledgeSourceTrace(workspace: string, sourceId: string, limit = 12) {
  return postJson<KnowledgeSourceTraceResponse>('/source/trace', {
    workspace,
    source_id: sourceId,
    limit,
  })
}

export function fetchKnowledgeLowSignalAudit(workspace: string, limit = 30) {
  return postJson<KnowledgeLowSignalAuditResponse>('/quality/low-signal-audit', {
    workspace,
    limit,
  })
}

export function scanKnowledgeDirectories(workspace: string, paths: string[] = [], options: { persist?: boolean; limit?: number } = {}) {
  return postJson<KnowledgeLifecycleEnvelope<KnowledgeDirectoryScan>>('/directories/scan', {
    workspace,
    paths,
    persist: options.persist ?? true,
    limit: options.limit || 500,
  })
}

export function ingestKnowledge(workspace: string, paths: string[]) {
  return postJson<{
    workspace: string
    summary: string
    results: Array<{ engine: string; status: string; meta: Record<string, any> }>
  }>('/ingest', { workspace, paths })
}

export function resetKnowledgeWorkspace(workspace: string, confirmation: string) {
  return postJson<{
    workspace: string
    removed: string[]
    row_preserved: boolean
  }>('/reset', { workspace, confirmation })
}

export function submitKnowledgeFeedback(
  workspace: string,
  payload: {
    target_type: string
    target_id: string
    action: string
    label?: string
    suggested_value?: string
    reason?: string
    metadata?: Record<string, any>
  },
) {
  return postJson<KnowledgeFeedbackResponse>('/quality/feedback', { workspace, ...payload })
}

export function fetchKnowledgeFeedback(
  workspace: string,
  options: { limit?: number; target_type?: string; target_id?: string } = {},
) {
  return postJson<KnowledgeFeedbackResponse>('/quality/feedback/list', {
    workspace,
    limit: options.limit || 100,
    target_type: options.target_type || undefined,
    target_id: options.target_id || undefined,
  })
}

export function fetchKnowledgeCorrectionRules(
  workspace: string,
  options: { limit?: number; status?: string } = {},
) {
  return postJson<KnowledgeCorrectionRulesResponse>('/quality/corrections', {
    workspace,
    limit: options.limit || 100,
    status: options.status || undefined,
  })
}

export function buildKnowledgeCorrectionRules(workspace: string) {
  return postJson<KnowledgeCorrectionRulesResponse>('/quality/corrections/build', { workspace })
}

export function reviewKnowledgeCorrectionRule(
  workspace: string,
  payload: { rule_id: string; status: string; reviewer?: string; note?: string },
) {
  return postJson<KnowledgeCorrectionReviewResponse>('/quality/corrections/review', { workspace, ...payload })
}

export function buildKnowledgeCorrectionPlan(workspace: string) {
  return postJson<KnowledgeCorrectionPlan>('/quality/corrections/plan', { workspace })
}
