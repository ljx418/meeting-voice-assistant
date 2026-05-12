import { useCallback, useState } from "react";

import type { Scope, ScopeValue } from "../models.js";
import type { HookActionState, HookClientOptions } from "./types.js";

export interface StartTurnOptions {
  input: string;
  sessionId?: string;
  domain?: string;
  scope?: Scope | ScopeValue;
}

export interface UseTurnResult extends HookActionState<Record<string, unknown>> {
  turn?: Record<string, unknown>;
  startTurn(options: StartTurnOptions): Promise<Record<string, unknown>>;
}

export function useTurn(options: HookClientOptions): UseTurnResult {
  const [state, setState] = useState<HookActionState<Record<string, unknown>>>({ status: "idle" });

  const startTurn = useCallback(
    async (params: StartTurnOptions) => {
      setState({ status: "loading" });
      try {
        const result = await options.client.turnStart({
          input: params.input,
          sessionId: params.sessionId,
          domain: params.domain,
          scope: params.scope ?? options.scope,
        });
        setState({ status: "success", data: result });
        return result;
      } catch (error) {
        setState({ status: "error", error });
        throw error;
      }
    },
    [options.client, options.scope],
  );

  return { ...state, turn: state.data, startTurn };
}
