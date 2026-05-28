import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const repoRoot = resolve(".");
const cli = resolve("packages/petctl/dist/cli.js");
const temp = mkdtempSync(join(tmpdir(), "pet-personalized-"));
const coreActions = ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"];
const cases = [];

try {
  const packDir = join(temp, "pack");
  const homeDir = join(temp, "home");
  const manifestPath = join(packDir, "manifest.json");
  const assets = {};
  const actions = {};

  mkdirSync(packDir, { recursive: true });
  mkdirSync(homeDir, { recursive: true });

  for (const action of coreActions) {
    const fileName = `${action}.glb`;
    writeFileSync(join(packDir, fileName), `glb-${action}`);
    assets[action] = { assetId: action, kind: "gltf", fileName };
    actions[action] = {
      assetId: action,
      loop: ["idle", "thinking", "running", "sleeping"].includes(action),
      priority: ["error", "need_input"].includes(action) ? "urgent" : ["success", "warning"].includes(action) ? "transient" : "base",
      durationMs: ["error", "need_input"].includes(action) ? 6000 : undefined
    };
  }

  writeFileSync(manifestPath, JSON.stringify({
    schemaVersion: "5.8",
    packId: "mochi-smoke",
    displayName: "Mochi Smoke",
    rendererKind: "gltf",
    license: { type: "user-generated", attribution: "Smoke generated asset" },
    assets,
    actions
  }, null, 2));

  const env = { ...process.env, HOME: homeDir };
  const prompt = run(["asset", "prompt-pack", "--name", "Mochi", "--description", "orange tabby green eyes", "--renderer", "gltf", "--json"], env);
  record("prompt pack exits 0", prompt.status === 0, prompt.output);
  record("prompt pack has core actions", coreActions.every((action) => prompt.output.includes(`"${action}"`)), prompt.output);

  const imported = run(["asset", "import", "--manifest", manifestPath, "--name", "Mochi Smoke", "--json"], env);
  record("asset import exits 0", imported.status === 0, imported.output);
  record("asset import app-managed", imported.output.includes('"appManagedStorage": true'), imported.output);

  const listed = run(["asset", "list", "--json"], env);
  record("asset list includes pack", listed.status === 0 && listed.output.includes("mochi-smoke"), listed.output);

  const activated = run(["asset", "activate", "--pack", "mochi-smoke", "--instance", "codex_123", "--json"], env);
  record("asset activate exits 0", activated.status === 0 && activated.output.includes("codex_123"), activated.output);

  const combined = [prompt.output, imported.output, listed.output, activated.output].join("\n");
  record("security redaction scan", !/(Authorization|api-token\.json|\/Users\/|raw payload|workspace path|config path|file:\/\/|https?:\/\/)/i.test(combined), combined);

  const failed = cases.filter((item) => item.result === "failed");
  console.log(JSON.stringify({ status: failed.length ? "failed" : "passed", cases }, null, 2));
  if (failed.length) process.exit(1);
} finally {
  rmSync(temp, { recursive: true, force: true });
}

function run(args, env) {
  const result = spawnSync(process.execPath, [cli, ...args], {
    cwd: repoRoot,
    env,
    encoding: "utf8"
  });
  return {
    status: result.status,
    output: `${result.stdout || ""}${result.stderr || ""}`
  };
}

function record(name, ok, details) {
  cases.push({
    name,
    result: ok ? "passed" : "failed",
    details: ok ? "ok" : sanitize(details)
  });
}

function sanitize(value) {
  return String(value).replaceAll(temp, "[temp]").slice(0, 200);
}
