import { useMutation, useQuery } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type { AgentWorkflowDraftRequest } from '../types/api';

export function useAgentWorkflowDraftQuery(workspaceId: string, taskId: string | null) {
  return useQuery({
    queryKey: queryKeys.agentWorkflowDraft(workspaceId, taskId ?? 'none'),
    queryFn: () => dataServiceClient.agentWorkflows.getDraft(workspaceId, taskId ?? ''),
    enabled: false,
    retry: false
  });
}

export function useCreateAgentWorkflowDraftMutation(workspaceId: string) {
  return useMutation({
    mutationFn: (input: AgentWorkflowDraftRequest) => dataServiceClient.agentWorkflows.createDraft(workspaceId, input),
    retry: false
  });
}
