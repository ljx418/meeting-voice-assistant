#!/usr/bin/env node
import { existsSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawnSync } from "node:child_process";

const repoRoot = resolve(new URL("..", import.meta.url).pathname);
const petctlBin = process.env.PETCTL_BIN
  ? resolve(process.env.PETCTL_BIN)
  : join(repoRoot, "packages/petctl/dist/cli.js");
const hookConfig = join(repoRoot, ".codex/hooks.json");
const cases = [];

try {
  main();
} catch (error) {
  recordCase("unexpected error", "failed", error instanceof Error ? error.message : String(error));
  finish("failed");
}

function main() {
  const version = spawnSync("codex", ["--version"], { cwd: repoRoot, encoding: "utf8" });
  if (version.status !== 0) {
    recordCase("Codex CLI available", "blocked", "codex_not_available");
    finish("blocked");
    return;
  }
  recordCase("Codex CLI available", "passed", safeVersion(version.stdout || version.stderr));

  if (!existsSync(petctlBin)) {
    recordCase("petctl dist exists", "blocked", "build petctl first");
    finish("blocked");
    return;
  }
  recordCase("petctl dist exists", "passed", "present");

  if (!existsSync(hookConfig)) {
    recordCase("project hook config exists", "blocked", ".codex/hooks.json missing");
    finish("blocked");
    return;
  }
  recordCase("project hook config exists", "passed", "present");

  if (process.env.CODEX_PET_HOOK_TRUST_CONFIRMED !== "1") {
    recordCase("Codex hook trust review", "blocked", "run /hooks and set CODEX_PET_HOOK_TRUST_CONFIRMED=1 after review");
    finish("blocked");
    return;
  }

  recordCase("Codex hook trust review", "passed", "operator confirmed");
  recordCase("real lifecycle trigger", "blocked", "manual trusted Codex lifecycle run required for no-false-green acceptance");
  finish("blocked");
}

function safeVersion(value) {
  return value.replace(/[^A-Za-z0-9 ._-]/g, "").trim().slice(0, 80);
}

function recordCase(name, result, details) {
  cases.push({ name, result, details });
}

function finish(status) {
  console.log(JSON.stringify({ status, cases }, null, 2));
  process.exitCode = status === "passed" ? 0 : status === "blocked" ? 2 : 1;
}
