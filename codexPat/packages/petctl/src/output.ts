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
  diagnostics?: Array<{
    name: string;
    status: "passed" | "warning" | "failed";
    reasonCode?: string;
    detail?: string;
  }>;
  probe?: {
    terminalAppName?: string;
    terminalBundleId?: string;
    windowSummary?: string;
    processId?: number;
    processName?: string;
    codexCliVersion?: string;
    ttySummary?: string;
    sessionSummary?: string;
    permissionState?: "granted" | "denied" | "unknown";
    verdict?: "candidate" | "unsupported" | "unavailable";
    reasonCode?: string;
  };
  codexBinding?: {
    candidateId?: string;
    bindingId?: string;
    bindingStatus?: "candidate" | "active" | "stale" | "expired";
    terminalAppName?: string;
    terminalBundleId?: string;
    processId?: number;
    processName?: string;
    codexCliVersion?: string;
    ttySummary?: string;
    sessionSummary?: string;
    petInstanceId?: string;
    candidateObservedAt?: string;
    bindingCreatedAt?: string;
    lastValidatedAt?: string;
    expiresAt?: string;
  };
  codexSession?: {
    instanceId?: string;
    bindingId?: string;
    mode?: "exec" | "tui" | "legacy";
    monitor?: "none" | "jsonl" | "hooks";
    status: "active" | "stale" | "unknown";
    lastEventKind?: string;
    lastSeenAt?: string;
  };
  raw?: unknown;
};

export function formatResult(result: CliResult, pretty: boolean) {
  if (pretty) {
    return JSON.stringify(result, null, 2);
  }
  if (result.ok) {
    if (result.codexBinding) {
      return [
        "codex binding",
        result.codexBinding.bindingStatus ? `status=${result.codexBinding.bindingStatus}` : undefined,
        result.codexBinding.candidateId ? `candidate=${result.codexBinding.candidateId}` : undefined,
        result.codexBinding.bindingId ? `binding=${result.codexBinding.bindingId}` : undefined,
        result.codexBinding.petInstanceId ? `instanceId=${result.codexBinding.petInstanceId}` : undefined
      ].filter(Boolean).join(" ");
    }
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
    if (result.diagnostics) {
      return result.diagnostics
        .map((diagnostic) => [
          `diagnostic=${diagnostic.name}`,
          `status=${diagnostic.status}`,
          diagnostic.reasonCode ? `reasonCode=${diagnostic.reasonCode}` : undefined,
          diagnostic.detail ? `detail="${diagnostic.detail}"` : undefined
        ].filter(Boolean).join(" "))
        .join("\n");
    }
    if (result.probe) {
      return [
        "codex probe active-window",
        result.probe.verdict ? `verdict=${result.probe.verdict}` : undefined,
        result.probe.terminalAppName ? `terminal=${result.probe.terminalAppName}` : undefined,
        result.probe.terminalBundleId ? `bundle=${result.probe.terminalBundleId}` : undefined,
        result.probe.permissionState ? `permission=${result.probe.permissionState}` : undefined,
        result.probe.reasonCode ? `reasonCode=${result.probe.reasonCode}` : undefined
      ].filter(Boolean).join(" ");
    }
    if (result.codexSession) {
      return [
        "codex session",
        `status=${result.codexSession.status}`,
        result.codexSession.instanceId ? `instanceId=${result.codexSession.instanceId}` : undefined,
        result.codexSession.bindingId ? `binding=${result.codexSession.bindingId}` : undefined,
        result.codexSession.mode ? `mode=${result.codexSession.mode}` : undefined,
        result.codexSession.monitor ? `monitor=${result.codexSession.monitor}` : undefined,
        result.codexSession.lastEventKind ? `lastEvent=${result.codexSession.lastEventKind}` : undefined
      ].filter(Boolean).join(" ");
    }
    return `accepted eventId=${result.eventId ?? "unknown"}`;
  }
  if (result.probe) {
    return [
      `error reasonCode=${result.reasonCode ?? result.probe.reasonCode ?? "unknown_error"} reason="${result.reason ?? "probe failed"}"`,
      "codex probe active-window",
      result.probe.verdict ? `verdict=${result.probe.verdict}` : undefined,
      result.probe.terminalAppName ? `terminal=${result.probe.terminalAppName}` : undefined,
      result.probe.terminalBundleId ? `bundle=${result.probe.terminalBundleId}` : undefined,
      result.probe.permissionState ? `permission=${result.probe.permissionState}` : undefined,
      result.probe.reasonCode ? `reasonCode=${result.probe.reasonCode}` : undefined
    ].filter(Boolean).join(" ");
  }
  if (result.diagnostics) {
    return [
      `error reasonCode=${result.reasonCode ?? "unknown_error"} reason="${result.reason ?? "unknown error"}"`,
      ...result.diagnostics.map((diagnostic) => [
        `diagnostic=${diagnostic.name}`,
        `status=${diagnostic.status}`,
        diagnostic.reasonCode ? `reasonCode=${diagnostic.reasonCode}` : undefined,
        diagnostic.detail ? `detail="${diagnostic.detail}"` : undefined
      ].filter(Boolean).join(" "))
    ].join("\n");
  }
  if (result.codexBinding) {
    return [
      `error reasonCode=${result.reasonCode ?? "unknown_error"} reason="${result.reason ?? "codex binding failed"}"`,
      "codex binding",
      result.codexBinding.bindingStatus ? `status=${result.codexBinding.bindingStatus}` : undefined,
      result.codexBinding.candidateId ? `candidate=${result.codexBinding.candidateId}` : undefined,
      result.codexBinding.bindingId ? `binding=${result.codexBinding.bindingId}` : undefined
    ].filter(Boolean).join(" ");
  }
  return `error reasonCode=${result.reasonCode ?? "unknown_error"} reason="${result.reason ?? "unknown error"}"`;
}
