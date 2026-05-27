#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:17321";
const HARD_LIMIT = 12;
const SENSITIVE_PATTERNS = [
  "AGENT_DESKTOP_PET_TOKEN=",
  "Authorization: Bearer",
  "api-token.json",
  "Application Support",
  "/Users/",
  "raw payload",
  "workspace path",
  "../../x.wav"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const url = (process.env.AGENT_DESKTOP_PET_URL || DEFAULT_URL).replace(/\/+$/, "");
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
const createdSmokeInstances = [];

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

  const token = resolveToken();
  if (!token) {
    recordCase("token available", "blocked", "token_missing");
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

  await authCases();

  const initial = runPetctl(["list", "--json"]);
  if (!initial.ok) {
    recordCase("petctl list baseline", "blocked", initial.reasonCode || "list_failed");
    finish("blocked");
    return;
  }
  const initialInstances = initial.json.instances || [];
  recordCase("petctl list baseline", "passed", `preExistingInstanceCount=${initialInstances.length}`);
  if (initialInstances.length > HARD_LIMIT - 1) {
    recordCase("free slot for contract smoke", "blocked", "need at least one free slot");
    finish("blocked");
    return;
  }

  const instance = attachSmokeInstance(`Third Party Smoke ${runId}`);
  if (!instance) {
    await cleanup();
    finish("failed");
    return;
  }

  await legacyDefaultCase(token, instance.instanceId);
  await instanceRouteCase(token, instance.instanceId);
  petctlNotifyInstanceCase(instance.instanceId);
  expectPetctlFailure("unknown instance returns instance_not_found", ["notify", "--instance", "not-found", "--level", "success"], "instance_not_found");
  expectPetctlFailure("invalid instance returns instance_id_invalid", ["notify", "--instance", "../../bad", "--level", "success"], "instance_id_invalid");
  await invalidSoundRedactionCase(token, instance.instanceId);
  await exampleCases(token);
  await hardLimitCase();
  await cleanup();
  securityScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

async function authCases() {
  const missing = await fetch(`${url}/api/events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(validEvent("auth-missing.local", "success"))
  });
  const missingBody = await readJson(missing);
  assertCase("missing token returns auth_missing", missing.status === 401 && missingBody?.reasonCode === "auth_missing", `status=${missing.status} reasonCode=${missingBody?.reasonCode || "none"}`);

  const invalid = await fetch(`${url}/api/events`, {
    method: "POST",
    headers: { "Authorization": "Bearer invalid-redacted", "Content-Type": "application/json" },
    body: JSON.stringify(validEvent("auth-invalid.local", "success"))
  });
  const invalidBody = await readJson(invalid);
  assertCase("invalid token returns auth_invalid", invalid.status === 401 && invalidBody?.reasonCode === "auth_invalid", `status=${invalid.status} reasonCode=${invalidBody?.reasonCode || "none"}`);
}

async function legacyDefaultCase(token, instanceId) {
  const before = listInstances();
  const response = await postEvent(token, "/api/events", validEvent("third-party.local", "success"));
  assertCase("legacy /api/events accepted", response.status === 202 && response.body?.accepted === true, `status=${response.status}`);
  assertCase("legacy /api/events does not alter target instance", stateOf(listInstances(), instanceId) === stateOf(before, instanceId), "target instance unchanged");
}

async function instanceRouteCase(token, instanceId) {
  const response = await postEvent(token, `/api/instances/${encodeURIComponent(instanceId)}/events`, validEvent("third-party.local", "need_input"));
  assertCase("instance route accepted", response.status === 202 && response.body?.accepted === true, `status=${response.status}`);
  assertCase("instance route updates target", stateOf(listInstances(), instanceId) === "need_input", "target instance state=need_input");
}

function petctlNotifyInstanceCase(instanceId) {
  const result = runPetctl(["notify", "--instance", instanceId, "--level", "warning", "--title", "third-party petctl smoke"]);
  assertCase("petctl notify --instance accepted", result.ok, result.reasonCode || "accepted");
  assertCase("petctl notify --instance updates target", stateOf(listInstances(), instanceId) === "warning", "target instance state=warning");
}

async function invalidSoundRedactionCase(token, instanceId) {
  const response = await postEvent(token, `/api/instances/${encodeURIComponent(instanceId)}/events`, {
    ...validEvent("third-party.local", "success"),
    sound: "../../x.wav"
  });
  const text = JSON.stringify(response.body || {});
  const rejected = response.status === 400 && response.body?.reasonCode === "whitelist_invalid";
  const redacted = !SENSITIVE_PATTERNS.some((pattern) => text.includes(pattern));
  assertCase("invalid sound redaction", rejected && redacted, `status=${response.status} reasonCode=${response.body?.reasonCode || "none"}`);
}

async function exampleCases(token) {
  const env = {
    ...process.env,
    AGENT_DESKTOP_PET_TOKEN: token,
    AGENT_DESKTOP_PET_URL: url
  };
  const curl = spawnSync("bash", ["examples/http/curl-agent-smoke.sh", "success"], { cwd: repoRoot, env, encoding: "utf8" });
  assertCase("curl local contract example", curl.status === 0 && safeText(curl.stdout + curl.stderr), `status=${curl.status}`);

  const node = spawnSync(process.execPath, ["examples/http/node-http-agent-smoke.mjs", "warning"], { cwd: repoRoot, env, encoding: "utf8" });
  assertCase("Node local contract example", node.status === 0 && safeText(node.stdout + node.stderr), `status=${node.status}`);

  const python = spawnSync("python3", ["examples/http/python_http_agent_smoke.py", "need_input"], { cwd: repoRoot, env, encoding: "utf8" });
  assertCase("Python local contract example", python.status === 0 && safeText(python.stdout + python.stderr), `status=${python.status}`);
}

async function hardLimitCase() {
  const currentCount = listInstances().length;
  if (currentCount > HARD_LIMIT) {
    recordCase("hard limit setup", "blocked", `currentCount=${currentCount}`);
    return;
  }
  for (let index = currentCount; index < HARD_LIMIT; index += 1) {
    const filler = attachSmokeInstance(`Third Party Fill ${index + 1} ${runId}`);
    if (!filler) {
      recordCase("hard limit fill", "failed", `failedAt=${index + 1}`);
      return;
    }
  }
  const thirteenth = runPetctl(["attach", "codex", "--name", `Third Party 13 ${runId}`, "--json"]);
  assertCase("hard limit returns instance_limit_reached", !thirteenth.ok && thirteenth.reasonCode === "instance_limit_reached", `reasonCode=${thirteenth.reasonCode || "none"}`);
}

function attachSmokeInstance(name) {
  const result = runPetctl(["attach", "codex", "--name", name, "--json"]);
  if (!result.ok || !result.json.instanceId) {
    recordCase(`attach ${name}`, "failed", result.reasonCode || "attach_failed");
    return null;
  }
  const instance = { instanceId: result.json.instanceId, displayName: result.json.displayName || name };
  createdSmokeInstances.push(instance);
  recordCase(`attach ${name}`, "passed", `instanceId=${instance.instanceId}`);
  return instance;
}

async function cleanup() {
  for (const instance of [...createdSmokeInstances].reverse()) {
    const result = runPetctl(["detach", "--instance", instance.instanceId, "--json"]);
    if (result.ok || result.reasonCode === "instance_not_found") {
      recordCase(`cleanup ${instance.instanceId}`, "passed", "detached");
    } else {
      recordCase(`cleanup ${instance.instanceId}`, "failed", `cleanup_failed:${result.reasonCode || "unknown"}`);
    }
  }
}

async function postEvent(token, path, event) {
  const response = await fetch(`${url}${path}`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify(event)
  });
  return { status: response.status, body: await readJson(response) };
}

function validEvent(sourceId, level) {
  return {
    source: { id: sourceId, kind: "custom", name: "Third Party Smoke" },
    level,
    title: `third-party contract ${level}`,
    sound: "none"
  };
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
  const text = (result.stdout || result.stderr || "").trim();
  const json = parseJson(text) || {};
  return {
    ok: result.status === 0,
    status: result.status,
    json,
    reasonCode: json.reasonCode || reasonCodeFromText(text),
    text
  };
}

function expectPetctlFailure(name, args, reasonCode) {
  const result = runPetctl(args);
  assertCase(name, !result.ok && result.reasonCode === reasonCode, `reasonCode=${result.reasonCode || "none"}`);
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

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

function reasonCodeFromText(text) {
  return text.match(/reasonCode=([A-Za-z0-9_]+)/)?.[1];
}

function safeText(text) {
  return !SENSITIVE_PATTERNS.some((pattern) => text.includes(pattern));
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

function summaryObject(status) {
  return {
    status,
    runId,
    cases,
    createdSmokeInstances: createdSmokeInstances.length
  };
}

function finish(status) {
  console.log(JSON.stringify(summaryObject(status), null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
