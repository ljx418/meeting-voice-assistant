#!/usr/bin/env node
import { existsSync } from "node:fs";
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
  "transcript_path",
  "tool input command"
];
const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const hookBin = join(repoRoot, "scripts/codex-pet-hook.mjs");
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
  if (!existsSync(hookBin)) {
    recordCase("hook wrapper exists", "blocked", "scripts/codex-pet-hook.mjs missing");
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

  const instance = attachSmokeInstance(`V3.4 Hook Fixture ${runId}`);
  if (!instance) {
    await cleanup();
    finish("failed");
    return;
  }

  expectHookState("SessionStart", {}, "running");
  await settle();
  expectHookState("UserPromptSubmit", { prompt: "redacted" }, "thinking");
  await settle();
  expectHookState("PreToolUse", { tool: "shell", input: "redacted" }, "running");
  expectHookState("PreToolUse duplicate cooldown", { tool: "shell", input: "redacted" }, "running", "PreToolUse");
  await settle();
  expectHookNoStateChange("PostToolUse observed schema without result", {
    tool: "shell",
    tool_input: { command: "redacted" }
  }, "running", "PostToolUse");
  await settle();
  expectHookState("PermissionRequest", { reason: "redacted" }, "need_input");
  await settle();
  expectHookState("PostToolUse failure", { exitCode: 17 }, "error", "PostToolUse");
  await settle();
  expectHookState("Stop after failure", {}, "error", "Stop");
  await settle();
  expectHookState("UserPromptSubmit clean turn", { prompt: "redacted" }, "thinking", "UserPromptSubmit");
  await settle();
  expectHookState("Stop after clean turn", {}, "success", "Stop");

  const noInstance = runHook("UserPromptSubmit", {}, {});
  assertCase("missing instance no-op", noInstance.status === 0 && noInstance.text.trim() === "{}", `status=${noInstance.status}`);

  await cleanup();
  securityScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

function expectHookState(name, payload, expectedState, eventOverride) {
  const event = eventOverride || name;
  const result = runHook(event, payload, { AGENT_DESKTOP_PET_INSTANCE_ID: createdInstances[0] });
  assertCase(`${name} hook exits 0`, result.status === 0 && result.text.trim() === "{}", `status=${result.status}`);
  assertCase(`${name} -> ${expectedState}`, stateOf(listInstances(), createdInstances[0]) === expectedState, `state=${expectedState}`);
}

function expectHookNoStateChange(name, payload, expectedState, eventOverride) {
  const event = eventOverride || name;
  const before = stateOf(listInstances(), createdInstances[0]);
  const result = runHook(event, payload, { AGENT_DESKTOP_PET_INSTANCE_ID: createdInstances[0] });
  const after = stateOf(listInstances(), createdInstances[0]);
  assertCase(`${name} hook exits 0`, result.status === 0 && result.text.trim() === "{}", `status=${result.status}`);
  assertCase(`${name} no-op`, before === expectedState && after === expectedState, `before=${before || "none"} after=${after || "none"}`);
}

function runHook(event, payload, extraEnv) {
  const result = spawnSync(process.execPath, [hookBin, event], {
    cwd: repoRoot,
    env: {
      ...process.env,
      PETCTL_BIN: petctlBin,
      ...extraEnv
    },
    input: JSON.stringify(payload),
    encoding: "utf8"
  });
  return {
    status: result.status,
    text: `${result.stdout || ""}${result.stderr || ""}`.trim()
  };
}

function attachSmokeInstance(name) {
  const result = runPetctl(["attach", "codex", "--name", name, "--json"]);
  if (!result.ok || !result.json.instanceId) {
    recordCase("attach hook fixture instance", "failed", result.reasonCode || "attach_failed");
    return null;
  }
  createdInstances.push(result.json.instanceId);
  recordCase("attach hook fixture instance", "passed", "instance attached");
  return result.json;
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

function runPetctl(args) {
  const result = spawnSync(process.execPath, [petctlBin, ...args], {
    cwd: repoRoot,
    env: process.env,
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

function securityScan() {
  const output = JSON.stringify(cases);
  const leaked = SENSITIVE_PATTERNS.filter((pattern) => output.includes(pattern));
  assertCase("security redaction scan", leaked.length === 0, leaked.length === 0 ? "no sensitive output" : `leaked=${leaked.join(",")}`);
}

function finish(status) {
  console.log(JSON.stringify({ status, runId, cases }, null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
