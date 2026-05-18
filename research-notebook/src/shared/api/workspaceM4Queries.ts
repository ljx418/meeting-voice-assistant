import { useMutation, useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { QualityFeedbackRequest } from '../types/api';

export function useGraphNeighborsQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.graphNeighbors(workspaceId),
    queryFn: () => dataServiceClient.graph.neighbors(workspaceId),
    enabled: Boolean(workspaceId)
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
