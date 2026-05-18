import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { CreateWorkspaceRequest } from '../types/api';

export function useWorkspacesQuery() {
  return useQuery({
    queryKey: queryKeys.workspaces,
    queryFn: () => dataServiceClient.workspaces.list()
  });
}

export function useWorkspaceQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.workspace(workspaceId),
    queryFn: () => dataServiceClient.workspaces.get(workspaceId),
    enabled: Boolean(workspaceId)
  });
}

export function useCreateWorkspaceMutation() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation({
    mutationFn: (input: CreateWorkspaceRequest) => dataServiceClient.workspaces.create(input),
    onSuccess: async (response) => {
      await queryClient.invalidateQueries({ queryKey: queryKeys.workspaces });
      navigate(`/workspaces/${encodeURIComponent(response.workspace.workspace_id)}`);
    }
  });
}

export function useArchiveWorkspaceMutation(workspaceId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => dataServiceClient.workspaces.archive(workspaceId),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.workspaces }),
        queryClient.invalidateQueries({ queryKey: queryKeys.workspace(workspaceId) })
      ]);
    }
  });
}
