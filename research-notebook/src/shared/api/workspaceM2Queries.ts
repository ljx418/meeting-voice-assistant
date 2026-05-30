import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../../app/routes/queryKeys';
import { dataServiceClient } from './dataServiceClient';
import type {
  BuildStartRequest,
  CapabilityManifest,
  CreateSourceRequest,
  QueryRequest,
  QueryResponse,
  ResearchRequest,
  RenameSourceRequest,
  StudioArtifactRequest
} from '../types/api';

export function isSourceLevelPreviewSupported(manifest: CapabilityManifest | undefined, sourceType?: string) {
  if (!manifest?.capabilities.source_preview || !manifest.capabilities.source_level_preview) return false;
  if (!sourceType) {
    return manifest.supported_source_types.some((item) => item.preview === 'source' || item.preview === 'unit' || item.preview === 'span');
  }
  const supported = manifest.supported_source_types.find((item) => item.source_type === sourceType);
  return supported?.preview === 'source' || supported?.preview === 'unit' || supported?.preview === 'span';
}

export function isUnitLevelNavigationSupported(manifest: CapabilityManifest | undefined, sourceType?: string) {
  if (!manifest?.capabilities.document_units || !manifest.capabilities.unit_level_navigation) return false;
  if (!sourceType) {
    return manifest.supported_source_types.some((item) => item.preview === 'unit' || item.preview === 'span');
  }
  const supported = manifest.supported_source_types.find((item) => item.source_type === sourceType);
  return supported?.preview === 'unit' || supported?.preview === 'span';
}

export function isEvidenceSpanNavigationSupported(manifest: CapabilityManifest | undefined) {
  return Boolean(
    manifest?.capabilities.evidence_spans &&
      manifest.capabilities.precise_span_highlight &&
      manifest.capabilities.citation_backjump &&
      manifest.capabilities.document_units &&
      manifest.capabilities.unit_level_navigation
  );
}

export function useCapabilitiesQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.capabilities(workspaceId),
    queryFn: () => dataServiceClient.capabilities.get(workspaceId),
    enabled: Boolean(workspaceId),
    retry: false
  });
}

export function useSourcesQuery(workspaceId: string) {
  return useQuery({
    queryKey: queryKeys.sources(workspaceId),
    queryFn: () => dataServiceClient.sources.list(workspaceId),
    enabled: Boolean(workspaceId)
  });
}

export function useNotebookGuideQuery(workspaceId: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.notebookGuide(workspaceId),
    queryFn: () => dataServiceClient.guide.get(workspaceId),
    enabled: Boolean(workspaceId && enabled),
    retry: false
  });
}

export function useSourceTraceQuery(workspaceId: string, sourceId: string | null) {
  return useQuery({
    queryKey: queryKeys.sourceTrace(workspaceId, sourceId ?? 'none'),
    queryFn: () => dataServiceClient.sources.trace(workspaceId, sourceId ?? ''),
    enabled: Boolean(workspaceId && sourceId)
  });
}

export function useSourcePreviewQuery(workspaceId: string, sourceId: string | null, enabled = true) {
  return useQuery({
    queryKey: queryKeys.sourcePreview(workspaceId, sourceId ?? 'none'),
    queryFn: () => dataServiceClient.sources.preview(workspaceId, sourceId ?? ''),
    enabled: Boolean(workspaceId && sourceId && enabled),
    retry: false
  });
}

export function useSourceUnitsQuery(workspaceId: string, sourceId: string | null, enabled = true) {
  return useInfiniteQuery({
    queryKey: queryKeys.sourceUnits(workspaceId, sourceId ?? 'none'),
    queryFn: ({ pageParam }) =>
      dataServiceClient.sources.listUnits(workspaceId, sourceId ?? '', {
        limit: 20,
        cursor: pageParam || undefined
      }),
    initialPageParam: '',
    getNextPageParam: (lastPage) => lastPage.next_cursor || undefined,
    enabled: Boolean(workspaceId && sourceId && enabled),
    retry: false
  });
}

export function useSourceUnitQuery(workspaceId: string, sourceId: string | null, unitId: string | null, enabled = true) {
  return useQuery({
    queryKey: queryKeys.sourceUnit(workspaceId, sourceId ?? 'none', unitId ?? 'none'),
    queryFn: () => dataServiceClient.sources.getUnit(workspaceId, sourceId ?? '', unitId ?? ''),
    enabled: Boolean(workspaceId && sourceId && unitId && enabled),
    retry: false
  });
}

export function useSourceEvidenceSpanQuery(
  workspaceId: string,
  sourceId: string | null,
  unitId: string | null,
  evidenceId: string | null,
  enabled = true
) {
  return useQuery({
    queryKey: queryKeys.sourceEvidenceSpan(workspaceId, sourceId ?? 'none', unitId ?? 'none', evidenceId ?? 'none'),
    queryFn: () => dataServiceClient.sources.getEvidenceSpan(workspaceId, sourceId ?? '', unitId ?? '', evidenceId ?? ''),
    enabled: Boolean(workspaceId && sourceId && unitId && evidenceId && enabled),
    retry: false
  });
}

export function useSourceQuery(workspaceId: string, sourceId: string | null) {
  return useQuery({
    queryKey: queryKeys.source(workspaceId, sourceId ?? 'none'),
    queryFn: () => dataServiceClient.sources.get(workspaceId, sourceId ?? ''),
    enabled: Boolean(workspaceId && sourceId)
  });
}

export function useCreateSourceMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateSourceRequest) => dataServiceClient.sources.create(workspaceId, input),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.notebookGuide(workspaceId) })
      ]);
    }
  });
}

export function useRemoveSourceMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sourceId: string) => dataServiceClient.sources.remove(workspaceId, sourceId),
    onSuccess: async (_response, sourceId) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.notebookGuide(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.sourcePreview(workspaceId, sourceId) })
      ]);
    }
  });
}

export function useRenameSourceMutation(workspaceId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sourceId, input }: { sourceId: string; input: RenameSourceRequest }) =>
      dataServiceClient.sources.rename(workspaceId, sourceId, input),
    onSuccess: async (_response, variables) => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: queryKeys.sources(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.notebookGuide(workspaceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.source(workspaceId, variables.sourceId) }),
        queryClient.invalidateQueries({ queryKey: queryKeys.sourcePreview(workspaceId, variables.sourceId) })
      ]);
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

export function useStudioArtifactMutation(workspaceId: string) {
  return useMutation({
    mutationFn: (input: StudioArtifactRequest) => dataServiceClient.studio.createArtifact(workspaceId, input)
  });
}

export function useResearchReportMutation(workspaceId: string) {
  return useMutation({
    mutationFn: (input: ResearchRequest) => dataServiceClient.research.createReport(workspaceId, input)
  });
}
