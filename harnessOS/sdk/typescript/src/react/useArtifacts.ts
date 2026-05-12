import { useCallback, useState } from "react";

import type { HookActionState, HookClientOptions } from "./types.js";

export interface UseArtifactsResult extends HookActionState<Record<string, unknown>> {
  artifacts?: Record<string, unknown>;
  refresh(params?: { sessionId?: string; kind?: string }): Promise<Record<string, unknown>>;
  readMetadata(artifactId: string): Promise<Record<string, unknown>>;
  lineage(params?: { artifactId?: string; sessionId?: string }): Promise<Record<string, unknown>>;
}

export function useArtifacts(options: HookClientOptions): UseArtifactsResult {
  const [state, setState] = useState<HookActionState<Record<string, unknown>>>({ status: "idle" });

  const run = useCallback(async (operation: () => Promise<Record<string, unknown>>) => {
    setState({ status: "loading" });
    try {
      const result = await operation();
      setState({ status: "success", data: result });
      return result;
    } catch (error) {
      setState({ status: "error", error });
      throw error;
    }
  }, []);

  const refresh = useCallback(
    (params: { sessionId?: string; kind?: string } = {}) =>
      run(() => options.client.artifactList({ sessionId: params.sessionId, kind: params.kind, scope: options.scope })),
    [options.client, options.scope, run],
  );

  const readMetadata = useCallback(
    (artifactId: string) => run(() => options.client.artifactReadMetadata({ artifactId, scope: options.scope })),
    [options.client, options.scope, run],
  );

  const lineage = useCallback(
    (params: { artifactId?: string; sessionId?: string } = {}) =>
      run(() => options.client.artifactLineage({ artifactId: params.artifactId, sessionId: params.sessionId, scope: options.scope })),
    [options.client, options.scope, run],
  );

  return { ...state, artifacts: state.data, refresh, readMetadata, lineage };
}
