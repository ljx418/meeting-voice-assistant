/**
 * Wiki API 客户端
 * 基于 ADR-002 设计的 Wiki 生成系统
 */

import { API_CONFIG } from './config'

export enum DocType {
  MEETING_SUMMARY = "meeting_summary",
  MEETING_NOTES = "meeting_notes",
  CHAPTER = "chapter",
  PAGE = "page",
  TEMPLATE = "template",
}

export interface WikiDocument {
  id: string
  title: string
  content: string
  doc_type: DocType
  parent_id?: string
  meeting_id?: string
  tags: string[]
  version: number
  is_deleted: boolean
  created_at: string
  updated_at: string
  created_by?: string
}

export interface WikiDocumentCreate {
  title: string
  content: string
  doc_type: DocType
  parent_id?: string
  meeting_id?: string
  tags?: string[]
}

export interface WikiDocumentUpdate {
  title?: string
  content?: string
  tags?: string[]
  parent_id?: string
  change_summary?: string
}

export interface WikiDocumentVersion {
  id: string
  document_id: string
  version: number
  title: string
  content: string
  change_summary?: string
  created_at: string
  created_by?: string
}

export interface WikiTemplate {
  id: string
  name: string
  description?: string
  doc_type?: DocType | string
  content?: string
  tags?: string[]
}

export interface WikiSearchResult {
  id: string
  title: string
  snippet: string
  doc_type: DocType
  tags: string[]
  updated_at: string
}

export interface WikiEntity {
  id: string
  name: string
  type: string
  description?: string
  source_doc_id?: string
}

export interface WikiRelationship {
  id: string
  source: string
  target: string
  relationship_type: string
  description?: string
  source_doc_id?: string
}

export interface WikiWorkflow {
  id: string
  name: string
  description?: string
  steps: Array<{
    order: number
    name: string
    description?: string
    status: string
  }>
  created_at: string
}

export interface WikiLongTermTask {
  id: string
  title: string
  description?: string
  assignee?: string
  due_date?: string
  status: 'pending' | 'in_progress' | 'completed'
  source_doc_id?: string
  created_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
}

export interface APIResponse<T = any> {
  success: boolean
  data?: T
  message?: string
}

export interface WikiIndexResponse {
  success: boolean
  document_id: string
  entities_count: number
  relationships_count: number
  message: string
}

const BASE_URL = API_CONFIG.baseUrl

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }

  return response.json()
}

// ============ 文档管理 ============

export async function createDocument(doc: WikiDocumentCreate): Promise<APIResponse> {
  return fetchApi<APIResponse>('/api/v1/wiki/pages', {
    method: 'POST',
    body: JSON.stringify(doc),
  })
}

export async function listDocuments(params?: {
  doc_type?: string
  meeting_id?: string
  parent_id?: string
  tags?: string
  page?: number
  size?: number
}): Promise<PaginatedResponse<WikiDocument>> {
  const searchParams = new URLSearchParams()
  if (params?.doc_type) searchParams.set('doc_type', params.doc_type)
  if (params?.meeting_id) searchParams.set('meeting_id', params.meeting_id)
  if (params?.parent_id) searchParams.set('parent_id', params.parent_id)
  if (params?.tags) searchParams.set('tags', params.tags)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.size) searchParams.set('size', String(params.size))

  const query = searchParams.toString()
  return fetchApi<PaginatedResponse<WikiDocument>>(`/api/v1/wiki/pages${query ? `?${query}` : ''}`)
}

export async function getDocument(docId: string): Promise<APIResponse<WikiDocument>> {
  return fetchApi<APIResponse<WikiDocument>>(`/api/v1/wiki/pages/${docId}`)
}

export async function updateDocument(docId: string, update: WikiDocumentUpdate): Promise<APIResponse> {
  return fetchApi<APIResponse>(`/api/v1/wiki/pages/${docId}`, {
    method: 'PUT',
    body: JSON.stringify(update),
  })
}

export async function deleteDocument(docId: string): Promise<APIResponse> {
  return fetchApi<APIResponse>(`/api/v1/wiki/pages/${docId}`, {
    method: 'DELETE',
  })
}

// ============ 版本管理 ============

export async function getDocumentVersions(docId: string): Promise<APIResponse<WikiDocumentVersion[]>> {
  return fetchApi<APIResponse<WikiDocumentVersion[]>>(`/api/v1/wiki/pages/${docId}/versions`)
}

export async function restoreVersion(docId: string, version: number): Promise<APIResponse> {
  return fetchApi<APIResponse>(`/api/v1/wiki/pages/${docId}/restore/${version}`, {
    method: 'POST',
  })
}

// ============ 搜索 ============

export async function searchDocuments(params: {
  q: string
  doc_type?: string
  tags?: string
  page?: number
  size?: number
}): Promise<{ items: WikiSearchResult[]; total: number; page: number; size: number }> {
  const searchParams = new URLSearchParams({ q: params.q })
  if (params?.doc_type) searchParams.set('doc_type', params.doc_type)
  if (params?.tags) searchParams.set('tags', params.tags)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.size) searchParams.set('size', String(params.size))

  return fetchApi(`/api/v1/wiki/search?${searchParams.toString()}`)
}

// ============ 标签 ============

export async function getAllTags(): Promise<APIResponse<string[]>> {
  return fetchApi<APIResponse<string[]>>('/api/v1/wiki/tags')
}

// ============ 会议集成 ============

export async function createWikiFromMeeting(meetingId: string, params: {
  doc_type?: DocType
  include_sections?: boolean
  tags?: string[]
}): Promise<APIResponse<{ job_id: string; document_id: string }>> {
  return fetchApi<APIResponse>(`/api/v1/wiki/from-meeting/${meetingId}`, {
    method: 'POST',
    body: JSON.stringify(params),
  })
}

export async function getDocumentsByMeeting(meetingId: string): Promise<APIResponse<{ items: WikiDocument[]; total: number }>> {
  return fetchApi<APIResponse>(`/api/v1/wiki/by-meeting/${meetingId}`)
}

// ============ GraphRAG 集成 ============

export async function indexDocument(docId: string): Promise<WikiIndexResponse> {
  return fetchApi<WikiIndexResponse>(`/api/v1/wiki/pages/${docId}/index`, {
    method: 'POST',
  })
}

export async function indexAllDocuments(): Promise<APIResponse<{ indexed: number; failed: number }>> {
  return fetchApi<APIResponse<{ indexed: number; failed: number }>>('/api/v1/wiki/index-all', {
    method: 'POST',
  })
}

export async function getDocumentEntities(docId: string): Promise<APIResponse<WikiEntity[]>> {
  return fetchApi<APIResponse<WikiEntity[]>>(`/api/v1/wiki/pages/${docId}/entities`)
}

export async function getDocumentRelationships(docId: string): Promise<APIResponse<WikiRelationship[]>> {
  return fetchApi<APIResponse<WikiRelationship[]>>(`/api/v1/wiki/pages/${docId}/relationships`)
}

export async function getDocumentGraph(docId: string): Promise<APIResponse<{
  nodes: Array<{ id: string; name: string; type: string }>
  edges: Array<{ source: string; target: string; type: string }>
}>> {
  return fetchApi<APIResponse>(`/api/v1/wiki/pages/${docId}/graph`)
}

// ============ 工作流与长期任务 ============

export async function getWorkflows(): Promise<APIResponse<WikiWorkflow[]>> {
  return fetchApi<APIResponse<WikiWorkflow[]>>('/api/v1/wiki/workflows')
}

export async function getLongTermTasks(): Promise<APIResponse<WikiLongTermTask[]>> {
  return fetchApi<APIResponse<WikiLongTermTask[]>>('/api/v1/wiki/long-term-tasks')
}

export async function analyzeWorkflows(): Promise<APIResponse<{
  analyzed_count: number
  insights: string[]
}>> {
  return fetchApi<APIResponse>(`/api/v1/wiki/workflows/analyze`, {
    method: 'POST',
  })
}

// ============ 子文档 ============

export async function getDocumentChildren(docId: string): Promise<APIResponse<WikiDocument[]>> {
  return fetchApi<APIResponse<WikiDocument[]>>(`/api/v1/wiki/pages/${docId}/children`)
}
