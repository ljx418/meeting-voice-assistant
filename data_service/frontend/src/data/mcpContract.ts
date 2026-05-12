export interface McpToolContract {
  name: string
  group: 'Core' | 'Distill' | 'Trace' | 'Quality' | 'V2 Envelope' | 'Workspace' | 'Source' | 'Build' | 'Session GraphRAG'
  required: string[]
  optional: string[]
  status: 'stable' | 'compat'
  samplePayload?: Record<string, unknown>
  successPreview?: Record<string, unknown>
  errorPreviews?: McpErrorPreview[]
  aliasTarget?: string
}

export interface McpResourceContract {
  uri: string
  name: string
  mimeType: string
  status: 'stable' | 'compat'
}

export interface McpErrorPreview {
  key: string
  label: string
  envelope: Record<string, unknown>
}

export interface InterfaceEntryContract {
  capability: 'workspace' | 'source' | 'build' | 'query' | 'distill' | 'graph' | 'trace' | 'quality' | 'session'
  mcpTool: string
  httpRoute: string
  cliCommand: string
  status: 'primary' | 'compat' | 'planned'
  target: string
}

export const mcpToolContracts: McpToolContract[] = [
  {
    name: 'knowledge_ingest',
    group: 'Core',
    required: ['paths'],
    optional: ['workspace'],
    status: 'stable',
    samplePayload: { paths: ['/path/to/source.md'], workspace: '/path/to/workspace' },
    successPreview: {
      workspace: '/path/to/workspace',
      results: [{ engine: 'llmwiki', status: 'success', meta: { source_count: 1 } }],
    },
  },
  {
    name: 'knowledge_query',
    group: 'Core',
    required: ['query'],
    optional: ['workspace', 'mode', 'top_k'],
    status: 'stable',
    samplePayload: { query: '示例查询', mode: 'hybrid', top_k: 8 },
    successPreview: {
      mode: 'hybrid',
      query: '示例查询',
      answer: '聚合回答摘要',
      hits: [{ title: '相关页面', snippet: '命中的证据片段', source: 'page_slug', score: 0.86 }],
      engine_payloads: { llmwiki: {}, graphrag: {} },
    },
  },
  {
    name: 'knowledge_distill_preview',
    group: 'Distill',
    required: [],
    optional: ['workspace', 'workspace_id', 'source_id', 'limit', 'kind', 'typed_unit_type', 'min_importance', 'llm_enriched_only', 'authority', 'min_source_weight', 'min_source_density'],
    status: 'stable',
    samplePayload: { workspace_id: 'research-vault', limit: 20, typed_unit_type: 'concept' },
  },
  {
    name: 'knowledge_source_trace',
    group: 'Trace',
    required: ['source_id'],
    optional: ['workspace', 'workspace_id', 'limit'],
    status: 'stable',
    samplePayload: { workspace_id: 'research-vault', source_id: 'src_123', limit: 12 },
  },
  { name: 'knowledge_quality_summary', group: 'Quality', required: [], optional: ['workspace', 'workspace_id'], status: 'stable' },
  { name: 'knowledge_correction_plan', group: 'Quality', required: [], optional: ['workspace', 'workspace_id', 'rebuild'], status: 'stable' },
  { name: 'knowledge_quality_feedback', group: 'Quality', required: ['target_type', 'target_id', 'action'], optional: ['workspace', 'workspace_id', 'label', 'suggested_value', 'reason', 'metadata'], status: 'stable' },
  { name: 'knowledge_correction_rules', group: 'Quality', required: [], optional: ['workspace', 'workspace_id', 'limit', 'status'], status: 'stable' },
  { name: 'knowledge_review_correction_rule', group: 'Quality', required: ['rule_id', 'status'], optional: ['workspace', 'workspace_id', 'reviewer', 'note'], status: 'stable' },
  { name: 'knowledge_ingest_v2', group: 'V2 Envelope', required: ['paths'], optional: ['workspace', 'workspace_id'], status: 'compat', aliasTarget: 'knowledge_ingest' },
  { name: 'knowledge_query_v2', group: 'V2 Envelope', required: ['query'], optional: ['workspace', 'workspace_id', 'mode', 'top_k'], status: 'compat', aliasTarget: 'knowledge_query' },
  { name: 'knowledge_quality_summary_v2', group: 'V2 Envelope', required: [], optional: ['workspace', 'workspace_id'], status: 'compat', aliasTarget: 'knowledge_quality_summary' },
  { name: 'knowledge_correction_plan_v2', group: 'V2 Envelope', required: [], optional: ['workspace', 'workspace_id', 'rebuild'], status: 'compat', aliasTarget: 'knowledge_correction_plan' },
  { name: 'knowledge_quality_feedback_v2', group: 'V2 Envelope', required: ['target_type', 'target_id', 'action'], optional: ['workspace', 'workspace_id', 'label', 'suggested_value', 'reason', 'metadata'], status: 'compat', aliasTarget: 'knowledge_quality_feedback' },
  { name: 'knowledge_correction_rules_v2', group: 'V2 Envelope', required: [], optional: ['workspace', 'workspace_id', 'limit', 'status'], status: 'compat', aliasTarget: 'knowledge_correction_rules' },
  { name: 'knowledge_review_correction_rule_v2', group: 'V2 Envelope', required: ['rule_id', 'status'], optional: ['workspace', 'workspace_id', 'reviewer', 'note'], status: 'compat', aliasTarget: 'knowledge_review_correction_rule' },
  { name: 'knowledge_workspace_create', group: 'Workspace', required: ['name'], optional: ['root', 'owner', 'tags', 'bound_paths'], status: 'stable' },
  { name: 'knowledge_workspace_list', group: 'Workspace', required: [], optional: ['root', 'owner', 'tag', 'limit'], status: 'stable' },
  { name: 'knowledge_workspace_describe', group: 'Workspace', required: [], optional: ['workspace', 'workspace_id'], status: 'stable' },
  { name: 'knowledge_workspace_archive', group: 'Workspace', required: [], optional: ['workspace', 'workspace_id', 'reason'], status: 'stable' },
  { name: 'knowledge_source_import', group: 'Source', required: ['paths'], optional: ['workspace', 'workspace_id', 'metadata'], status: 'stable' },
  { name: 'knowledge_source_list', group: 'Source', required: [], optional: ['workspace', 'workspace_id', 'limit', 'status'], status: 'stable' },
  { name: 'knowledge_source_remove', group: 'Source', required: ['source_id'], optional: ['workspace', 'workspace_id', 'reason'], status: 'stable' },
  { name: 'knowledge_build_start', group: 'Build', required: [], optional: ['workspace', 'workspace_id', 'mode', 'paths'], status: 'stable' },
  { name: 'knowledge_build_status', group: 'Build', required: ['operation_id'], optional: ['workspace', 'workspace_id'], status: 'stable' },
  { name: 'knowledge_build_cancel', group: 'Build', required: ['operation_id'], optional: ['workspace', 'workspace_id', 'reason'], status: 'stable' },
  { name: 'knowledge_session_create', group: 'Session GraphRAG', required: [], optional: ['workspace_id', 'external_id', 'title', 'metadata'], status: 'stable' },
  { name: 'knowledge_session_get', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id'], status: 'stable' },
  { name: 'knowledge_session_list', group: 'Session GraphRAG', required: [], optional: ['workspace_id', 'limit', 'status'], status: 'stable' },
  { name: 'knowledge_session_close', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'reason'], status: 'stable' },
  { name: 'knowledge_session_delete', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'reason'], status: 'stable' },
  { name: 'knowledge_session_ingest', group: 'Session GraphRAG', required: ['session_id', 'turns'], optional: ['workspace_id', 'source_id', 'metadata'], status: 'stable' },
  { name: 'knowledge_session_build_start', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'mode'], status: 'stable' },
  { name: 'knowledge_session_build_status', group: 'Session GraphRAG', required: ['operation_id'], optional: ['workspace_id', 'session_id'], status: 'stable' },
  { name: 'knowledge_session_build_cancel', group: 'Session GraphRAG', required: ['operation_id'], optional: ['workspace_id', 'session_id', 'reason'], status: 'stable' },
  { name: 'knowledge_graph_snapshot', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'max_nodes'], status: 'stable' },
  { name: 'knowledge_graph_neighbors', group: 'Session GraphRAG', required: ['session_id', 'node_id'], optional: ['workspace_id', 'depth', 'limit'], status: 'stable' },
  { name: 'knowledge_community_summary', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'community_id'], status: 'stable' },
  { name: 'knowledge_session_query', group: 'Session GraphRAG', required: ['session_id', 'query'], optional: ['workspace_id', 'mode', 'top_k'], status: 'stable' },
  { name: 'knowledge_actor_summary', group: 'Session GraphRAG', required: ['session_id'], optional: ['workspace_id', 'actor_id'], status: 'stable' },
]

export const mcpResourceContracts: McpResourceContract[] = [
  { uri: 'data-service://summary', name: 'Workspace Summary', mimeType: 'text/markdown', status: 'stable' },
  { uri: 'data-service://layout', name: 'Workspace Layout', mimeType: 'application/json', status: 'stable' },
  { uri: 'data_service://summary', name: 'Legacy Summary URI', mimeType: 'text/markdown', status: 'compat' },
  { uri: 'data_service://layout', name: 'Legacy Layout URI', mimeType: 'application/json', status: 'compat' },
]

export const mcpV2AliasContracts = [
  ['knowledge_ingest_v2', 'knowledge_ingest'],
  ['knowledge_query_v2', 'knowledge_query'],
  ['knowledge_quality_summary_v2', 'knowledge_quality_summary'],
  ['knowledge_correction_plan_v2', 'knowledge_correction_plan'],
  ['knowledge_quality_feedback_v2', 'knowledge_quality_feedback'],
  ['knowledge_correction_rules_v2', 'knowledge_correction_rules'],
  ['knowledge_review_correction_rule_v2', 'knowledge_review_correction_rule'],
] as const

export const interfaceEntryContracts: InterfaceEntryContract[] = [
  { capability: 'workspace', mcpTool: 'knowledge_workspace_create/list/describe/archive', httpRoute: '/api/v1/knowledge/workspaces/*', cliCommand: 'knowledge workspace create/list/describe/archive', status: 'primary', target: 'PhaseG25 workspace_id-first lifecycle CLI aliases active' },
  { capability: 'source', mcpTool: 'knowledge_source_import/list/remove', httpRoute: '/api/v1/knowledge/sources/*', cliCommand: 'knowledge source import/list/remove', status: 'primary', target: 'PhaseG26 source registry CLI aliases active' },
  { capability: 'build', mcpTool: 'knowledge_build_start/status/cancel', httpRoute: '/api/v1/knowledge/build/*', cliCommand: 'knowledge build start/status/cancel', status: 'primary', target: 'PhaseG27 operation lifecycle CLI aliases active' },
  { capability: 'query', mcpTool: 'knowledge_query / knowledge_query_v2', httpRoute: '/api/v1/knowledge/query', cliCommand: 'data_service query / knowledge query', status: 'compat', target: 'PhaseG18 shared query payload contract active across MCP/HTTP/CLI' },
  { capability: 'distill', mcpTool: 'knowledge_distill_preview', httpRoute: '/api/v1/knowledge/distill', cliCommand: 'data_service distill', status: 'primary', target: 'PhaseG28 shared distill preview payload contract active across MCP/HTTP/CLI' },
  { capability: 'graph', mcpTool: 'knowledge_graph_snapshot/neighbors/community_summary', httpRoute: '/api/v1/knowledge/graph', cliCommand: 'planned: knowledge graph *', status: 'compat', target: 'GraphRAG service boundary remains app.graphrag.service' },
  { capability: 'trace', mcpTool: 'knowledge_source_trace', httpRoute: '/api/v1/knowledge/source/trace', cliCommand: 'knowledge trace source', status: 'primary', target: 'PhaseG29 shared source trace payload contract active across MCP/HTTP/CLI' },
  { capability: 'quality', mcpTool: 'knowledge_quality_* / knowledge_correction_*', httpRoute: '/api/v1/knowledge/quality/*', cliCommand: 'planned: knowledge quality *', status: 'primary', target: 'feedback/rules/plan review contract' },
  { capability: 'session', mcpTool: 'knowledge_session_* / knowledge_actor_summary', httpRoute: 'planned: /api/v1/knowledge/sessions/*', cliCommand: 'planned: knowledge session *', status: 'primary', target: 'session graph lifecycle stays MCP-first' },
]
