export const queryKeys = {
  workspaces: ['workspaces'] as const,
  workspace: (workspaceId: string) => ['workspace', workspaceId] as const,
  sources: (workspaceId: string) => ['sources', workspaceId] as const,
  source: (workspaceId: string, sourceId: string) => ['source', workspaceId, sourceId] as const,
  sourceTrace: (workspaceId: string, sourceId: string) => ['source-trace', workspaceId, sourceId] as const,
  buildOperation: (workspaceId: string, operationId: string) => ['build-operation', workspaceId, operationId] as const,
  workspaceQuery: (workspaceId: string) => ['workspace-query', workspaceId] as const,
  sessions: (workspaceId: string) => ['sessions', workspaceId] as const,
  session: (workspaceId: string, sessionId: string) => ['session', workspaceId, sessionId] as const,
  sessionBuildOperation: (workspaceId: string, sessionId: string, operationId: string) =>
    ['session-build-operation', workspaceId, sessionId, operationId] as const,
  sessionQuery: (workspaceId: string, sessionId: string) => ['session-query', workspaceId, sessionId] as const,
  graphNeighbors: (workspaceId: string) => ['graph-neighbors', workspaceId] as const,
  graphCommunities: (workspaceId: string) => ['graph-communities', workspaceId] as const,
  sessionGraph: (workspaceId: string, sessionId: string) => ['session-graph', workspaceId, sessionId] as const
};
