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
};

export function formatResult(result: CliResult, pretty: boolean) {
  if (pretty) {
    return JSON.stringify(result, null, 2);
  }
  if (result.ok) {
    return `accepted eventId=${result.eventId ?? "unknown"}`;
  }
  return `error reasonCode=${result.reasonCode ?? "unknown_error"} reason="${result.reason ?? "unknown error"}"`;
}
