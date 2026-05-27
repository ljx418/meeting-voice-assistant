#!/usr/bin/env node
import { existsSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:17321";
const SENSITIVE_PATTERNS = [
  "AGENT_DESKTOP_PET_TOKEN=",
  "Authorization: Bearer",
  "api-token.json",
  "Application Support",
  "/Users/",
  "raw payload",
  "workspace path",
  "/dev/ttys"
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
  await new Promise((resolvePromise) => setTimeout(resolvePromise, 11000));
  recordCase("rate limit window settled", "passed", "waited before burst smoke");

  const fakeCodex = createFakeCodex();
  const success = launchFakeCodex("Codex Binding A", fakeCodex, "success", "thinking");
  if (success.json.instanceId) createdInstances.push(success.json.instanceId);
  assertCase("codex launch success exits 0", success.ok, `status=${success.status} reasonCode=${success.reasonCode || "none"}`);
  assertCase("codex launch success has instance", Boolean(success.json.instanceId), "instanceId present");
  assertCase("success launch final state is success", stateOf(listInstances(), success.json.instanceId) === "success", "state=success");

  const failure = launchFakeCodex("Codex Binding B", fakeCodex, "fail", "need_input");
  if (failure.json.instanceId) createdInstances.push(failure.json.instanceId);
  assertCase("codex launch failure exits nonzero", !failure.ok && failure.reasonCode === "codex_process_failed", `status=${failure.status} reasonCode=${failure.reasonCode || "none"}`);
  assertCase("codex launch failure has instance", Boolean(failure.json.instanceId), "instanceId present");
  assertCase("failure launch final state is error", stateOf(listInstances(), failure.json.instanceId) === "error", "state=error");

  const successState = stateOf(listInstances(), success.json.instanceId);
  assertCase("session B does not alter session A", successState === "success", `sessionAState=${successState || "missing"}`);

  await cleanup();
  securityScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

function launchFakeCodex(name, fakeCodex, mode, childLevel) {
  return runPetctl([
    "codex",
    "launch",
    "--name",
    `${name} ${runId}`,
    "--bin",
    process.execPath,
    "--no-title",
    "--json",
    "--",
    fakeCodex,
    mode,
    childLevel
  ]);
}

function createFakeCodex() {
  const dir = mkdtempSync(join(tmpdir(), "agent-pet-v33-"));
  const script = join(dir, "fake-codex.mjs");
  writeFileSync(script, `#!/usr/bin/env node
import { spawnSync } from "node:child_process";
const [, , mode, level] = process.argv;
const petctl = process.env.PETCTL_BIN;
if (!process.env.AGENT_DESKTOP_PET_INSTANCE_ID || !petctl) process.exit(22);
const result = spawnSync(process.execPath, [petctl, "notify", "--level", level || "thinking", "--source-id", "codex.local", "--source-kind", "codex", "--source-name", "Codex", "--title", "fake codex state"], {
  env: process.env,
  stdio: "ignore"
});
if (result.status !== 0) process.exit(23);
process.exit(mode === "fail" ? 17 : 0);
`);
  return script;
}

async function cleanup() {
  for (const instanceId of [...createdInstances].reverse()) {
    const result = runPetctl(["detach", "--instance", instanceId, "--json"]);
    if (result.ok || result.reasonCode === "instance_not_found") {
      recordCase(`cleanup ${instanceId}`, "passed", "detached");
    } else {
      recordCase(`cleanup ${instanceId}`, "failed", `cleanup_failed:${result.reasonCode || "unknown"}`);
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
      // Keep waiting until timeout.
    }
    const curl = spawnSync("curl", ["-sS", `${url}/api/health`], { encoding: "utf8" });
    if (curl.status === 0) {
      try {
        const body = JSON.parse(curl.stdout);
        if (body?.ok === true) return { ok: true };
      } catch {
        // Keep waiting until timeout.
      }
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 500));
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
  const match = text.match(/reasonCode=([A-Za-z0-9_.-]+)/);
  return match?.[1];
}

function assertCase(name, condition, details) {
  recordCase(name, condition ? "passed" : "failed", details);
}

function recordCase(name, result, details) {
  cases.push({ name, result, details });
}

function securityScan() {
  const output = JSON.stringify(cases);
  const leaked = SENSITIVE_PATTERNS.filter((pattern) => output.includes(pattern));
  assertCase("security redaction scan", leaked.length === 0, leaked.length === 0 ? "no sensitive output" : `leaked=${leaked.join(",")}`);
}

function finish(status) {
  const summary = { status, cases };
  console.log(JSON.stringify(summary, null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
