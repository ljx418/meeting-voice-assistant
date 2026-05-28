import { CAT_STATE_CONFIG, type CatState } from "../pet-states";
import type { AssetManifest, CoreActionId, SafeActionId, OptionalActionId } from "../assets/asset-manifest";

export type CatActionResolutionWarning = {
  code: "optional_action_fallback" | "success_preserved_active_priority";
  actionId: string;
  fallbackActionId: SafeActionId;
};

export type CatActionResolution = {
  actionId: SafeActionId;
  playback: {
    loop: boolean;
    priority: "base" | "transient" | "urgent";
    durationMs?: number;
  };
  warnings: CatActionResolutionWarning[];
};

export function resolveCatAction(
  requestedState: CatState,
  manifest: AssetManifest,
  options: { currentState?: CatState; optionalActionId?: OptionalActionId } = {}
): CatActionResolution {
  const warnings: CatActionResolutionWarning[] = [];
  const stateAction = preservePriorityState(requestedState, options.currentState, warnings);
  const requestedAction = options.optionalActionId ?? stateAction;
  const actionId = manifest.actions[requestedAction] ? requestedAction : fallbackAction(requestedAction, warnings);
  const action = manifest.actions[actionId] ?? manifest.actions.idle;

  return {
    actionId,
    playback: {
      loop: action?.loop ?? true,
      priority: action?.priority ?? "base",
      durationMs: action?.durationMs
    },
    warnings
  };
}

function preservePriorityState(
  requestedState: CatState,
  currentState: CatState | undefined,
  warnings: CatActionResolutionWarning[]
): CoreActionId {
  if (
    requestedState === "success" &&
    (currentState === "error" || currentState === "need_input") &&
    CAT_STATE_CONFIG[currentState].priority > CAT_STATE_CONFIG.success.priority
  ) {
    warnings.push({
      code: "success_preserved_active_priority",
      actionId: "success",
      fallbackActionId: currentState
    });
    return currentState;
  }
  return requestedState;
}

function fallbackAction(actionId: SafeActionId, warnings: CatActionResolutionWarning[]): CoreActionId {
  warnings.push({
    code: "optional_action_fallback",
    actionId,
    fallbackActionId: "idle"
  });
  return "idle";
}

