import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { CreateSessionRequest, SessionBuildStartRequest, SessionIngestRequest, SessionQueryRequest, SessionQueryResponse } from '../types/api';

export function useSessionsQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.sessions(workspaceId),
    queryFn: () => dataServiceClient.sessions.list(workspaceId),
    enabled: Boolean(workspaceId)
  });
}

export function useSessionQuery(workspaceId: string, sessionId: string | null) {
  return useQuery({
    queryKey: queryKeys.session(workspaceId, sessionId ?? 'none'),
    queryFn: () => dataServiceClient.sessions.get(workspaceId, sessionId ?? ''),
    enabled: Boolean(workspaceId && sessionId)
  });
}

export function useCreateSessionMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateSessionRequest) => dataServiceClient.sessions.create(workspaceId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.sessions(workspaceId) });
    }
  });
}

export function useCloseSessionMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => dataServiceClient.sessions.close(workspaceId, sessionId),
    onSuccess: async (response) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.sessions(workspaceId) });
      await queryClient.invalidateQueries({ queryKey: queryKeys.session(workspaceId, response.session_id) });
    }
  });
}

export function useSessionIngestMutation(workspaceId: string, sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: SessionIngestRequest) => dataServiceClient.sessions.ingest(workspaceId, sessionId, input),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.session(workspaceId, sessionId) });
    }
  });
}

export function useStartSessionBuildMutation(workspaceId: string, sessionId: string) {
  return useMutation({
    mutationFn: (input?: SessionBuildStartRequest) => dataServiceClient.sessions.build.start(workspaceId, sessionId, input)
  });
}

export function useSessionQueryMutation(workspaceId: string, sessionId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: SessionQueryRequest) => dataServiceClient.sessions.query(workspaceId, sessionId, input),
    onSuccess: (response: SessionQueryResponse) => {
      queryClient.setQueryData(queryKeys.sessionQuery(workspaceId, sessionId), response);
    }
  });
}
