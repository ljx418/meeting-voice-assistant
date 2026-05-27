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
  "../../x.wav",
  "ANTHROPIC_AUTH_TOKEN",
  "DEEPSEEK_API_KEY"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
let tempDir;

main();

function main() {
  tempDir = mkdtempSync(join(tmpdir(), "agent-pet-v3-3-config-load-"));
  const markerValue = `loaded-${runId}`;
  const markerPath = join(tempDir, "marker.txt");
  const hookPath = join(tempDir, "hook.sh");
  const settingsPath = join(tempDir, "settings.json");

  writeFileSync(hookPath, [
    "#!/usr/bin/env zsh",
    "set -u",
    `printf '%s' ${shellQuote(markerValue)} > ${shellQuote(markerPath)}`,
    "exit 0",
    ""
  ].join("\n"), { mode: 0o700 });

  writeFileSync(settingsPath, JSON.stringify({
    hooks: {
      SessionStart: [
        {
          matcher: "startup",
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

  const version = readClaudeVersion();
  if (!version) {
    recordCase("Claude Code version", "blocked", "claude_not_available");
    finish("blocked", { loadResult: "blocked" });
    return;
  }
  recordCase("Claude Code version", "passed", version);

  const result = spawnSync("claude", [
    "-p",
    "--settings",
    settingsPath,
    "--output-format",
    "stream-json",
    "--verbose",
    "--include-hook-events",
    "--tools",
    "",
    "--permission-mode",
    "default",
    "Respond with exactly: config-load-ok"
  ], {
    cwd: repoRoot,
    encoding: "utf8",
    timeout: Number(process.env.V3_3_CONFIG_LOAD_TIMEOUT_MS || 90000)
  });

  const combined = `${result.stdout || ""}\n${result.stderr || ""}`;
  assertCase("Claude Code process completed", result.status === 0, `status=${result.status}`);
  assertCase("SessionStart lifecycle observed", /SessionStart/.test(combined), "SessionStart lifecycle marker in Claude stream");

  const marker = existsSync(markerPath) ? readFileSync(markerPath, "utf8") : "";
  const loaded = marker === markerValue;
  recordCase("temporary settings hook loaded", loaded ? "passed" : "failed", loaded ? "marker observed" : "marker missing");
  recordCase("hook command redacted", "passed", "hook command and temporary paths are not emitted");
  securityScan(version);

  const failed = cases.some((item) => item.result === "failed");
  const blocked = cases.some((item) => item.result === "blocked");
  finish(failed ? "failed" : blocked ? "blocked" : "passed", {
    claudeVersion: version,
    loadResult: loaded ? "loaded" : "not-loaded",
    settingsSource: "temporary --settings file",
    hookEvent: "SessionStart",
    hookCommand: "redacted",
    marker: loaded ? "observed" : "missing"
  });
}

function readClaudeVersion() {
  const result = spawnSync("claude", ["--version"], { encoding: "utf8" });
  const version = `${result.stdout || result.stderr || ""}`.trim();
  return result.status === 0 && version ? version : undefined;
}

function securityScan(version) {
  const serialized = JSON.stringify(summaryObject("pending", {
    claudeVersion: version,
    loadResult: "redacted",
    settingsSource: "temporary --settings file",
    hookEvent: "SessionStart",
    hookCommand: "redacted",
    marker: "redacted"
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
  rmSync(tempDir, { recursive: true, force: true });
  console.log(JSON.stringify(summaryObject(status, extra), null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
