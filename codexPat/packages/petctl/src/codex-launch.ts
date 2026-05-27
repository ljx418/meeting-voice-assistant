import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import type { Readable, Writable } from "node:stream";
import type { PetEventLevel } from "@agent-desktop-pet/pet-protocol";
import { runCodexDoctor } from "./codex-doctor.js";
import { touchManagedSession } from "./codex-session-status.js";
import { attachCodex } from "./instances.js";
import { notify } from "./notify.js";
import { EXIT_CODES, type CliResult } from "./output.js";

export type CodexLaunchOptions = {
  token?: string;
  url?: string;
  name?: string;
  workspaceLabel?: string;
  workspaceHash?: string;
  bin: string;
  monitor?: "none" | "jsonl" | "hooks";
  sessionMode?: "legacy" | "exec" | "tui";
  passthrough: string[];
  noTitle?: boolean;
  spawnImpl?: typeof spawn;
  titleStream?: Writable;
};

type MonitorSummary = {
  mode: "none" | "jsonl" | "hooks";
  sessionMode: "legacy" | "exec" | "tui";
  bindingId: string;
  observedEventTypes: string[];
  mappedStates: PetEventLevel[];
  observedFailureSignal: boolean;
};

export async function launchCodex(options: CodexLaunchOptions): Promise<CliResult> {
  if (options.sessionMode === "tui" && options.monitor === "hooks") {
    const diagnostics = await runCodexDoctor({
      token: options.token,
      url: options.url,
      strict: true,
      includeInstanceEnv: false,
      includeTrustHint: true
    });
    if (!diagnostics.ok) {
      return {
        ...diagnostics,
        reason: "codex managed TUI startup diagnostics failed"
      };
    }
  }

  const attached = await attachCodex({
    token: options.token,
    url: options.url,
    name: options.name,
    workspaceLabel: options.workspaceLabel,
    workspaceHash: options.workspaceHash
  });
  if (!attached.ok || !attached.instanceId) {
    return attached;
  }

  writeTerminalTitle(attached.displayName || options.name || "Codex Cat", attached.instanceId, options);

  const running = await sendCodexState(options, attached.instanceId, "running", "Codex session running", {
    codexBinding: "wrapper",
    codexLauncher: "petctl"
  });
  if (!running.ok) {
    return {
      ...running,
      instanceId: attached.instanceId,
      displayName: attached.displayName,
      windowLabel: attached.windowLabel
    };
  }

  const monitorMode = options.monitor ?? "none";
  const sessionMode = options.sessionMode ?? "legacy";
  const bindingId = `bind_managed_${randomUUID().replace(/-/g, "").slice(0, 24)}`;
  const command = resolveLaunchCommand(options);
  const monitorSummary: MonitorSummary = {
    mode: monitorMode,
    sessionMode,
    bindingId,
    observedEventTypes: [],
    mappedStates: [],
    observedFailureSignal: false
  };
  touchManagedSession({
    instanceId: attached.instanceId,
    bindingId,
    mode: sessionMode,
    monitor: monitorMode,
    status: "active",
    lastEventKind: "session.started"
  });

  const spawnImpl = options.spawnImpl ?? spawn;
  const child = spawnImpl(command.bin, command.args, {
    stdio: monitorMode === "jsonl" ? ["inherit", "pipe", "inherit"] : "inherit",
    env: {
      ...process.env,
      AGENT_DESKTOP_PET_INSTANCE_ID: attached.instanceId,
      AGENT_DESKTOP_PET_BINDING_ID: bindingId,
      AGENT_DESKTOP_PET_SESSION_MODE: sessionMode,
      AGENT_DESKTOP_PET_MONITOR: monitorMode,
      AGENT_DESKTOP_PET_SOURCE_ID: "codex.local",
      AGENT_DESKTOP_PET_SOURCE_KIND: "codex",
      AGENT_DESKTOP_PET_SOURCE_NAME: "Codex"
    }
  });

  const monitorDone = monitorMode === "jsonl"
    ? monitorJsonl(child.stdout, options, attached.instanceId, monitorSummary)
    : Promise.resolve();

  const exit = await new Promise<{ code: number | null; signal: NodeJS.Signals | null }>((resolve) => {
    child.once("error", () => resolve({ code: null, signal: "SIGABRT" }));
    child.once("exit", (code, signal) => resolve({ code, signal }));
  });
  await monitorDone;
  touchManagedSession({
    instanceId: attached.instanceId,
    bindingId,
    mode: sessionMode,
    monitor: monitorMode,
    status: "stale",
    lastEventKind: "process.exit"
  });

  const passed = exit.code === 0 && exit.signal === null;
  if (monitorMode !== "jsonl") {
    const finalEvent = await sendCodexState(
      options,
      attached.instanceId,
      passed ? "success" : "error",
      passed ? "Codex session completed" : "Codex session failed",
      {
        codexBinding: "wrapper",
        codexSessionMode: sessionMode,
        exitCode: exit.code === null ? "none" : String(exit.code),
        signal: exit.signal ?? "none"
      }
    );
    if (!finalEvent.ok) {
      return finalEvent;
    }
  }

  return {
    ok: passed,
    exitCode: passed ? EXIT_CODES.success : EXIT_CODES.genericError,
    reasonCode: passed ? undefined : "codex_process_failed",
    reason: passed ? undefined : "codex process exited with failure",
    instanceId: attached.instanceId,
    displayName: attached.displayName,
    windowLabel: attached.windowLabel,
    raw: {
      monitor: monitorSummary
    }
  };
}

export function resolveLaunchCommand(options: CodexLaunchOptions) {
  if (options.bin === "codex" && options.passthrough[0] === "codex") {
    return { bin: "codex", args: options.passthrough.slice(1) };
  }
  return { bin: options.bin, args: options.passthrough };
}

async function monitorJsonl(
  stdout: Readable | null | undefined,
  options: CodexLaunchOptions,
  instanceId: string,
  summary: MonitorSummary
) {
  if (!stdout) return;
  let buffer = "";
  for await (const chunk of stdout) {
    buffer += Buffer.isBuffer(chunk) ? chunk.toString("utf8") : String(chunk);
    let newline = buffer.indexOf("\n");
    while (newline >= 0) {
      const line = buffer.slice(0, newline);
      buffer = buffer.slice(newline + 1);
      await handleJsonlLine(line, options, instanceId, summary);
      newline = buffer.indexOf("\n");
    }
  }
  if (buffer.trim()) {
    await handleJsonlLine(buffer, options, instanceId, summary);
  }
}

async function handleJsonlLine(
  line: string,
  options: CodexLaunchOptions,
  instanceId: string,
  summary: MonitorSummary
) {
  const parsed = parseJsonObject(line);
  if (!parsed) return;
  const eventType = getEventType(parsed);
  if (!eventType) return;
  if (!summary.observedEventTypes.includes(eventType)) {
    summary.observedEventTypes.push(eventType);
  }
  const mapping = mapJsonlEvent(eventType, summary.observedFailureSignal);
  if (!mapping) return;
  if (mapping.failure) {
    summary.observedFailureSignal = true;
  }
  touchManagedSession({
    instanceId,
    bindingId: summary.bindingId,
    mode: options.sessionMode ?? "legacy",
    monitor: options.monitor ?? "none",
    status: "active",
    lastEventKind: eventType
  });
  if (mapping.level === "success" && summary.observedFailureSignal) {
    return;
  }
  const result = await sendCodexState(options, instanceId, mapping.level, mapping.title, {
    codexBinding: "jsonl-monitor",
    codexLauncher: "petctl",
    codexSessionMode: options.sessionMode ?? "legacy",
    monitorEventType: safeMetadataValue(eventType),
    mappingVersion: "v3.7",
    failureDetected: mapping.failure ? "true" : "false"
  });
  if (result.ok) {
    summary.mappedStates.push(mapping.level);
  }
}

function parseJsonObject(line: string): Record<string, unknown> | undefined {
  const trimmed = line.trim();
  if (!trimmed.startsWith("{")) return undefined;
  try {
    const parsed = JSON.parse(trimmed);
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed as Record<string, unknown> : undefined;
  } catch {
    return undefined;
  }
}

function getEventType(payload: Record<string, unknown>) {
  if (typeof payload.type === "string") return payload.type;
  const event = payload.event;
  if (event && typeof event === "object" && !Array.isArray(event) && typeof (event as { type?: unknown }).type === "string") {
    return (event as { type: string }).type;
  }
  return undefined;
}

function mapJsonlEvent(eventType: string, hasFailure: boolean): { level: PetEventLevel; title: string; failure: boolean } | undefined {
  switch (eventType) {
    case "turn.started":
      return { level: "thinking", title: "Codex turn started", failure: false };
    case "item.started":
      return { level: "running", title: "Codex item running", failure: false };
    case "turn.completed":
      return hasFailure ? undefined : { level: "success", title: "Codex turn completed", failure: false };
    case "turn.failed":
    case "error":
      return { level: "error", title: "Codex turn failed", failure: true };
    default:
      return undefined;
  }
}

function safeMetadataValue(value: string) {
  return value.replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 64);
}

async function sendCodexState(
  options: CodexLaunchOptions,
  instanceId: string,
  level: PetEventLevel,
  title: string,
  metadata: Record<string, string>
) {
  return notify({
    token: options.token,
    url: options.url,
    instance: instanceId,
    event: {
      source: { id: "codex.local", kind: "codex", name: "Codex" },
      level,
      title,
      sound: "none",
      metadata
    }
  });
}

function writeTerminalTitle(name: string, instanceId: string, options: CodexLaunchOptions) {
  if (options.noTitle) return;
  const stream = options.titleStream ?? process.stdout;
  if (!("isTTY" in stream) || stream.isTTY !== true) return;
  const shortId = instanceId.slice(0, 12);
  const safeName = name.replace(/[\u0000-\u001F\u007F]/g, " ").slice(0, 40);
  stream.write(`\u001B]0;Agent Pet: ${safeName} [${shortId}]\u0007`);
}
