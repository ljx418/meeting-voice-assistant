import { useMutation, useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { GraphNeighborsRequest, QualityFeedbackRequest } from '../types/api';

function graphNeighborsQueryKey(workspaceId: string, request: GraphNeighborsRequest | null) {
  if (request?.nodeId) return queryKeys.graphNeighborsByNode(workspaceId, request.nodeId);
  if (request?.entityId) return queryKeys.graphNeighborsByEntity(workspaceId, request.entityId);
  return ['graph-neighbors', workspaceId, 'none'] as const;
}

export function useGraphNeighborsQuery(workspaceId: string, request: GraphNeighborsRequest | null) {
  return useQuery({
    queryKey: graphNeighborsQueryKey(workspaceId, request),
    queryFn: () => dataServiceClient.graph.neighbors(workspaceId, request as GraphNeighborsRequest),
    enabled: Boolean(workspaceId && request)
  });
}

export function useGraphCommunitiesQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.graphCommunities(workspaceId),
    queryFn: () => dataServiceClient.graph.communities(workspaceId),
    enabled: Boolean(workspaceId)
  });
}

export function useSessionGraphQuery(workspaceId: string, sessionId: string | null) {
  return useQuery({
    queryKey: queryKeys.sessionGraph(workspaceId, sessionId ?? 'none'),
    queryFn: () => dataServiceClient.graph.session(workspaceId, sessionId ?? ''),
    enabled: Boolean(workspaceId && sessionId)
  });
}

export function useQualityFeedbackMutation(workspaceId: string) {
  return useMutation({
    mutationFn: (input: QualityFeedbackRequest) => dataServiceClient.quality.feedback(workspaceId, input)
  });
}
