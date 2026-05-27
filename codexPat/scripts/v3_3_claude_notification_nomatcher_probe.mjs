#!/usr/bin/env node
import { existsSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

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
  "../../x.wav"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const tempDir = mkdtempSync(join(tmpdir(), "agent-pet-v3-3-nomatcher-"));
const cases = [];
const scenarios = [];

try {
  const version = readClaudeVersion();
  if (!version) {
    recordCase("Claude Code version", "blocked", "claude_not_available");
    finish("blocked", { notificationResult: "blocked" });
  } else {
    recordCase("Claude Code version", "passed", version);
    runScenario({
      name: "no_matcher_bash",
      tools: "Bash",
      prompt: "Use the Bash tool to run exactly this command: printf claude-notification-nomatcher. Do not include secrets."
    });
    runScenario({
      name: "no_matcher_write_tmp",
      tools: "Write",
      prompt: "Use the Write tool to create a temporary file named v33_write_permission_probe.txt under the system temporary directory containing exactly ok. Do not include secrets."
    });
    securityScan(version);
    const passedScenario = scenarios.some((scenario) => scenario.result === "passed");
    const blocked = cases.some((item) => item.result === "blocked");
    finish(passedScenario ? "passed" : blocked ? "blocked" : "failed", {
      claudeVersion: version,
      notificationResult: passedScenario ? "triggered" : "not-triggered",
      scenarios
    });
  }
} finally {
  rmSync(tempDir, { recursive: true, force: true });
}

function runScenario({ name, tools, prompt }) {
  const markerValue = `${name}-${runId}`;
  const markerPath = join(tempDir, `${name}.marker`);
  const hookPath = join(tempDir, `${name}.hook.sh`);
  const settingsPath = join(tempDir, `${name}.settings.json`);

  writeFileSync(hookPath, [
    "#!/usr/bin/env zsh",
    "set -u",
    `printf '%s' ${shellQuote(markerValue)} > ${shellQuote(markerPath)}`,
    "exit 0",
    ""
  ].join("\n"), { mode: 0o700 });

  writeFileSync(settingsPath, JSON.stringify({
    hooks: {
      Notification: [
        {
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
    tools,
    "--permission-mode",
    "default",
    prompt
  ], {
    cwd: repoRoot,
    encoding: "utf8",
    timeout: Number(process.env.V3_3_NOMATCHER_TIMEOUT_MS || 120000)
  });

  const combined = `${result.stdout || ""}\n${result.stderr || ""}`;
  const marker = existsSync(markerPath) ? readFileSync(markerPath, "utf8") : "";
  const hookMarkerObserved = marker === markerValue;
  const notificationObserved = /"hookEvent"\s*:\s*"Notification"|"hook_event_name"\s*:\s*"Notification"|Notification/.test(combined);
  const passed = notificationObserved && hookMarkerObserved;

  scenarios.push({
    name,
    matcher: "omitted",
    result: passed ? "passed" : "failed",
    processStatus: result.status === null ? "timeout-or-signal" : `status=${result.status}`,
    notificationObserved,
    hookMarker: hookMarkerObserved ? "observed" : "missing",
    notes: passed ? "real Notification hook command executed" : "Notification hook did not execute in this scenario"
  });

  recordCase(`${name} process completed`, result.status === 0 || result.status === 1 ? "passed" : "failed", result.status === null ? "timeout-or-signal" : `status=${result.status}`);
  recordCase(`${name} Notification observed`, notificationObserved ? "passed" : "failed", notificationObserved ? "Notification observed" : "Notification not observed");
  recordCase(`${name} hook marker`, hookMarkerObserved ? "passed" : "failed", hookMarkerObserved ? "marker observed" : "marker missing");
}

function readClaudeVersion() {
  const result = spawnSync("claude", ["--version"], { encoding: "utf8" });
  const version = `${result.stdout || result.stderr || ""}`.trim();
  return result.status === 0 && version ? version : undefined;
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
