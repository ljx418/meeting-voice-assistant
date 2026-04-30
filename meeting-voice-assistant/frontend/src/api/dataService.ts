import { API_CONFIG } from './config'

const BASE_URL = `${API_CONFIG.baseUrl}/api/v1/knowledge`

export type QueryMode = 'llmwiki' | 'graphrag' | 'hybrid'

export interface KnowledgeSummaryResponse {
  workspace: string
  summary_markdown: string
  summary_json: Record<string, any>
  quality: Record<string, any>
  quality_feedback: KnowledgeFeedbackRecord[]
  quality_correction_rules: KnowledgeCorrectionRule[]
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
  nodes: any[]
  edges: any[]
  communities: any[]
  stats: {
    entity_count: number
    relationship_count: number
    community_count: number
    document_count: number
  }
  db_path: string
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

async function postJson<T>(endpoint: string, body: Record<string, any>): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
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

export function fetchKnowledgeGraph(workspace: string, maxNodes = 120) {
  return postJson<KnowledgeGraphResponse>('/graph', { workspace, max_nodes: maxNodes })
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
