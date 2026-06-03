export interface McpToolContract {
  name: string
  group:
    | 'Core'
    | 'Distill'
    | 'Trace'
    | 'Quality'
    | 'V2 Envelope'
    | 'Workspace'
    | 'Source'
    | 'Build'
    | 'Session GraphRAG'
    | 'Project Intelligence'
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
  capability:
    | 'workspace'
    | 'source'
    | 'build'
    | 'query'
    | 'distill'
    | 'graph'
    | 'trace'
    | 'quality'
    | 'session'
    | 'codebase'
  mcpTool: string
  httpRoute: string
  cliCommand: string
  status: 'primary' | 'compat' | 'planned'
  target: string
}

export interface GovernanceEvidenceMetric {
  label: string
  value: string
  detail: string
}

export interface GovernanceOverlayEvidence {
  phase: string
  delta: string
  detail: string
}

export interface GovernanceCapabilityEvidence {
  capability: string
  status: string
  evidence: string
}

export const governanceBaselineEvidence: GovernanceEvidenceMetric[] = [
  { label: 'V1.5 target baseline', value: '3', detail: 'query / distill / source trace' },
  { label: 'MCP tool count', value: '61', detail: 'V1.5 baseline 40 + V2 project intelligence 10 + V2.1 DevWiki 2 + V2.1 Code Graph 4 + V2.1 Code Quality 5' },
  { label: 'CLI top-level', value: '8', detail: 'build / code / graph / quality / query / source / trace / workspace' },
  { label: 'Current target HTTP', value: '65', detail: 'V1.5 baseline + accepted overlays + V2 overview/context routes + V2.1 DevWiki routes + V2.1 Code Graph routes + V2.1 Code Quality routes' },
  { label: 'Compatibility HTTP', value: 'retained', detail: '/api/v1/knowledge/*' },
  { label: 'Console role', value: 'governance', detail: 'service governance console, not end-user knowledge consumption app' },
]

export const governanceOverlayEvidence: GovernanceOverlayEvidence[] = [
  { phase: 'A public surface guard', delta: '+0', detail: 'guard only, not a route overlay' },
  { phase: 'B lifecycle overlays', delta: '+11', detail: 'workspace / source / build' },
  { phase: 'C graph advanced overlays', delta: '+4', detail: 'neighbors / community / query / session inspection' },
  { phase: 'D1 planning', delta: '+0', detail: 'contract hardening, not a route overlay' },
  { phase: 'D2 lifecycle', delta: '+5', detail: 'session create / list / get / close / delete' },
  { phase: 'D3 planning', delta: '+0', detail: 'ingest / query / build planning, not a route overlay' },
  { phase: 'D4/D5/D6 session overlays', delta: '+5', detail: 'session ingest / query / build' },
  { phase: 'E1-E5 quality overlays', delta: '+7', detail: 'feedback / rules / review / plan / rules-build; no correction apply' },
  { phase: 'F1 evidence baseline', delta: '+0', detail: 'documentation evidence and guard only' },
  { phase: 'F2 console polish', delta: '+0', detail: 'display-only governance evidence; no backend public surface' },
]

export const governanceCapabilityEvidence: GovernanceCapabilityEvidence[] = [
  { capability: 'V1.5 baseline', status: 'immutable', evidence: 'MCP 40 / CLI top-level 7 / target HTTP 3' },
  { capability: 'V2 codebase asset', status: 'accepted', evidence: 'MCP +7 / CLI top-level +1 / target HTTP codebase + snapshot + inventory + symbol routes' },
  { capability: 'V2.1 DevWiki', status: 'accepted', evidence: 'MCP +2 / CLI nested code devwiki / target HTTP devwiki build/pages/read' },
  { capability: 'V2.1 Code Graph', status: 'accepted', evidence: 'MCP +4 / CLI nested code graph / target HTTP graph build/snapshot/neighbors/mermaid' },
  { capability: 'V2.1 Code Quality', status: 'accepted', evidence: 'MCP +5 / CLI nested code quality / target HTTP quality feedback/summary/rules/review/plan' },
  { capability: 'Public surface guard', status: 'accepted', evidence: 'A guard tests' },
  { capability: 'Workspace/Source/Build', status: 'accepted', evidence: 'B overlays +11' },
  { capability: 'Graph advanced', status: 'accepted', evidence: 'C overlays +4; graph neighbors / community / query / session CLI nested additions' },
  { capability: 'Session lifecycle/ingest/query/build', status: 'accepted', evidence: 'D overlays +10, D1/D3 +0' },
  { capability: 'Quality feedback/rules/review/plan/rules-build', status: 'accepted', evidence: 'E overlays +7; correction apply not opened' },
  { capability: 'Console governance evidence plan', status: 'F1 accepted', evidence: 'evidence plan exists' },
  { capability: 'Console polish', status: 'F2 implemented', evidence: 'no backend public surface' },
  { capability: 'Closure acceptance', status: 'planned', evidence: 'not implemented' },
]

export const acceptedGraphCliNestedAdditions = [
  'graph neighbors',
  'graph community',
  'graph query',
  'graph session',
] as const

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
  { name: 'knowledge_codebase_import', group: 'Project Intelligence', required: ['workspace_id', 'path'], optional: ['codebase_id', 'name', 'metadata', 'scan_policy'], status: 'stable' },
  { name: 'knowledge_codebase_list', group: 'Project Intelligence', required: ['workspace_id'], optional: ['include_archived', 'limit'], status: 'stable' },
  { name: 'knowledge_codebase_snapshot', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['scan_policy', 'include_git'], status: 'stable' },
  { name: 'knowledge_codebase_describe', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_codebase_archive', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['reason'], status: 'stable' },
  { name: 'knowledge_project_inventory', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id', 'build'], status: 'stable' },
  { name: 'knowledge_code_symbol_search', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id', 'query', 'kind', 'limit', 'build'], status: 'stable' },
  { name: 'knowledge_public_surface_trace', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id', 'surface_id', 'capability', 'limit', 'build'], status: 'stable' },
  { name: 'knowledge_project_overview', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_agent_context_pack', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id', 'mode', 'task', 'format', 'max_tokens', 'focus', 'include', 'pack_id'], status: 'stable' },
  { name: 'knowledge_devwiki_build', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_devwiki_read', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['page_slug'], status: 'stable' },
  { name: 'knowledge_code_graph_build', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_code_graph_snapshot', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_code_graph_neighbors', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id', 'node_id'], optional: ['snapshot_id', 'depth', 'limit'], status: 'stable' },
  { name: 'knowledge_code_graph_mermaid', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_code_quality_feedback', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id', 'target_type', 'target_id', 'action', 'rule_type'], optional: ['severity', 'reason', 'suggested_value', 'metadata'], status: 'stable' },
  { name: 'knowledge_code_quality_summary', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_code_quality_rules_build', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_code_quality_rule_review', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id', 'rule_id', 'status'], optional: ['reviewer', 'note'], status: 'stable' },
  { name: 'knowledge_code_quality_plan', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_architecture_sources_scan', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_architecture_model_build', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_architecture_model_read', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_architecture_alignment', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_architecture_findings', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_architecture_view', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['view_id'], status: 'stable' },
  { name: 'knowledge_code_architecture_build', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['snapshot_id'], status: 'stable' },
  { name: 'knowledge_code_architecture_roles', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_code_architecture_patterns', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: [], status: 'stable' },
  { name: 'knowledge_code_architecture_view', group: 'Project Intelligence', required: ['workspace_id', 'codebase_id'], optional: ['view_id'], status: 'stable' },
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
  { capability: 'codebase', mcpTool: 'knowledge_codebase_import/list/snapshot/project_inventory/code_symbol_search/public_surface_trace/project_overview/agent_context_pack/devwiki_build/devwiki_read/code_graph_build/code_graph_snapshot/code_graph_neighbors/code_graph_mermaid/code_quality_feedback/code_quality_summary/code_quality_rules_build/code_quality_rule_review/code_quality_plan/describe/archive', httpRoute: '/api/workspaces/{workspace_id}/codebases/*', cliCommand: 'knowledge code import/list/snapshot/inventory/symbols/trace/overview/context-pack/devwiki/graph/quality/describe/archive', status: 'primary', target: 'V2.1 project intelligence foundation plus DevWiki, Code Graph, and Code Quality baselines' },
]
