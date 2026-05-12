import { useCallback, useState } from "react";

import type { Scope, ScopeValue } from "../models.js";
import type { HookActionState, HookClientOptions } from "./types.js";

export interface ApprovalRecord {
  approval_id?: string;
  id?: string;
  [key: string]: unknown;
}

export interface UseApprovalsOptions extends HookClientOptions {
  pendingApprovals?: ApprovalRecord[];
}

export interface UseApprovalsResult extends HookActionState<Record<string, unknown>> {
  pendingApprovals: ApprovalRecord[];
  respond(options: { approvalId: string; decision: "approve" | "reject"; reason?: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>>;
}

export function useApprovals(options: UseApprovalsOptions): UseApprovalsResult {
  const [state, setState] = useState<HookActionState<Record<string, unknown>>>({ status: "idle" });

  const respond = useCallback(
    async (params: { approvalId: string; decision: "approve" | "reject"; reason?: string; scope?: Scope | ScopeValue }) => {
      setState({ status: "loading" });
      try {
        const result = await options.client.approvalRespond({
          approvalId: params.approvalId,
          decision: params.decision,
          reason: params.reason,
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

  return { ...state, pendingApprovals: options.pendingApprovals || [], respond };
}
