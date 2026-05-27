#!/usr/bin/env node
import { appendFileSync, existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";

const EVENT = process.argv[2] || "";
const SUPPORTED_EVENTS = new Set([
  "SessionStart",
  "UserPromptSubmit",
  "PreToolUse",
  "PermissionRequest",
  "PostToolUse",
  "PreCompact",
  "PostCompact",
  "SubagentStart",
  "SubagentStop",
  "Stop"
]);
const COOLDOWN_MS = {
  SessionStart: 1000,
  UserPromptSubmit: 500,
  PreToolUse: 1500,
  PermissionRequest: 0,
  PostToolUse: 0,
  Stop: 800
};
const TURN_ISSUE_TTL_MS = 10 * 60 * 1000;
const STATE_DIR = join(tmpdir(), "agent-desktop-pet-codex-hook-v3-4");
const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");

main().catch((error) => {
  debug({ result: "error", reason: error instanceof Error ? error.message : "unknown" });
  finish();
});

async function main() {
  const stdin = await readStdin({
    idleTimeoutMs: 250,
    maxTimeoutMs: 1200
  });
  const payload = parseJson(stdin);
  const instanceId = process.env.AGENT_DESKTOP_PET_INSTANCE_ID || "";

  if (!SUPPORTED_EVENTS.has(EVENT)) {
    debug({ result: "noop", reason: "unsupported_event", hookEvent: safeValue(EVENT) });
    finish();
    return;
  }
  if (!instanceId) {
    debug({ result: "noop", reason: "instance_missing", hookEvent: EVENT });
    finish();
    return;
  }
  if (!isValidInstanceId(instanceId)) {
    debug({ result: "noop", reason: "instance_invalid", hookEvent: EVENT });
    finish();
    return;
  }
  if (!existsSync(petctlBin)) {
    debug({ result: "noop", reason: "petctl_missing", hookEvent: EVENT });
    finish();
    return;
  }
  touchSession({
    instanceId,
    bindingId: process.env.AGENT_DESKTOP_PET_BINDING_ID,
    mode: process.env.AGENT_DESKTOP_PET_SESSION_MODE,
    monitor: process.env.AGENT_DESKTOP_PET_MONITOR,
    lastEventKind: EVENT
  });

  const mapping = mapHook(EVENT, payload, instanceId);
  if (!mapping) {
    debug({ result: "noop", reason: "no_mapping", hookEvent: EVENT, ...payloadSummary(payload) });
    finish();
    return;
  }

  if (isDeduped(instanceId, EVENT, mapping.level)) {
    debug({ result: "noop", reason: "cooldown", hookEvent: EVENT, level: mapping.level });
    finish();
    return;
  }

  const result = spawnSync(process.execPath, [
    petctlBin,
    "notify",
    "--source-id",
    "codex.local",
    "--source-kind",
    "codex",
    "--source-name",
    "Codex",
    "--level",
    mapping.level,
    "--title",
    mapping.title,
    "--sound",
    "none",
    "--metadata",
    `hookEvent=${EVENT}`,
    "--metadata",
    "codexBinding=hooks",
    "--metadata",
    "mappingVersion=v3.4",
    "--metadata",
    `failureDetected=${mapping.failureDetected ? "true" : "false"}`
  ], {
    cwd: repoRoot,
    env: process.env,
    encoding: "utf8",
    timeout: 2500,
    stdio: ["ignore", "pipe", "pipe"]
  });

  debug({
    result: result.status === 0 ? "notified" : "notify_failed",
    hookEvent: EVENT,
    level: mapping.level,
    status: String(result.status ?? "none")
  });
  finish();
}

function mapHook(event, payload, instanceId) {
  switch (event) {
    case "SessionStart":
      clearTurnIssue(instanceId);
      return { level: "running", title: "Codex session started", failureDetected: false };
    case "UserPromptSubmit":
      clearTurnIssue(instanceId);
      return { level: "thinking", title: "Codex thinking", failureDetected: false };
    case "PreToolUse":
      return { level: "running", title: "Codex tool running", failureDetected: false };
    case "PermissionRequest":
      return { level: "need_input", title: "Codex needs approval", failureDetected: false };
    case "PostToolUse":
      if (detectFailure(payload)) {
        markTurnIssue(instanceId, "failure");
        return { level: "error", title: "Codex tool failed", failureDetected: true };
      }
      if (detectWarning(payload)) {
        markTurnIssue(instanceId, "warning");
      }
      return null;
    case "Stop":
      if (hasRecentTurnIssue(instanceId)) {
        return null;
      }
      return { level: "success", title: "Codex turn completed", failureDetected: false };
    default:
      return null;
  }
}

function detectWarning(payload) {
  if (!payload || typeof payload !== "object") return false;
  if (typeof payload.status === "string" && payload.status.toLowerCase() === "warning") return true;
  if ("warning" in payload && payload.warning) return true;
  const result = payload.result;
  if (result && typeof result === "object") {
    if (typeof result.status === "string" && result.status.toLowerCase() === "warning") return true;
    if ("warning" in result && result.warning) return true;
  }
  return false;
}

function markTurnIssue(instanceId, kind) {
  try {
    mkdirSync(STATE_DIR, { recursive: true });
    writeFileSync(turnIssuePath(instanceId), JSON.stringify({ at: Date.now(), kind }));
  } catch {
    // Ignore diagnostics state failures; never block Codex hooks.
  }
}

function clearTurnIssue(instanceId) {
  try {
    mkdirSync(STATE_DIR, { recursive: true });
    writeFileSync(turnIssuePath(instanceId), JSON.stringify({ at: 0, kind: "clear" }));
  } catch {
    // Ignore diagnostics state failures; never block Codex hooks.
  }
}

function hasRecentTurnIssue(instanceId) {
  try {
    const path = turnIssuePath(instanceId);
    if (!existsSync(path)) return false;
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    return typeof parsed.at === "number" && Date.now() - parsed.at < TURN_ISSUE_TTL_MS && parsed.kind !== "clear";
  } catch {
    return false;
  }
}

function turnIssuePath(instanceId) {
  const key = createHash("sha256").update(`${instanceId}:turn-issue`).digest("hex").slice(0, 32);
  return join(STATE_DIR, `${key}.issue.json`);
}

function detectFailure(payload) {
  if (!payload || typeof payload !== "object") return false;
  // Do not infer tool failure from tool_input; observed Codex PostToolUse payloads omit result fields.
  if (typeof payload.exitCode === "number" && payload.exitCode !== 0) return true;
  if (typeof payload.exit_code === "number" && payload.exit_code !== 0) return true;
  if (payload.success === false) return true;
  if (typeof payload.status === "string" && ["error", "failed", "failure"].includes(payload.status.toLowerCase())) return true;
  if ("error" in payload && payload.error) return true;
  const result = payload.result;
  if (result && typeof result === "object") {
    if (typeof result.exitCode === "number" && result.exitCode !== 0) return true;
    if (typeof result.exit_code === "number" && result.exit_code !== 0) return true;
    if (result.success === false) return true;
    if (typeof result.status === "string" && ["error", "failed", "failure"].includes(result.status.toLowerCase())) return true;
    if ("error" in result && result.error) return true;
  }
  for (const key of ["tool_result", "tool_response", "response"]) {
    const nested = payload[key];
    if (nested && typeof nested === "object") {
      if (typeof nested.exitCode === "number" && nested.exitCode !== 0) return true;
      if (typeof nested.exit_code === "number" && nested.exit_code !== 0) return true;
      if (nested.success === false) return true;
      if (typeof nested.status === "string" && ["error", "failed", "failure"].includes(nested.status.toLowerCase())) return true;
      if ("error" in nested && nested.error) return true;
    }
  }
  return false;
}

function isDeduped(instanceId, event, level) {
  const cooldown = COOLDOWN_MS[event] ?? 0;
  if (cooldown <= 0) return false;
  try {
    mkdirSync(STATE_DIR, { recursive: true });
    const key = createHash("sha256").update(`${instanceId}:${event}:${level}`).digest("hex").slice(0, 32);
    const path = join(STATE_DIR, `${key}.json`);
    const now = Date.now();
    if (existsSync(path)) {
      const parsed = JSON.parse(readFileSync(path, "utf8"));
      if (typeof parsed.at === "number" && now - parsed.at < cooldown) return true;
    }
    writeFileSync(path, JSON.stringify({ at: now }));
  } catch {
    return false;
  }
  return false;
}

function readStdin({ idleTimeoutMs, maxTimeoutMs }) {
  return new Promise((resolvePromise) => {
    const chunks = [];
    let resolved = false;
    let idleTimer;

    const resolveOnce = () => {
      if (resolved) return;
      resolved = true;
      clearTimeout(idleTimer);
      clearTimeout(maxTimer);
      resolvePromise(Buffer.concat(chunks).toString("utf8"));
    };

    const bumpIdleTimer = () => {
      clearTimeout(idleTimer);
      idleTimer = setTimeout(resolveOnce, idleTimeoutMs);
      idleTimer.unref?.();
    };

    const maxTimer = setTimeout(resolveOnce, maxTimeoutMs);
    maxTimer.unref?.();

    process.stdin.on("data", (chunk) => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
      bumpIdleTimer();
    });
    process.stdin.on("end", resolveOnce);
    process.stdin.on("error", resolveOnce);
    process.stdin.resume();
    bumpIdleTimer();
  });
}

function parseJson(text) {
  if (!text.trim()) return {};
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function isValidInstanceId(value) {
  return /^[A-Za-z0-9._-]{1,64}$/.test(value) && !value.includes("..");
}

function touchSession({ instanceId, bindingId, mode, monitor, lastEventKind }) {
  if (!isValidInstanceId(instanceId) || !isSafeBindingId(bindingId)) return;
  const record = {
    instanceId,
    bindingId,
    mode: mode === "exec" || mode === "tui" || mode === "legacy" ? mode : "tui",
    monitor: monitor === "none" || monitor === "jsonl" || monitor === "hooks" ? monitor : "hooks",
    status: "active",
    lastEventKind: /^[A-Za-z0-9._:-]{1,64}$/.test(lastEventKind || "") ? lastEventKind : "unknown",
    lastSeenAt: new Date().toISOString()
  };
  const path = sessionStorePath();
  const store = readSessionStore(path);
  store.sessions = [
    ...store.sessions.filter((item) => item.instanceId !== instanceId && item.bindingId !== bindingId),
    record
  ].slice(-50);
  try {
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, `${JSON.stringify(store, null, 2)}\n`, { mode: 0o600 });
  } catch {
    // Ignore status store failures; never block Codex hooks.
  }
}

function readSessionStore(path) {
  if (!existsSync(path)) return { sessions: [] };
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8"));
    return { sessions: Array.isArray(parsed.sessions) ? parsed.sessions : [] };
  } catch {
    return { sessions: [] };
  }
}

function sessionStorePath() {
  if (process.env.AGENT_DESKTOP_PET_SESSION_STORE) return process.env.AGENT_DESKTOP_PET_SESSION_STORE;
  const appId = "com.agentdesktoppet.desktop";
  if (process.platform === "darwin") {
    return join(homedir(), "Library", "Application Support", appId, "codex-sessions.json");
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return join(base, appId, "codex-sessions.json");
}

function isSafeBindingId(value) {
  return typeof value === "string" && /^bind_[A-Za-z0-9_]{1,80}$/.test(value);
}

function safeValue(value) {
  return String(value).replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 64);
}

function debug(summary) {
  if (process.env.CODEX_PET_HOOK_DEBUG !== "1") return;
  const safe = Object.fromEntries(Object.entries(summary).map(([key, value]) => [key, safeValue(value)]));
  const line = `${JSON.stringify(safe)}\n`;
  process.stderr.write(line);
  if (process.env.CODEX_PET_HOOK_DEBUG_FILE) {
    try {
      appendFileSync(process.env.CODEX_PET_HOOK_DEBUG_FILE, line);
    } catch {
      // Ignore debug sink failures; never block Codex hooks.
    }
  }
}

function payloadSummary(payload) {
  if (!payload || typeof payload !== "object") return {};
  const result = payload.result && typeof payload.result === "object" ? payload.result : {};
  const toolResult = payload.tool_result && typeof payload.tool_result === "object" ? payload.tool_result : {};
  const toolResponse = payload.tool_response && typeof payload.tool_response === "object" ? payload.tool_response : {};
  return {
    payloadKeys: Object.keys(payload).sort().slice(0, 12).join("_"),
    statusField: typeof payload.status === "string" ? payload.status : "none",
    exitCodeField: typeof payload.exitCode === "number" ? String(payload.exitCode) : typeof payload.exit_code === "number" ? String(payload.exit_code) : "none",
    resultKeys: Object.keys(result).sort().slice(0, 12).join("_"),
    resultStatusField: typeof result.status === "string" ? result.status : "none",
    resultExitCodeField: typeof result.exitCode === "number" ? String(result.exitCode) : typeof result.exit_code === "number" ? String(result.exit_code) : "none",
    toolResultKeys: Object.keys(toolResult).sort().slice(0, 12).join("_"),
    toolResultStatusField: typeof toolResult.status === "string" ? toolResult.status : "none",
    toolResultExitCodeField: typeof toolResult.exitCode === "number" ? String(toolResult.exitCode) : typeof toolResult.exit_code === "number" ? String(toolResult.exit_code) : "none",
    toolResponseKeys: Object.keys(toolResponse).sort().slice(0, 12).join("_"),
    toolResponseStatusField: typeof toolResponse.status === "string" ? toolResponse.status : "none",
    toolResponseExitCodeField: typeof toolResponse.exitCode === "number" ? String(toolResponse.exitCode) : typeof toolResponse.exit_code === "number" ? String(toolResponse.exit_code) : "none"
  };
}

function finish() {
  process.stdout.write("{}\n");
}
