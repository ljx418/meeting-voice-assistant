export const queryKeys = {
  workspaces: ['workspaces'] as const,
  workspace: (workspaceId: string) => ['workspace', workspaceId] as const,
  notebookGuide: (workspaceId: string) => ['notebook-guide', workspaceId] as const,
  sources: (workspaceId: string) => ['sources', workspaceId] as const,
  source: (workspaceId: string, sourceId: string) => ['source', workspaceId, sourceId] as const,
  sourceTrace: (workspaceId: string, sourceId: string) => ['source-trace', workspaceId, sourceId] as const,
  capabilities: (workspaceId: string) => ['capabilities', workspaceId] as const,
  sourcePreview: (workspaceId: string, sourceId: string) => ['source-preview', workspaceId, sourceId] as const,
  sourceUnits: (workspaceId: string, sourceId: string) => ['source-units', workspaceId, sourceId] as const,
  sourceUnit: (workspaceId: string, sourceId: string, unitId: string) => ['source-unit', workspaceId, sourceId, unitId] as const,
  sourceEvidenceSpan: (workspaceId: string, sourceId: string, unitId: string, evidenceId: string) =>
    ['source-evidence-span', workspaceId, sourceId, unitId, evidenceId] as const,
  sourceSearch: (workspaceId: string, query: string, typeFilter: string) => ['source-search', workspaceId, query, typeFilter] as const,
  buildOperation: (workspaceId: string, operationId: string) => ['build-operation', workspaceId, operationId] as const,
  workspaceQuery: (workspaceId: string) => ['workspace-query', workspaceId] as const,
  sessions: (workspaceId: string) => ['sessions', workspaceId] as const,
  session: (workspaceId: string, sessionId: string) => ['session', workspaceId, sessionId] as const,
  sessionBuildOperation: (workspaceId: string, sessionId: string, operationId: string) =>
    ['session-build-operation', workspaceId, sessionId, operationId] as const,
  sessionQuery: (workspaceId: string, sessionId: string) => ['session-query', workspaceId, sessionId] as const,
  agentWorkflowDraft: (workspaceId: string, taskId: string) => ['agent-workflow-draft', workspaceId, taskId] as const,
  agentWorkflowRun: (workspaceId: string, runId: string) => ['agent-workflow-run', workspaceId, runId] as const,
  graphNeighborsByNode: (workspaceId: string, nodeId: string) => ['graph-neighbors', workspaceId, 'node', nodeId] as const,
  graphNeighborsByEntity: (workspaceId: string, entityId: string) => ['graph-neighbors', workspaceId, 'entity', entityId] as const,
  graphCommunities: (workspaceId: string) => ['graph-communities', workspaceId] as const,
  sessionGraph: (workspaceId: string, sessionId: string) => ['session-graph', workspaceId, sessionId] as const,
  // Artifacts
  artifacts: (workspaceId: string) => ['artifacts', workspaceId] as const,
  artifact: (workspaceId: string, artifactId: string) => ['artifact', workspaceId, artifactId] as const,
  artifactStatus: (workspaceId: string, artifactId: string) => ['artifact-status', workspaceId, artifactId] as const,
  ocrStatus: (workspaceId: string, sourceId: string) => ['ocr-status', workspaceId, sourceId] as const
};
