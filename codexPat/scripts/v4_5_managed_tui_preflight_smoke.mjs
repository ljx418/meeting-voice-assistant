#!/usr/bin/env node
import { existsSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:17321";
const SENSITIVE_PATTERNS = [
  "AGENT_DESKTOP_PET_TOKEN=",
  "Authorization",
  "api-token.json",
  "Application Support",
  "/Users/",
  "raw hook",
  "raw payload",
  "prompt text",
  "tool command",
  "terminal text",
  "workspace path",
  "config path",
  "transcript_path"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const url = (process.env.AGENT_DESKTOP_PET_URL || DEFAULT_URL).replace(/\/+$/, "");
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
const createdInstances = [];

main().catch(async (error) => {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  await cleanup();
  finish("failed");
});

async function main() {
  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "build petctl first");
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
  await settle(11000);
  recordCase("rate limit window settled", "passed", "waited before TUI preflight");

  const fakeTui = createFakeTui();
  const result = runPetctl([
    "codex",
    "session",
    "start",
    "--mode",
    "tui",
    "--monitor",
    "hooks",
    "--name",
    `V45 TUI Preflight ${runId}`,
    "--bin",
    process.execPath,
    "--no-title",
    "--json",
    "--",
    fakeTui
  ]);

  if (result.json.instanceId) createdInstances.push(result.json.instanceId);
  assertCase("managed TUI preflight exits 0", result.ok, `status=${result.status} reasonCode=${result.reasonCode || "none"}`);
  assertCase("managed TUI instance created", Boolean(result.json.instanceId), "instanceId present");
  assertCase("managed TUI session mode recorded", result.json.raw?.monitor?.sessionMode === "tui", "sessionMode=tui");
  assertCase("managed TUI monitor recorded", result.json.raw?.monitor?.mode === "hooks", "mode=hooks");
  assertCase("managed TUI binding id recorded", /^bind_managed_/.test(result.json.raw?.monitor?.bindingId || ""), "bindingId=bind_managed_*");
  assertCase("managed TUI final state success", stateOf(listInstances(), result.json.instanceId) === "success", "state=success");

  await cleanup();
  securityScan();
  claimScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

function createFakeTui() {
  const dir = mkdtempSync(join(tmpdir(), "agent-pet-v45-"));
  const script = join(dir, "fake-codex-tui.mjs");
  writeFileSync(script, `#!/usr/bin/env node
if (!process.env.AGENT_DESKTOP_PET_INSTANCE_ID) process.exit(22);
if (!process.env.AGENT_DESKTOP_PET_BINDING_ID) process.exit(23);
if (process.env.AGENT_DESKTOP_PET_SOURCE_ID !== "codex.local") process.exit(24);
process.exit(0);
`);
  return script;
}

async function cleanup() {
  for (const instanceId of [...createdInstances].reverse()) {
    const result = runPetctl(["detach", "--instance", instanceId, "--json"]);
    if (result.ok || result.reasonCode === "instance_not_found") {
      recordCase(`cleanup ${safeInstance(instanceId)}`, "passed", "detached");
    } else {
      recordCase(`cleanup ${safeInstance(instanceId)}`, "failed", `cleanup_failed:${result.reasonCode || "unknown"}`);
    }
  }
}

async function waitForHealth() {
  const deadline = Date.now() + Number(process.env.AGENT_DESKTOP_PET_HEALTH_TIMEOUT_MS || 60000);
  while (Date.now() < deadline) {
    const curl = spawnSync("curl", ["-sS", `${url}/api/health`], { encoding: "utf8" });
    if (curl.status === 0) {
      try {
        const body = JSON.parse(curl.stdout);
        if (body?.ok === true) return { ok: true };
      } catch {
        // Try fetch below.
      }
    }
    try {
      const response = await fetch(`${url}/api/health`);
      if (response.ok) {
        const body = await response.json();
        if (body?.ok === true) return { ok: true };
      }
    } catch {
      // Keep waiting.
    }
    await settle(500);
  }
  return { ok: false };
}

function listInstances() {
  const result = runPetctl(["list", "--json"]);
  return result.ok ? result.json.instances || [] : [];
}

function stateOf(instances, instanceId) {
  return instances.find((item) => item.instanceId === instanceId)?.currentState;
}

function runPetctl(args) {
  const result = spawnSync(process.execPath, [petctlBin, ...args], {
    cwd: repoRoot,
    env: {
      ...process.env,
      PETCTL_BIN: petctlBin
    },
    encoding: "utf8"
  });
  const text = `${result.stdout || ""}${result.stderr || ""}`.trim();
  const json = parseJson(text) || {};
  return {
    ok: result.status === 0,
    status: result.status,
    json,
    reasonCode: json.reasonCode || reasonCodeFromText(text),
    text
  };
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    const start = text.lastIndexOf("{");
    if (start >= 0) {
      try {
        return JSON.parse(text.slice(start));
      } catch {
        return undefined;
      }
    }
    return undefined;
  }
}

function reasonCodeFromText(text) {
  return text.match(/reasonCode=([A-Za-z0-9_.-]+)/)?.[1];
}

function settle(ms = 1200) {
  return new Promise((resolvePromise) => setTimeout(resolvePromise, ms));
}

function assertCase(name, condition, details) {
  recordCase(name, condition ? "passed" : "failed", details);
}

function recordCase(name, result, details) {
  cases.push({ name, result, details });
}

function safeInstance(instanceId) {
  return String(instanceId || "unknown").replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 24);
}

function securityScan() {
  const text = JSON.stringify(cases);
  const leaked = SENSITIVE_PATTERNS.filter((pattern) => text.includes(pattern));
  recordCase("security redaction scan", leaked.length === 0 ? "passed" : "failed", leaked.length === 0 ? "no sensitive output" : `leaked=${leaked.join(",")}`);
}

function claimScan() {
  const forbidden = [
    "interactive Codex TUI monitoring ready",
    "already-open Codex window auto-monitoring ready",
    "OS-level Codex window binding ready",
    "all Codex workflows verified",
    "Codex internal reasoning exact mapping ready"
  ];
  const text = JSON.stringify(cases);
  const leaked = forbidden.filter((claim) => text.includes(claim));
  recordCase("claim scan", leaked.length === 0 ? "passed" : "failed", leaked.length === 0 ? "no forbidden ready claim" : `claim=${leaked[0]}`);
}

function finish(status) {
  const payload = { status, cases };
  process.stdout.write(`${JSON.stringify(payload, null, 2)}\n`);
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
