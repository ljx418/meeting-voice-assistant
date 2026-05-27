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
  "raw JSONL",
  "raw payload",
  "prompt text",
  "tool command",
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
  recordCase("rate limit window settled", "passed", "waited before monitor smoke");

  const fakeCodex = createFakeCodexExecJsonl();

  const simple = launchJsonlMonitor("V37 Simple", fakeCodex, "simple");
  if (simple.json.instanceId) createdInstances.push(simple.json.instanceId);
  assertCase("simple answer launch exits 0", simple.ok, `status=${simple.status} reasonCode=${simple.reasonCode || "none"}`);
  assertCase("simple answer observed turn.started", hasEvent(simple, "turn.started"), "eventType=turn.started");
  assertCase("simple answer observed turn.completed", hasEvent(simple, "turn.completed"), "eventType=turn.completed");
  assertCase("simple answer mapped thinking", hasState(simple, "thinking"), "state=thinking");
  assertCase("simple answer final state success", stateOf(listInstances(), simple.json.instanceId) === "success", "state=success");

  await settle(1200);
  const success = launchJsonlMonitor("V37 Success", fakeCodex, "tool-success");
  if (success.json.instanceId) createdInstances.push(success.json.instanceId);
  assertCase("tool success launch exits 0", success.ok, `status=${success.status} reasonCode=${success.reasonCode || "none"}`);
  assertCase("tool success observed item.started", hasEvent(success, "item.started"), "eventType=item.started");
  assertCase("tool success mapped running", hasState(success, "running"), "state=running");
  assertCase("tool success final state success", stateOf(listInstances(), success.json.instanceId) === "success", "state=success");

  await settle(1200);
  const failure = launchJsonlMonitor("V37 Failure", fakeCodex, "tool-failure");
  if (failure.json.instanceId) createdInstances.push(failure.json.instanceId);
  assertCase("tool failure launch exits nonzero", !failure.ok && failure.reasonCode === "codex_process_failed", `status=${failure.status} reasonCode=${failure.reasonCode || "none"}`);
  assertCase("tool failure observed structured failure", hasEvent(failure, "turn.failed") || hasEvent(failure, "error"), "eventType=turn.failed_or_error");
  assertCase("tool failure monitor summary marks failure", failure.json.raw?.monitor?.observedFailureSignal === true, "observedFailureSignal=true");
  assertCase("tool failure mapped error", stateOf(listInstances(), failure.json.instanceId) === "error", "state=error");

  await cleanup();
  securityScan();
  claimScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

function launchJsonlMonitor(name, fakeCodex, scenario) {
  return runPetctl([
    "codex",
    "launch",
    "--name",
    `${name} ${runId}`,
    "--monitor",
    "jsonl",
    "--bin",
    process.execPath,
    "--no-title",
    "--json",
    "--",
    fakeCodex,
    scenario
  ]);
}

function createFakeCodexExecJsonl() {
  const dir = mkdtempSync(join(tmpdir(), "agent-pet-v37-"));
  const script = join(dir, "fake-codex-exec-jsonl.mjs");
  writeFileSync(script, `#!/usr/bin/env node
const scenario = process.argv[2];
if (!process.env.AGENT_DESKTOP_PET_INSTANCE_ID) process.exit(22);
function emit(type, extra = {}) {
  process.stdout.write(JSON.stringify({ type, ...extra }) + "\\n");
}
emit("thread.started", { safe: true });
emit("turn.started", { safe: true });
if (scenario === "tool-success" || scenario === "tool-failure") {
  emit("item.started", { item: { kind: "tool" } });
  emit("item.completed", { item: { kind: "tool" } });
}
if (scenario === "tool-failure") {
  emit("turn.failed", { status: "failed" });
  process.exit(17);
}
emit("turn.completed", { status: "completed" });
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
    try {
      const response = await fetch(`${url}/api/health`);
      if (response.ok) {
        const body = await response.json();
        if (body?.ok === true) return { ok: true };
      }
    } catch {
      // Fall back to curl below.
    }
    const curl = spawnSync("curl", ["-sS", `${url}/api/health`], { encoding: "utf8" });
    if (curl.status === 0) {
      try {
        const body = JSON.parse(curl.stdout);
        if (body?.ok === true) return { ok: true };
      } catch {
        // Keep waiting.
      }
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

function hasEvent(result, eventType) {
  return (result.json.raw?.monitor?.observedEventTypes || []).includes(eventType);
}

function hasState(result, state) {
  return (result.json.raw?.monitor?.mappedStates || []).includes(state);
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
  const output = JSON.stringify(cases);
  const leaked = SENSITIVE_PATTERNS.filter((pattern) => output.includes(pattern));
  assertCase("security redaction scan", leaked.length === 0, leaked.length === 0 ? "no sensitive output" : `leaked=${leaked.join(",")}`);
}

function claimScan() {
  const output = JSON.stringify(cases);
  const forbiddenReady = [
    "V3.6 selected Codex workflow hook coverage smoke passed",
    "PostToolUse failure hook evidence passed",
    "all Codex workflows verified",
    "Codex internal reasoning exact mapping ready",
    "OS-level Codex window binding ready"
  ].filter((claim) => output.includes(claim));
  assertCase("claim scan", forbiddenReady.length === 0, forbiddenReady.length === 0 ? "no forbidden passed claim" : `forbidden=${forbiddenReady.join(",")}`);
}

function finish(status) {
  console.log(JSON.stringify({ status, runId, cases }, null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
