#!/usr/bin/env node
import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:17321";
const HARD_LIMIT = 12;
const REQUIRED_FREE_SLOTS = 2;
const SENSITIVE_PATTERNS = [
  "AGENT_DESKTOP_PET_TOKEN=",
  "Authorization: Bearer",
  "api-token.json",
  "Application Support",
  "raw payload",
  "../../x.wav",
  "file://",
  "/Users/"
];

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const url = trimTrailingSlash(process.env.AGENT_DESKTOP_PET_URL || DEFAULT_URL);
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const createdSmokeInstances = [];
const cases = [];
const securityChecks = [];
const skipped = [];
let preExistingInstanceCount = null;

main().catch(async (error) => {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  await cleanup();
  finish("failed");
});

async function main() {
  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "build petctl first: pnpm --filter @agent-desktop-pet/petctl build");
    finish("blocked");
    return;
  }

  const health = await getJson("/api/health");
  if (!health.ok) {
    recordCase("health API", "blocked", "desktop_not_running");
    finish("blocked");
    return;
  }
  recordCase("health API", "passed", "desktop app is reachable");

  const initialList = runPetctl(["list", "--json"]);
  if (!initialList.ok) {
    recordCase("petctl list baseline", "blocked", initialList.reasonCode || "list_failed");
    finish("blocked");
    return;
  }
  const initialInstances = initialList.json.instances || [];
  preExistingInstanceCount = initialInstances.length;
  recordCase("read current instance list", "passed", `preExistingInstanceCount=${preExistingInstanceCount}`);

  if (preExistingInstanceCount > HARD_LIMIT - REQUIRED_FREE_SLOTS) {
    recordCase("free slots for A/B smoke", "blocked", `need at least ${REQUIRED_FREE_SLOTS} free slots`);
    finish("blocked");
    return;
  }

  const a = attachSmokeInstance(`Smoke Cat A ${runId}`);
  const b = attachSmokeInstance(`Smoke Cat B ${runId}`);
  if (!a || !b) {
    await cleanup();
    finish("failed");
    return;
  }

  const listAfterAttach = runPetctl(["list", "--json"]);
  const listedIds = new Set((listAfterAttach.json.instances || []).map((instance) => instance.instanceId));
  assertCase(
    "petctl list shows default + A + B",
    listAfterAttach.ok && listedIds.has("default") && listedIds.has(a.instanceId) && listedIds.has(b.instanceId),
    `default=${listedIds.has("default")} A=${listedIds.has(a.instanceId)} B=${listedIds.has(b.instanceId)}`
  );

  notifyCase("notify --instance A routes to A", ["notify", "--instance", a.instanceId, "--level", "success", "--title", "runtime smoke A"], () => {
    const instances = listInstances();
    return stateOf(instances, a.instanceId) === "success" && stateOf(instances, b.instanceId) !== "success";
  });

  notifyCase("notify --instance B routes to B", ["notify", "--instance", b.instanceId, "--level", "error", "--title", "runtime smoke B"], () => {
    const instances = listInstances();
    return stateOf(instances, b.instanceId) === "error";
  });

  notifyCase("env instance routes to A", ["notify", "--level", "running", "--title", "env route A"], () => {
    const instances = listInstances();
    return stateOf(instances, a.instanceId) === "running";
  }, { AGENT_DESKTOP_PET_INSTANCE_ID: a.instanceId });

  notifyCase("explicit --instance overrides env", ["notify", "--instance", b.instanceId, "--level", "success", "--title", "explicit override B"], () => {
    const instances = listInstances();
    return stateOf(instances, b.instanceId) === "success" && stateOf(instances, a.instanceId) === "running";
  }, { AGENT_DESKTOP_PET_INSTANCE_ID: a.instanceId });

  const beforeLegacy = listInstances();
  notifyCase("legacy notify uses default route", ["notify", "--level", "success", "--title", "legacy runtime smoke"], () => {
    const instances = listInstances();
    return stateOf(instances, a.instanceId) === stateOf(beforeLegacy, a.instanceId)
      && stateOf(instances, b.instanceId) === stateOf(beforeLegacy, b.instanceId);
  });

  expectFailure("unknown instance returns 404", ["notify", "--instance", "not-found", "--level", "success"], "instance_not_found");
  expectFailure("invalid instanceId is rejected safely", ["notify", "--instance", "../../bad", "--level", "success"], "instance_id_invalid");
  expectFailure("env not-found does not fallback default", ["notify", "--level", "success"], "instance_not_found", {
    AGENT_DESKTOP_PET_INSTANCE_ID: "not-found"
  });

  await invalidSoundRedactionCase(a.instanceId);
  await hardLimitCase();
  await cleanup();

  const afterCleanup = runPetctl(["list", "--json"]);
  const remainingIds = new Set((afterCleanup.json.instances || []).map((instance) => instance.instanceId));
  const detachedGone = createdSmokeInstances.every((instance) => !remainingIds.has(instance.instanceId));
  assertCase("detached smoke instances no longer listed", detachedGone, `remainingSmoke=${createdSmokeInstances.filter((instance) => remainingIds.has(instance.instanceId)).length}`);

  expectFailure("detach after notify returns 404", ["notify", "--instance", a.instanceId, "--level", "success", "--title", "after detach"], "instance_not_found");
  securityScan();

  const failed = cases.some((item) => item.result === "failed");
  const blocked = cases.some((item) => item.result === "blocked");
  finish(failed ? "failed" : blocked ? "blocked" : "passed");
}

function attachSmokeInstance(name) {
  const result = runPetctl(["attach", "codex", "--name", name, "--json"]);
  if (!result.ok || !result.json.instanceId) {
    recordCase(`attach ${name}`, "failed", result.reasonCode || "attach_failed");
    return null;
  }
  const instance = {
    instanceId: result.json.instanceId,
    displayName: result.json.displayName || name
  };
  createdSmokeInstances.push(instance);
  recordCase(`attach ${name}`, "passed", `instanceId=${instance.instanceId}`);
  return instance;
}

function notifyCase(name, args, verify, extraEnv = {}) {
  const result = runPetctl(args, extraEnv);
  if (!result.ok) {
    recordCase(name, "failed", result.reasonCode || "notify_failed");
    return;
  }
  assertCase(name, verify(), "accepted and routing check passed");
}

function expectFailure(name, args, reasonCode, extraEnv = {}) {
  const result = runPetctl(args, extraEnv);
  assertCase(name, !result.ok && result.reasonCode === reasonCode, `reasonCode=${result.reasonCode || "none"}`);
}

async function invalidSoundRedactionCase(instanceId) {
  const token = resolveToken();
  if (!token) {
    recordCase("invalid sound redaction", "blocked", "token_missing");
    return;
  }
  const response = await fetch(`${url}/api/instances/${encodeURIComponent(instanceId)}/events`, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      source: { id: "smoke.local", kind: "custom", name: "Runtime Smoke" },
      level: "success",
      sound: "../../x.wav",
      title: "invalid sound redaction"
    })
  });
  const text = await response.text();
  const rejected = response.status === 400 && text.includes("whitelist_invalid");
  const redacted = !SENSITIVE_PATTERNS.some((pattern) => text.includes(pattern));
  assertCase("invalid sound path rejected and redacted", rejected && redacted, `status=${response.status}`);
}

async function hardLimitCase() {
  const current = listInstances();
  const currentCount = current.length;
  if (currentCount > HARD_LIMIT) {
    recordCase("hard limit setup", "blocked", `currentCount=${currentCount}`);
    return;
  }
  for (let index = currentCount; index < HARD_LIMIT; index += 1) {
    const filler = attachSmokeInstance(`Smoke Cat Fill ${index + 1} ${runId}`);
    if (!filler) {
      recordCase("hard limit fill", "failed", `failedAt=${index + 1}`);
      return;
    }
  }
  const thirteenth = runPetctl(["attach", "codex", "--name", `Smoke Cat 13 ${runId}`, "--json"]);
  assertCase(
    "hard limit rejects 13th pet",
    !thirteenth.ok && thirteenth.reasonCode === "instance_limit_reached",
    `reasonCode=${thirteenth.reasonCode || "none"}`
  );
}

async function cleanup() {
  for (const instance of [...createdSmokeInstances].reverse()) {
    const result = runPetctl(["detach", "--instance", instance.instanceId, "--json"]);
    if (result.ok) {
      recordCase(`cleanup ${instance.instanceId}`, "passed", "detached");
    } else if (result.reasonCode === "instance_not_found") {
      recordCase(`cleanup ${instance.instanceId}`, "passed", "already detached");
    } else {
      recordCase(`cleanup ${instance.instanceId}`, "failed", `cleanup_failed:${result.reasonCode || "unknown"}`);
    }
  }
}

function listInstances() {
  const result = runPetctl(["list", "--json"]);
  return result.ok ? result.json.instances || [] : [];
}

function stateOf(instances, instanceId) {
  return instances.find((instance) => instance.instanceId === instanceId)?.currentState;
}

function runPetctl(args, extraEnv = {}) {
  const result = spawnSync(process.execPath, [petctlBin, ...args], {
    cwd: repoRoot,
    env: {
      ...process.env,
      ...extraEnv
    },
    encoding: "utf8"
  });
  const stdout = result.stdout.trim();
  const stderr = result.stderr.trim();
  const text = stdout || stderr;
  const parsed = parseJson(text);
  return {
    ok: result.status === 0,
    status: result.status,
    json: parsed || {},
    reasonCode: parsed?.reasonCode || reasonCodeFromText(text),
    text
  };
}

async function getJson(path) {
  try {
    const response = await fetch(`${url}${path}`);
    if (!response.ok) return { ok: false, status: response.status };
    return await response.json();
  } catch {
    return { ok: false };
  }
}

function parseJson(text) {
  if (!text) return undefined;
  try {
    return JSON.parse(text);
  } catch {
    return undefined;
  }
}

function reasonCodeFromText(text) {
  return text.match(/reasonCode=([A-Za-z0-9_]+)/)?.[1];
}

function recordCase(name, result, notes = "") {
  cases.push({ name, result, notes });
}

function assertCase(name, condition, notes = "") {
  recordCase(name, condition ? "passed" : "failed", notes);
}

function securityScan() {
  const summary = summaryObject("pending");
  const serialized = JSON.stringify(summary);
  for (const pattern of SENSITIVE_PATTERNS) {
    securityChecks.push({
      pattern,
      result: serialized.includes(pattern) ? "failed" : "passed"
    });
  }
  if (securityChecks.some((check) => check.result === "failed")) {
    recordCase("security redaction scan", "failed", "summary contained forbidden text");
  } else {
    recordCase("security redaction scan", "passed", "summary did not contain forbidden text");
  }
}

function finish(status) {
  const summary = summaryObject(status);
  console.log(JSON.stringify(summary, null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}

function summaryObject(status) {
  return {
    status,
    runId,
    listenAddress: url.replace(/^http:\/\//, ""),
    preExistingInstanceCount,
    createdSmokeInstances,
    cleanupResult: cleanupResult(),
    cases,
    securityChecks,
    skipped
  };
}

function cleanupResult() {
  const cleanupCases = cases.filter((item) => item.name.startsWith("cleanup "));
  if (cleanupCases.length === 0) return "not-run";
  if (cleanupCases.every((item) => item.result === "passed")) return "passed";
  return "failed";
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
    return process.env.APPDATA ? join(process.env.APPDATA, appId, "api-token.json") : undefined;
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return join(base, appId, "api-token.json");
}

function trimTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}
