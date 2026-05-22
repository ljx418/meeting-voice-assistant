export const EXIT_CODES = {
  success: 0,
  genericError: 1,
  tokenMissing: 2,
  localValidation: 3,
  desktopNotRunning: 4,
  unauthorized: 5,
  rejectedByBridge400: 6,
  rateLimited: 7,
  bridgeUnavailable: 8
} as const;

export type CliResult = {
  exitCode: number;
  ok: boolean;
  reasonCode?: string;
  reason?: string;
  eventId?: string;
  queued?: boolean;
  instanceId?: string;
  displayName?: string;
  windowLabel?: string;
  exportCommand?: string;
  instances?: Array<{
    instanceId?: string;
    displayName?: string;
    windowLabel?: string;
    currentState?: string;
    isDefault?: boolean;
  }>;
  raw?: unknown;
};

export function formatResult(result: CliResult, pretty: boolean) {
  if (pretty) {
    return JSON.stringify(result, null, 2);
  }
  if (result.ok) {
    if (result.instanceId) {
      if (!result.displayName && !result.exportCommand) {
        return [
          `detached instanceId=${result.instanceId}`,
          result.windowLabel ? `windowLabel=${result.windowLabel}` : undefined
        ].filter(Boolean).join(" ");
      }
      return [
        `attached instanceId=${result.instanceId}`,
        result.displayName ? `displayName="${result.displayName}"` : undefined,
        result.windowLabel ? `windowLabel=${result.windowLabel}` : undefined,
        result.exportCommand ? `export="${result.exportCommand}"` : undefined
      ].filter(Boolean).join(" ");
    }
    if (result.instances) {
      return result.instances
        .map((instance) => [
          instance.isDefault ? "default" : "instance",
          `instanceId=${instance.instanceId ?? "unknown"}`,
          instance.displayName ? `displayName="${instance.displayName}"` : undefined,
          instance.windowLabel ? `windowLabel=${instance.windowLabel}` : undefined,
          instance.currentState ? `state=${instance.currentState}` : undefined
        ].filter(Boolean).join(" "))
        .join("\n");
    }
    return `accepted eventId=${result.eventId ?? "unknown"}`;
  }
  return `error reasonCode=${result.reasonCode ?? "unknown_error"} reason="${result.reason ?? "unknown error"}"`;
}
