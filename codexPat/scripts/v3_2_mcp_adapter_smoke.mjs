#!/usr/bin/env node
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawn, spawnSync } from "node:child_process";

const HARD_LIMIT = 12;
const REQUIRED_FREE_SLOTS = 1;
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
const petMcpBin = process.env.PET_MCP_BIN
  ? resolve(process.env.PET_MCP_BIN)
  : join(repoRoot, "packages/pet-mcp/dist/index.js");
const runId = `${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
const cases = [];
const createdSmokeInstances = [];
let mcp;

main().catch(async (error) => {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  await cleanup();
  if (mcp) mcp.close();
  finish("failed");
});

async function main() {
  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "build petctl first: pnpm --filter @agent-desktop-pet/petctl build");
    finish("blocked");
    return;
  }
  if (!existsSync(petMcpBin)) {
    recordCase("pet-mcp dist exists", "blocked", "build pet-mcp first: pnpm --filter @agent-desktop-pet/pet-mcp build");
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

  const initialList = runPetctl(["list", "--json"]);
  if (!initialList.ok) {
    recordCase("petctl list baseline", "blocked", initialList.reasonCode || "list_failed");
    finish("blocked");
    return;
  }
  const initialInstances = initialList.json.instances || [];
  recordCase("read current instance list", "passed", `preExistingInstanceCount=${initialInstances.length}`);
  if (initialInstances.length > HARD_LIMIT - REQUIRED_FREE_SLOTS) {
    recordCase("free slot for MCP smoke", "blocked", `need at least ${REQUIRED_FREE_SLOTS} free slot`);
    finish("blocked");
    return;
  }

  mcp = startMcp();
  await mcp.request("initialize", {
    protocolVersion: "2024-11-05",
    capabilities: {},
    clientInfo: { name: "v3_2_mcp_adapter_smoke", version: "0.1.0" }
  });
  recordCase("mcp initialize", "passed", "server initialized");

  const tools = await mcp.request("tools/list", {});
  const toolNames = new Set((tools.tools || []).map((tool) => tool.name));
  assertCase("mcp tools listed", ["pet_notify", "pet_list_instances", "pet_get_capabilities", "pet_get_state"].every((name) => toolNames.has(name)), `tools=${[...toolNames].join(",")}`);

  const instance = attachSmokeInstance(`MCP Smoke Cat ${runId}`);
  if (!instance) {
    await cleanup();
    mcp.close();
    finish("failed");
    return;
  }

  const listResult = await callTool("pet_list_instances", {});
  assertCase("pet_list_instances returns sanitized list", listResult.ok === true && !JSON.stringify(listResult).includes("/Users/"), "no local paths in response");

  const capabilities = await callTool("pet_get_capabilities", {});
  assertCase("pet_get_capabilities returns public summary", capabilities.ok === true && Boolean(capabilities.capabilities), "capabilities present");

  const beforeDefault = listInstances();
  const defaultNotify = await callTool("pet_notify", {
    event: {
      source: { id: "mcp-smoke.local", kind: "custom", name: "MCP Smoke" },
      level: "success",
      title: "MCP default smoke",
      sound: "none"
    }
  });
  assertCase("pet_notify default route accepted", defaultNotify.ok === true && defaultNotify.accepted === true, `reasonCode=${defaultNotify.reasonCode || "none"}`);
  assertCase("pet_notify default route does not alter smoke instance", stateOf(listInstances(), instance.instanceId) === stateOf(beforeDefault, instance.instanceId), "target instance unchanged");

  const instanceNotify = await callTool("pet_notify", {
    instanceId: instance.instanceId,
    event: {
      source: { id: "mcp-smoke.local", kind: "custom", name: "MCP Smoke" },
      level: "need_input",
      title: "MCP instance smoke",
      sound: "none"
    }
  });
  assertCase("pet_notify instance route accepted", instanceNotify.ok === true && instanceNotify.accepted === true, `reasonCode=${instanceNotify.reasonCode || "none"}`);
  assertCase("pet_notify instance route updates target", stateOf(listInstances(), instance.instanceId) === "need_input", "target instance state=need_input");

  const state = await callTool("pet_get_state", { instanceId: instance.instanceId });
  assertCase("pet_get_state returns target state", state.ok === true && state.instance?.currentState === "need_input", "state read back");

  const unknown = await callTool("pet_notify", {
    instanceId: "not-found",
    event: {
      source: { id: "mcp-smoke.local", kind: "custom" },
      level: "success"
    }
  });
  assertCase("unknown instance returns instance_not_found", unknown.ok === false && unknown.reasonCode === "instance_not_found", `reasonCode=${unknown.reasonCode || "none"}`);

  const invalid = await callTool("pet_notify", {
    instanceId: "../../bad",
    event: {
      source: { id: "mcp-smoke.local", kind: "custom" },
      level: "success"
    }
  });
  assertCase("invalid instance returns instance_id_invalid", invalid.ok === false && invalid.reasonCode === "instance_id_invalid", `reasonCode=${invalid.reasonCode || "none"}`);

  const invalidSound = await callTool("pet_notify", {
    instanceId: instance.instanceId,
    event: {
      source: { id: "mcp-smoke.local", kind: "custom" },
      level: "success",
      sound: "../../x.wav"
    }
  });
  assertCase("invalid sound rejected before bridge", invalidSound.ok === false && invalidSound.reasonCode === "schema_invalid", `reasonCode=${invalidSound.reasonCode || "none"}`);

  await cleanup();
  mcp.close();
  securityScan();
  finish(cases.some((item) => item.result === "failed") ? "failed" : cases.some((item) => item.result === "blocked") ? "blocked" : "passed");
}

async function callTool(name, args) {
  const result = await mcp.request("tools/call", { name, arguments: args });
  const text = result.content?.[0]?.text || "{}";
  try {
    return JSON.parse(text);
  } catch {
    return { ok: false, reasonCode: "invalid_tool_response" };
  }
}

function startMcp() {
  const child = spawn(process.execPath, [petMcpBin], {
    cwd: repoRoot,
    env: process.env,
    stdio: ["pipe", "pipe", "pipe"]
  });
  let nextId = 1;
  const pending = new Map();
  let buffer = "";
  child.stdout.on("data", (chunk) => {
    buffer += chunk.toString("utf8");
    let newline;
    while ((newline = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, newline).trim();
      buffer = buffer.slice(newline + 1);
      if (!line) continue;
      const message = JSON.parse(line);
      const waiter = pending.get(message.id);
      if (!waiter) continue;
      pending.delete(message.id);
      if (message.error) waiter.reject(new Error(message.error.message || "mcp error"));
      else waiter.resolve(message.result);
    }
  });
  child.stderr.on("data", (chunk) => {
    recordCase("mcp stderr", "failed", chunk.toString("utf8").trim().slice(0, 120));
  });
  return {
    request(method, params) {
      const id = nextId++;
      const payload = { jsonrpc: "2.0", id, method, params };
      const promise = new Promise((resolvePromise, reject) => {
        pending.set(id, { resolve: resolvePromise, reject });
      });
      child.stdin.write(`${JSON.stringify(payload)}\n`);
      return promise;
    },
    close() {
      child.kill();
    }
  };
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

async function waitForHealth() {
  const url = (process.env.AGENT_DESKTOP_PET_URL || "http://127.0.0.1:17321").replace(/\/+$/, "");
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

function recordCase(name, result, notes = "") {
  cases.push({ name, result, notes });
}

function assertCase(name, condition, notes = "") {
  recordCase(name, condition ? "passed" : "failed", notes);
}

function securityScan() {
  const serialized = JSON.stringify(summaryObject("pending"));
  if (SENSITIVE_PATTERNS.some((pattern) => serialized.includes(pattern))) {
    recordCase("security redaction scan", "failed", "summary contained forbidden text");
  } else {
    recordCase("security redaction scan", "passed", "summary did not contain forbidden text");
  }
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
