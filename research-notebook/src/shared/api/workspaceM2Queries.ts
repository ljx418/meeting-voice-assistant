import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { BuildStartRequest, CreateSourceRequest, QueryRequest, QueryResponse } from '../types/api';

export function useSourcesQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.sources(workspaceId),
    queryFn: () => dataServiceClient.sources.list(workspaceId),
    enabled: Boolean(workspaceId)
  });
}

export function useSourceTraceQuery(workspaceId: string, sourceId: string | null) {
  return useQuery({
    queryKey: queryKeys.sourceTrace(workspaceId, sourceId ?? 'none'),
    queryFn: () => dataServiceClient.sources.trace(workspaceId, sourceId ?? ''),
    enabled: Boolean(workspaceId && sourceId)
  });
}

export function useCreateSourceMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateSourceRequest) => dataServiceClient.sources.create(workspaceId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) });
    }
  });
}

export function useRemoveSourceMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sourceId: string) => dataServiceClient.sources.remove(workspaceId, sourceId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) });
    }
  });
}

export function useStartBuildMutation(workspaceId: string) {
  return useMutation({
    mutationFn: (input?: BuildStartRequest) => dataServiceClient.build.start(workspaceId, input)
  });
}

export function useWorkspaceQueryMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: QueryRequest) => dataServiceClient.query.workspace(workspaceId, input),
    onSuccess: (response: QueryResponse) => {
      queryClient.setQueryData(queryKeys.workspaceQuery(workspaceId), response);
    }
  });
}
