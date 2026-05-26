import { spawnSync, type SpawnSyncReturns } from "node:child_process";
import { createHash } from "node:crypto";
import { EXIT_CODES, type CliResult } from "./output.js";

export type CodexProbeTerminal = "terminal" | "iterm2";

export type CodexProbeOptions = {
  terminal: CodexProbeTerminal;
  spawnImpl?: typeof spawnSync;
  platform?: NodeJS.Platform;
};

type ProbeInfo = {
  appName: string;
  bundleId: string;
  processId?: number;
  processName?: string;
  tty?: string;
  sessionId?: string;
};

type ProbeResult = SpawnSyncReturns<string>;

const TERMINALS = {
  terminal: {
    appName: "Terminal",
    bundleId: "com.apple.Terminal"
  },
  iterm2: {
    appName: "iTerm2",
    bundleId: "com.googlecode.iterm2"
  }
} as const;

export async function runCodexProbe(options: CodexProbeOptions): Promise<CliResult> {
  const platform = options.platform ?? process.platform;
  if (platform !== "darwin") {
    return probeFailure("unsupported_platform", "codex active-window probe supports macOS only", {
      terminalAppName: terminalConfig(options.terminal).appName,
      terminalBundleId: terminalConfig(options.terminal).bundleId,
      permissionState: "unknown",
      verdict: "unsupported",
      reasonCode: "unsupported_platform"
    });
  }

  const spawnImpl = options.spawnImpl ?? spawnSync;
  const infoResult = readFocusedTerminal(options.terminal, spawnImpl);
  if (!infoResult.ok) {
    return infoResult.result;
  }
  const info = infoResult.info;
  const baseProbe = {
    terminalAppName: info.appName,
    terminalBundleId: info.bundleId,
    windowSummary: "focused-window",
    processId: info.processId,
    processName: safeProcessName(info.processName),
    ttySummary: redactedSummary(info.tty, "tty"),
    sessionSummary: redactedSummary(info.sessionId ?? info.tty, "session"),
    permissionState: "granted" as const
  };

  const codex = findCodexProcess(info.tty, spawnImpl);
  if (!codex.found) {
    return probeFailure("codex_process_not_found", "codex process not found for focused terminal", {
      ...baseProbe,
      verdict: "unavailable",
      reasonCode: "codex_process_not_found"
    });
  }

  return {
    ok: true,
    exitCode: EXIT_CODES.success,
    probe: {
      ...baseProbe,
      processId: codex.processId ?? baseProbe.processId,
      processName: "codex",
      codexCliVersion: codexVersion(spawnImpl),
      verdict: "candidate",
      reasonCode: "candidate_detected"
    }
  };
}

function readFocusedTerminal(terminal: CodexProbeTerminal, spawnImpl: typeof spawnSync): { ok: true; info: ProbeInfo } | { ok: false; result: CliResult } {
  const config = terminalConfig(terminal);
  const script = terminal === "terminal" ? terminalScript() : iterm2Script();
  const result = spawnImpl("osascript", ["-e", script], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 64 * 1024
  }) as ProbeResult;

  if (result.status !== 0) {
    const reasonCode = permissionDenied(result) ? "permission_denied" : "probe_unavailable";
    return {
      ok: false,
      result: probeFailure(reasonCode, reasonCode === "permission_denied" ? "permission denied" : "active window probe unavailable", {
        terminalAppName: config.appName,
        terminalBundleId: config.bundleId,
        permissionState: reasonCode === "permission_denied" ? "denied" : "unknown",
        verdict: "unavailable",
        reasonCode
      })
    };
  }

  const parsed = parseProbeInfo(String(result.stdout || ""));
  if (!parsed || parsed.bundleId !== config.bundleId) {
    return {
      ok: false,
      result: probeFailure("unsupported_terminal", "focused app is not the requested terminal", {
        terminalAppName: parsed?.appName ?? config.appName,
        terminalBundleId: parsed?.bundleId ?? config.bundleId,
        permissionState: "granted",
        verdict: "unsupported",
        reasonCode: "unsupported_terminal"
      })
    };
  }

  if (!parsed.tty) {
    return {
      ok: false,
      result: probeFailure("session_identity_unavailable", "terminal session identity unavailable", {
        terminalAppName: parsed.appName,
        terminalBundleId: parsed.bundleId,
        windowSummary: "focused-window",
        processId: parsed.processId,
        processName: safeProcessName(parsed.processName),
        permissionState: "granted",
        verdict: "unavailable",
        reasonCode: "session_identity_unavailable"
      })
    };
  }

  return { ok: true, info: parsed };
}

function terminalScript() {
  return [
    "tell application \"System Events\"",
    "set frontProc to first application process whose frontmost is true",
    "set appName to name of frontProc",
    "set bundleId to bundle identifier of frontProc",
    "set pidValue to unix id of frontProc",
    "end tell",
    "set ttyValue to \"\"",
    "if bundleId is \"com.apple.Terminal\" then",
    "tell application \"Terminal\"",
    "if (count of windows) > 0 then set ttyValue to tty of selected tab of front window",
    "end tell",
    "end if",
    "return appName & \"\\n\" & bundleId & \"\\n\" & pidValue & \"\\n\" & ttyValue"
  ].join("\n");
}

function iterm2Script() {
  return [
    "tell application \"System Events\"",
    "set frontProc to first application process whose frontmost is true",
    "set appName to name of frontProc",
    "set bundleId to bundle identifier of frontProc",
    "set pidValue to unix id of frontProc",
    "end tell",
    "set ttyValue to \"\"",
    "if bundleId is \"com.googlecode.iterm2\" then",
    "tell application \"iTerm2\"",
    "if (count of windows) > 0 then set ttyValue to tty of current session of current window",
    "end tell",
    "end if",
    "return appName & \"\\n\" & bundleId & \"\\n\" & pidValue & \"\\n\" & ttyValue"
  ].join("\n");
}

function parseProbeInfo(stdout: string): ProbeInfo | undefined {
  const lines = stdout.split(/\r?\n/).map((line) => line.trim());
  const [appName, bundleId, pid, tty] = lines;
  if (!safeIdentifier(appName) || !safeBundleId(bundleId)) return undefined;
  const processId = Number(pid);
  return {
    appName,
    bundleId,
    processId: Number.isInteger(processId) && processId > 0 ? processId : undefined,
    processName: appName,
    tty: safeTty(tty),
    sessionId: safeTty(tty)
  };
}

function findCodexProcess(tty: string | undefined, spawnImpl: typeof spawnSync): { found: boolean; processId?: number } {
  if (!tty) return { found: false };
  const ttyName = tty.replace(/^\/dev\//, "");
  if (!/^[A-Za-z0-9._/-]{1,64}$/.test(ttyName)) return { found: false };
  const result = spawnImpl("ps", ["-axo", "pid=,comm=,tty="], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 512 * 1024
  }) as ProbeResult;
  if (result.status !== 0) return { found: false };

  const nodeCandidatePids: number[] = [];
  for (const line of String(result.stdout || "").split(/\r?\n/)) {
    const match = line.trim().match(/^(\d+)\s+(\S+)\s+(\S+)$/);
    if (!match) continue;
    const [, pid, command, processTty] = match;
    const commandName = command.split("/").pop() ?? command;
    if (processTty !== ttyName) continue;
    const processId = Number(pid);
    if (!Number.isInteger(processId) || processId <= 0) continue;
    if (isCodexCommandName(commandName)) {
      return { found: true, processId };
    }
    if (isNodeWrapperCommandName(commandName)) {
      nodeCandidatePids.push(processId);
    }
  }

  for (const processId of nodeCandidatePids) {
    if (processArgsLookLikeCodex(processId, spawnImpl)) {
      return { found: true, processId };
    }
  }

  return { found: false };
}

function isCodexCommandName(commandName: string) {
  return /^codex(?:\.js)?$/i.test(commandName);
}

function isNodeWrapperCommandName(commandName: string) {
  return /^(?:node|nodejs|npm|npx|env|n)$/i.test(commandName);
}

function processArgsLookLikeCodex(processId: number, spawnImpl: typeof spawnSync) {
  const result = spawnImpl("ps", ["-p", String(processId), "-o", "args="], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 64 * 1024
  }) as ProbeResult;
  if (result.status !== 0) return false;
  const args = String(result.stdout || "");
  return codexArgsSignature(args);
}

function codexArgsSignature(args: string) {
  const normalized = args.replace(/\\/g, "/").toLowerCase();
  return (
    normalized.includes("@openai/codex") ||
    normalized.includes("/codex/bin/") ||
    normalized.includes("/codex-cli/")
  );
}

function codexVersion(spawnImpl: typeof spawnSync): string | undefined {
  const result = spawnImpl("codex", ["--version"], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 32 * 1024
  }) as ProbeResult;
  if (result.status !== 0) return undefined;
  const version = String(result.stdout || result.stderr || "").trim();
  return safeVersion(version);
}

function terminalConfig(terminal: CodexProbeTerminal) {
  return TERMINALS[terminal];
}

function probeFailure(reasonCode: string, reason: string, probe: NonNullable<CliResult["probe"]>): CliResult {
  return {
    ok: false,
    exitCode: EXIT_CODES.localValidation,
    reasonCode,
    reason,
    probe
  };
}

function permissionDenied(result: ProbeResult) {
  const stderr = String(result.stderr || "").toLowerCase();
  return stderr.includes("not authorized") || stderr.includes("not allowed") || stderr.includes("permission") || stderr.includes("accessibility");
}

function redactedSummary(value: string | undefined, prefix: string) {
  if (!value) return undefined;
  const safe = value.replace(/^\/dev\//, "");
  if (!/^[A-Za-z0-9._/-]{1,64}$/.test(safe)) return undefined;
  const digest = createHash("sha256").update(safe).digest("hex").slice(0, 12);
  return `${prefix}_${digest}`;
}

function safeProcessName(value: string | undefined) {
  if (!value) return undefined;
  const safe = value.replace(/[^A-Za-z0-9 ._-]/g, "").trim().slice(0, 40);
  return safe || undefined;
}

function safeIdentifier(value: string | undefined) {
  return typeof value === "string" && /^[A-Za-z0-9 ._-]{1,80}$/.test(value);
}

function safeBundleId(value: string | undefined) {
  return typeof value === "string" && /^[A-Za-z0-9.-]{1,120}$/.test(value);
}

function safeTty(value: string | undefined) {
  if (!value) return undefined;
  return /^\/dev\/[A-Za-z0-9._/-]{1,64}$/.test(value) ? value : undefined;
}

function safeVersion(value: string | undefined) {
  if (!value) return undefined;
  const safe = value.replace(/[^A-Za-z0-9 ._/-]/g, "").trim().slice(0, 80);
  if (!safe || safe.includes("/Users/")) return undefined;
  return safe;
}
