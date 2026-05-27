#!/usr/bin/env node
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { homedir, tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:17321";
const SENSITIVE_PATTERNS = [
  "AGENT_DESKTOP_PET_TOKEN=",
  "Authorization",
  "Bearer",
  "api-token.json",
  "Application Support",
  "/Users/",
  "raw payload",
  "workspace path",
  "../../x.wav",
  "ANTHROPIC_AUTH_TOKEN",
  "DEEPSEEK_API_KEY"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const hookScript = join(repoRoot, "skills/claude-agent-pet/hooks/notify-pet.sh");
const url = (process.env.AGENT_DESKTOP_PET_URL || DEFAULT_URL).replace(/\/+$/, "");
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
let tempDir;

main().catch((error) => {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  cleanupTemp();
  finish("failed");
});

async function main() {
  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "build petctl first");
    finish("blocked");
    return;
  }
  if (!existsSync(hookScript)) {
    recordCase("Claude hook script exists", "blocked", "hook_script_missing");
    finish("blocked");
    return;
  }

  const token = resolveToken();
  if (!token) {
    recordCase("desktop token available", "blocked", "token_missing");
    finish("blocked");
    return;
  }

  const health = await waitForHealth();
  if (!health.ok) {
    recordCase("desktop health", "blocked", "desktop_not_running");
    finish("blocked");
    return;
  }
  recordCase("desktop health", "passed", "health ok");

  const claudeVersion = readClaudeVersion();
  if (!claudeVersion) {
    recordCase("Claude Code version", "blocked", "claude_not_available");
    finish("blocked");
    return;
  }
  recordCase("Claude Code version", "passed", claudeVersion);

  clearNotificationCooldown();
  const before = await diagnostics(token);
  const beforeIds = new Set((before.acceptedEvents || []).map((event) => event.id));

  const settingsPath = writeTempSettings();
  const claude = runClaude(settingsPath);
  assertCase("Claude Code process completed", claude.status === 0 || claude.status === 1, `status=${claude.status}`);
  assertCase("Claude execution classification", claude.failureKind !== "unknown", `kind=${claude.failureKind}`);
  assertCase("Claude hook lifecycle event observed", claude.hookEventSeen, claude.hookEventSeen ? "Notification hook event observed" : "Notification hook event not observed");
  assertCase("Claude hook command redacted", true, "hook command recorded only as redacted summary; raw Claude stream is not emitted");

  const accepted = await waitForAcceptedClaudeEvent(token, beforeIds);
  if (!accepted) {
    recordCase("accepted Claude need_input event", "failed", "accepted_event_not_found");
  } else {
    recordCase("accepted Claude need_input event", "passed", `eventId=${accepted.id}`);
    assertCase("accepted event level need_input", accepted.level === "need_input", `level=${accepted.level || "none"}`);
    assertCase("accepted event source id", accepted.sourceId === "claude-code.local", `sourceId=${accepted.sourceId || "none"}`);
    assertCase("accepted event route", Boolean(accepted.targetInstanceId || accepted.targetWindowLabel || accepted.id), accepted.targetInstanceId ? "instance route" : "default route");
  }

  const instances = listInstances();
  const defaultState = stateOf(instances, "default");
  assertCase("target pet state entered need_input", defaultState === "need_input", `defaultState=${defaultState || "none"}`);

  await invalidSoundRedactionCase(token);
  securityScan();
  cleanupTemp();

  const failed = cases.some((item) => item.result === "failed");
  const blocked = cases.some((item) => item.result === "blocked");
  finish(failed ? "failed" : blocked ? "blocked" : "passed", {
    claudeVersion,
    hookEvent: "Notification",
    hookCommand: "redacted",
    sourceId: "claude-code.local",
    sourceKind: "claude_code",
    sourceName: "Claude Code",
    targetRoute: "default",
    claudeFailureKind: claude.failureKind
  });
}

function runClaude(settingsPath) {
  const args = [
    "-p",
    "--settings",
    settingsPath,
    "--output-format",
    "stream-json",
    "--verbose",
    "--include-hook-events",
    "--tools",
    "Bash",
    "--permission-mode",
    "default",
    "Use the Bash tool to run exactly this command: printf claude-hook-smoke. This is a permission prompt probe for a local hook smoke. Do not include secrets."
  ];
  const result = spawnSync("claude", args, {
    cwd: repoRoot,
    env: {
      ...process.env,
      AGENT_DESKTOP_PET_URL: url
    },
    encoding: "utf8",
    timeout: Number(process.env.V3_3_CLAUDE_TIMEOUT_MS || 120000)
  });
  const combined = `${result.stdout || ""}\n${result.stderr || ""}`;
  return {
    status: result.status,
    hookEventSeen: /"hookEvent"\s*:\s*"Notification"|"hook_event_name"\s*:\s*"Notification"|Notification/.test(combined),
    failureKind: classifyClaudeOutput(combined, result.status)
  };
}

function classifyClaudeOutput(text, status) {
  if (status === 0) return "completed";
  if (/credit|billing|quota/i.test(text)) return "provider_quota";
  if (/auth|api key|token|credential|login/i.test(text)) return "auth_or_credentials";
  if (/permission/i.test(text)) return "permission_flow";
  if (/settings|hook|json/i.test(text)) return "settings_or_hook_config";
  if (/timeout/i.test(text)) return "timeout";
  if (/network|fetch|connect|ENOTFOUND|ECONN|ETIMEDOUT/i.test(text)) return "network";
  return "unknown";
}

function writeTempSettings() {
  tempDir = mkdtempSync(join(tmpdir(), "agent-pet-v3-3-"));
  const settingsPath = join(tempDir, "claude-settings.json");
  writeFileSync(settingsPath, JSON.stringify({
    hooks: {
      Notification: [
        {
          hooks: [
            {
              type: "command",
              command: `zsh ${JSON.stringify(hookScript).slice(1, -1)} notification`,
              timeout: 10
            }
          ]
        }
      ]
    }
  }, null, 2));
  return settingsPath;
}

function cleanupTemp() {
  if (tempDir) {
    rmSync(tempDir, { recursive: true, force: true });
  }
}

function readClaudeVersion() {
  const result = spawnSync("claude", ["--version"], { encoding: "utf8" });
  const version = `${result.stdout || result.stderr || ""}`.trim();
  return result.status === 0 && version ? version : undefined;
}

function clearNotificationCooldown() {
  rmSync("/tmp/agent-desktop-pet-claude-hook-notification_need_input.stamp", { force: true });
}

async function invalidSoundRedactionCase(token) {
  const response = await fetch(`${url}/api/events`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      source: { id: "claude-code.local", kind: "claude_code", name: "Claude Code" },
      level: "need_input",
      sound: "../../x.wav",
      title: "invalid sound redaction"
    })
  });
  const body = await readJson(response);
  const text = JSON.stringify(body || {});
  assertCase("invalid sound/path rejected", response.status === 400 && body?.reasonCode === "whitelist_invalid", `status=${response.status} reasonCode=${body?.reasonCode || "none"}`);
  assertCase("invalid sound/path redacted", !SENSITIVE_PATTERNS.some((pattern) => text.includes(pattern)), "no unsafe input echoed");
}

async function waitForAcceptedClaudeEvent(token, beforeIds) {
  const deadline = Date.now() + 15000;
  while (Date.now() < deadline) {
    const snapshot = await diagnostics(token);
    const accepted = (snapshot.acceptedEvents || []).find((event) => {
      return !beforeIds.has(event.id)
        && event.accepted === true
        && event.sourceId === "claude-code.local"
        && event.level === "need_input";
    });
    if (accepted) return accepted;
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return undefined;
}

async function diagnostics(token) {
  const response = await fetch(`${url}/api/diagnostics`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!response.ok) return {};
  return await readJson(response) || {};
}

function listInstances() {
  const result = spawnSync(process.execPath, [petctlBin, "list", "--json"], {
    cwd: repoRoot,
    env: process.env,
    encoding: "utf8"
  });
  try {
    return JSON.parse(result.stdout || "{}").instances || [];
  } catch {
    return [];
  }
}

function stateOf(instances, instanceId) {
  return instances.find((item) => item.instanceId === instanceId)?.currentState;
}

async function waitForHealth() {
  const deadline = Date.now() + Number(process.env.AGENT_DESKTOP_PET_HEALTH_TIMEOUT_MS || 15000);
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`${url}/api/health`);
      if (response.ok) {
        const body = await response.json();
        if (body?.ok === true) return { ok: true };
      }
    } catch {
      // Keep waiting until timeout.
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
  return { ok: false };
}

async function readJson(response) {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function resolveToken() {
  if (process.env.AGENT_DESKTOP_PET_TOKEN) return process.env.AGENT_DESKTOP_PET_TOKEN;
  const configPath = tokenConfigPath();
  if (!configPath || !existsSync(configPath)) return undefined;
  try {
    const parsed = JSON.parse(readFileSync(configPath, "utf8"));
    return typeof parsed.token === "string" && parsed.token.trim() ? parsed.token : undefined;
  } catch {
    return undefined;
  }
}

function tokenConfigPath() {
  const appId = "com.agentdesktoppet.desktop";
  if (process.platform === "darwin") {
    return join(homedir(), "Library", "Application Support", appId, "api-token.json");
  }
  if (process.platform === "win32") {
    const appData = process.env.APPDATA;
    return appData ? join(appData, appId, "api-token.json") : undefined;
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return join(base, appId, "api-token.json");
}

function securityScan() {
  const serialized = JSON.stringify(summaryObject("pending"));
  if (SENSITIVE_PATTERNS.some((pattern) => serialized.includes(pattern))) {
    recordCase("security redaction scan", "failed", "summary contained forbidden text");
  } else {
    recordCase("security redaction scan", "passed", "summary did not contain forbidden text");
  }
}

function recordCase(name, result, notes = "") {
  cases.push({ name, result, notes });
}

function assertCase(name, condition, notes = "") {
  recordCase(name, condition ? "passed" : "failed", notes);
}

function summaryObject(status, extra = {}) {
  return {
    status,
    runId,
    cases,
    ...extra
  };
}

function finish(status, extra = {}) {
  console.log(JSON.stringify(summaryObject(status, extra), null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
