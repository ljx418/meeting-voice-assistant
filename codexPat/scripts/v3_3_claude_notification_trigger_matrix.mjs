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
  "config path",
  "../../x.wav",
  "ANTHROPIC_AUTH_TOKEN",
  "DEEPSEEK_API_KEY"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const hookScript = join(repoRoot, "skills/claude-agent-pet/hooks/notify-pet.sh");
const url = (process.env.AGENT_DESKTOP_PET_URL || DEFAULT_URL).replace(/\/+$/, "");
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
const scenarios = [];
let tempDir;

main().catch((error) => {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  cleanupTemp();
  finish("failed");
});

async function main() {
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

  const version = readClaudeVersion();
  if (!version) {
    recordCase("Claude Code version", "blocked", "claude_not_available");
    finish("blocked");
    return;
  }
  recordCase("Claude Code version", "passed", version);

  tempDir = mkdtempSync(join(tmpdir(), "agent-pet-v3-3-notification-matrix-"));

  await runPermissionPromptScenario(token, version);
  recordScenario({
    name: "idle_prompt",
    matcher: "idle_prompt",
    result: "not-run",
    processStatus: "not-run",
    notificationObserved: false,
    hookMarker: "not-run",
    acceptedNeedInput: false,
    targetState: "not-read",
    notes: "interactive idle requires a tty session; prior V3.3 manual interactive probe did not emit Notification"
  });
  recordScenario({
    name: "elicitation_dialog",
    matcher: "elicitation_dialog",
    result: "not-run",
    processStatus: "not-run",
    notificationObserved: false,
    hookMarker: "not-run",
    acceptedNeedInput: false,
    targetState: "not-read",
    notes: "no safe local MCP elicitation scenario is configured in this repo"
  });
  recordScenario({
    name: "auth_success",
    matcher: "auth_success",
    result: "not-run",
    processStatus: "not-run",
    notificationObserved: false,
    hookMarker: "not-run",
    acceptedNeedInput: false,
    targetState: "not-read",
    notes: "auth flow is not rerun because credentials must not be exposed or changed"
  });

  securityScan(version);
  cleanupTemp();

  const passedScenario = scenarios.some((scenario) => scenario.result === "passed");
  const blocked = cases.some((item) => item.result === "blocked");
  const failed = cases.some((item) => item.result === "failed");
  finish(passedScenario && !failed && !blocked ? "passed" : blocked ? "blocked" : "failed", {
    claudeVersion: version,
    notificationResult: passedScenario ? "triggered" : "not-triggered",
    scenarios
  });
}

async function runPermissionPromptScenario(token, version) {
  clearNotificationCooldown();
  const before = await diagnostics(token);
  const beforeIds = new Set((before.acceptedEvents || []).map((event) => event.id));

  const markerValue = `permission-${runId}`;
  const markerPath = join(tempDir, "permission-marker.txt");
  const hookPath = join(tempDir, "permission-hook.sh");
  const settingsPath = join(tempDir, "permission-settings.json");

  writeFileSync(hookPath, [
    "#!/usr/bin/env zsh",
    "set -u",
    `printf '%s' ${shellQuote(markerValue)} > ${shellQuote(markerPath)}`,
    `zsh ${shellQuote(hookScript)} notification >/dev/null 2>&1 || true`,
    "exit 0",
    ""
  ].join("\n"), { mode: 0o700 });

  writeFileSync(settingsPath, JSON.stringify({
    hooks: {
      Notification: [
        {
          matcher: "permission_prompt",
          hooks: [
            {
              type: "command",
              command: `zsh ${hookPath}`,
              timeout: 10
            }
          ]
        }
      ]
    }
  }, null, 2));

  const result = spawnSync("claude", [
    "-p",
    "--settings",
    settingsPath,
    "--output-format",
    "stream-json",
    "--verbose",
    "--include-hook-events",
    "--tools",
    "Bash,Edit,Write",
    "--permission-mode",
    "default",
    "Use the Bash tool to run exactly this command: printf claude-notification-matrix. Do not include secrets."
  ], {
    cwd: repoRoot,
    env: {
      ...process.env,
      AGENT_DESKTOP_PET_URL: url
    },
    encoding: "utf8",
    timeout: Number(process.env.V3_3_NOTIFICATION_MATRIX_TIMEOUT_MS || 120000)
  });

  const combined = `${result.stdout || ""}\n${result.stderr || ""}`;
  const marker = existsSync(markerPath) ? readFileSync(markerPath, "utf8") : "";
  const hookMarkerObserved = marker === markerValue;
  const notificationObserved = /"hookEvent"\s*:\s*"Notification"|"hook_event_name"\s*:\s*"Notification"|Notification/.test(combined);
  const accepted = await waitForAcceptedClaudeEvent(token, beforeIds);
  const defaultState = stateOf(listInstances(), "default");
  const passed = notificationObserved && hookMarkerObserved && Boolean(accepted) && defaultState === "need_input";

  recordScenario({
    name: "permission_prompt",
    matcher: "permission_prompt",
    result: passed ? "passed" : "failed",
    processStatus: result.status === null ? "timeout-or-signal" : `status=${result.status}`,
    notificationObserved,
    hookMarker: hookMarkerObserved ? "observed" : "missing",
    acceptedNeedInput: Boolean(accepted),
    targetState: defaultState || "none",
    notes: passed ? "real Notification accepted" : "Claude Code did not emit accepted Notification -> need_input in this scenario"
  });

  recordCase("permission_prompt scenario completed", result.status === 0 || result.status === 1 ? "passed" : "failed", result.status === null ? "timeout-or-signal" : `status=${result.status}`);
  recordCase("permission_prompt Notification observed", notificationObserved ? "passed" : "failed", notificationObserved ? "Notification observed" : "Notification not observed");
  recordCase("permission_prompt hook marker", hookMarkerObserved ? "passed" : "failed", hookMarkerObserved ? "marker observed" : "marker missing");
  recordCase("permission_prompt accepted need_input", accepted ? "passed" : "failed", accepted ? "accepted event observed" : "accepted event missing");
  recordCase("permission_prompt target state", defaultState === "need_input" ? "passed" : "failed", `defaultState=${defaultState || "none"}`);

  void version;
}

function recordScenario(scenario) {
  scenarios.push(scenario);
}

function readClaudeVersion() {
  const result = spawnSync("claude", ["--version"], { encoding: "utf8" });
  const version = `${result.stdout || result.stderr || ""}`.trim();
  return result.status === 0 && version ? version : undefined;
}

function clearNotificationCooldown() {
  rmSync("/tmp/agent-desktop-pet-claude-hook-notification_need_input.stamp", { force: true });
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
  const petctlBin = join(repoRoot, "packages/petctl/dist/cli.js");
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

function securityScan(version) {
  const serialized = JSON.stringify(summaryObject("pending", {
    claudeVersion: version,
    notificationResult: "redacted",
    scenarios
  }));
  if (SENSITIVE_PATTERNS.some((pattern) => serialized.includes(pattern))) {
    recordCase("security redaction scan", "failed", "summary contained forbidden text");
  } else {
    recordCase("security redaction scan", "passed", "summary did not contain forbidden text");
  }
}

function shellQuote(value) {
  return `'${String(value).replace(/'/g, "'\\''")}'`;
}

function cleanupTemp() {
  if (tempDir) {
    rmSync(tempDir, { recursive: true, force: true });
  }
}

function recordCase(name, result, notes = "") {
  cases.push({ name, result, notes });
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
