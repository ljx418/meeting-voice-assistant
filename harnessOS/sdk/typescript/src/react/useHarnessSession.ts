import { useCallback, useState } from "react";

import type { Scope, ScopeValue } from "../models.js";
import type { HookActionState, HookClientOptions } from "./types.js";

export interface StartSessionOptions {
  model?: string;
  scope?: Scope | ScopeValue;
}

export interface UseHarnessSessionResult extends HookActionState<Record<string, unknown>> {
  session?: Record<string, unknown>;
  startSession(options?: StartSessionOptions): Promise<Record<string, unknown>>;
}

export function useHarnessSession(options: HookClientOptions): UseHarnessSessionResult {
  const [state, setState] = useState<HookActionState<Record<string, unknown>>>({ status: "idle" });

  const startSession = useCallback(
    async (params: StartSessionOptions = {}) => {
      setState({ status: "loading" });
      try {
        const result = await options.client.sessionStart({ model: params.model, scope: params.scope ?? options.scope });
        setState({ status: "success", data: result });
        return result;
      } catch (error) {
        setState({ status: "error", error });
        throw error;
      }
    },
    [options.client, options.scope],
  );

  return { ...state, session: state.data, startSession };
}
