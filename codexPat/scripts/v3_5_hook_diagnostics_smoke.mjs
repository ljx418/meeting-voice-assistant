#!/usr/bin/env node
import { spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = join(repoRoot, "packages/petctl/dist/cli.js");
const cases = [];

function recordCase(name, status, detail = "") {
  cases.push({ name, status, detail });
}

function assertCase(name, condition, detail = "") {
  recordCase(name, condition ? "passed" : "failed", detail);
}

try {
  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "run pnpm --filter @agent-desktop-pet/petctl build");
  } else {
    recordCase("petctl dist exists", "passed", "present");

    const healthy = runDoctor({ AGENT_DESKTOP_PET_INSTANCE_ID: "codex_v35_smoke" });
    assertCase("codex doctor exits 0", healthy.status === 0, `status=${healthy.status}`);
    assertDiagnostic(healthy.json, "hook_config", "passed");
    assertDiagnostic(healthy.json, "hook_wrapper", "passed");
    assertDiagnostic(healthy.json, "instance_env", "passed");
    assertCase("codex doctor reports codex cli version field", hasDiagnostic(healthy.json, "codex_cli"), "codex_cli diagnostic present");
    assertCase("desktop unavailable is non-hard diagnostic", hasDiagnostic(healthy.json, "desktop_health"), "desktop_health diagnostic present");
    assertNoLeaks("healthy diagnostics output", healthy.text);

    const missingEnv = runDoctor({});
    assertCase("missing instance env exits 0", missingEnv.status === 0, `status=${missingEnv.status}`);
    assertDiagnostic(missingEnv.json, "instance_env", "warning");
    assertNoLeaks("missing env diagnostics output", missingEnv.text);

    const badEnv = runDoctor({ AGENT_DESKTOP_PET_INSTANCE_ID: "../../bad" });
    assertCase("invalid instance env fails safely", badEnv.status !== 0, `status=${badEnv.status}`);
    assertDiagnostic(badEnv.json, "instance_env", "failed");
    assertCase("invalid instance env reports safe code", hasReason(badEnv.json, "instance_id_invalid"), "reasonCode=instance_id_invalid");
    assertNoLeaks("invalid env diagnostics output", badEnv.text);

    const tempRoot = mkdtempSync(join(tmpdir(), "agent-desktop-pet-v35-doctor-"));
    try {
      writeFileSync(join(tempRoot, "placeholder.txt"), "no hook config");
      const missingConfig = spawnSync(process.execPath, [petctlBin, "codex", "doctor", "--json"], {
        cwd: tempRoot,
        env: {
          ...process.env,
          CODEX_PET_PROJECT_ROOT: tempRoot,
          AGENT_DESKTOP_PET_TOKEN: "v3_5_smoke_secret",
          AGENT_DESKTOP_PET_INSTANCE_ID: "codex_v35_smoke"
        },
        encoding: "utf8"
      });
      const parsed = parseJson(missingConfig.stdout || missingConfig.stderr);
      assertCase("missing hook config fails safely", missingConfig.status !== 0, `status=${missingConfig.status}`);
      assertDiagnostic(parsed, "hook_config", "failed");
      assertNoLeaks("missing hook config output", `${missingConfig.stdout}${missingConfig.stderr}`);
    } finally {
      rmSync(tempRoot, { recursive: true, force: true });
    }
  }
} catch (error) {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : "unknown");
}

const failed = cases.filter((item) => item.status === "failed");
const blocked = cases.filter((item) => item.status === "blocked");
for (const item of cases) {
  console.log(`${item.status.toUpperCase()} ${item.name}${item.detail ? ` - ${item.detail}` : ""}`);
}

if (failed.length > 0) {
  process.exitCode = 1;
} else if (blocked.length > 0) {
  process.exitCode = 2;
}

function runDoctor(extraEnv) {
  const result = spawnSync(process.execPath, [petctlBin, "codex", "doctor", "--json"], {
    cwd: repoRoot,
    env: {
      ...process.env,
      AGENT_DESKTOP_PET_TOKEN: "v3_5_smoke_secret",
      ...extraEnv
    },
    encoding: "utf8"
  });
  const text = `${result.stdout}${result.stderr}`;
  return {
    status: result.status,
    text,
    json: parseJson(result.stdout || result.stderr)
  };
}

function parseJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return {};
  }
}

function hasDiagnostic(summary, name) {
  return Array.isArray(summary?.diagnostics) && summary.diagnostics.some((diagnostic) => diagnostic.name === name);
}

function assertDiagnostic(summary, name, status) {
  const diagnostic = Array.isArray(summary?.diagnostics)
    ? summary.diagnostics.find((item) => item.name === name)
    : undefined;
  assertCase(`${name} diagnostic is ${status}`, diagnostic?.status === status, `status=${diagnostic?.status || "missing"}`);
}

function hasReason(summary, reasonCode) {
  return summary?.reasonCode === reasonCode
    || (Array.isArray(summary?.diagnostics) && summary.diagnostics.some((diagnostic) => diagnostic.reasonCode === reasonCode));
}

function assertNoLeaks(name, text) {
  const leaked = [
    /v3_5_smoke_secret/,
    /Authorization/i,
    /Bearer\s+/i,
    /raw payload/i,
    /api-token\.json/,
    /\/Users\/[^\s"]+/,
    /workspace\/codexPat/,
    /\.\.\/\.\.\/bad/
  ].some((pattern) => pattern.test(text));
  assertCase(`${name} redaction scan`, !leaked, leaked ? "leak_detected" : "no sensitive output");
}
