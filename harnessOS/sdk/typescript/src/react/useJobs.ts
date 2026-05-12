import { useCallback, useState } from "react";

import type { HookActionState, HookClientOptions } from "./types.js";

export interface UseJobsResult extends HookActionState<Record<string, unknown>> {
  jobs?: Record<string, unknown>;
  refresh(params?: { sessionId?: string; status?: string }): Promise<Record<string, unknown>>;
  get(jobId: string): Promise<Record<string, unknown>>;
}

export function useJobs(options: HookClientOptions): UseJobsResult {
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
    (params: { sessionId?: string; status?: string } = {}) =>
      run(() => options.client.jobList({ sessionId: params.sessionId, status: params.status, scope: options.scope })),
    [options.client, options.scope, run],
  );

  const get = useCallback((jobId: string) => run(() => options.client.jobGet({ jobId, scope: options.scope })), [options.client, options.scope, run]);

  return { ...state, jobs: state.data, refresh, get };
}
