import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { createHash, randomUUID } from "node:crypto";
import { spawnSync } from "node:child_process";
import { attachCodex } from "./instances.js";
import { listInstances } from "./instances.js";
import { notify } from "./notify.js";
import { runCodexProbe } from "./codex-probe.js";
import { EXIT_CODES, type CliResult } from "./output.js";
import type { PetEventLevel } from "@agent-desktop-pet/pet-protocol";

export type CodexBindPreviewOptions = {
  terminal: "terminal";
  now?: Date;
  storePath?: string;
  spawnImpl?: typeof spawnSync;
};

export type CodexBindConfirmOptions = {
  candidateId: string;
  name?: string;
  token?: string;
  url?: string;
  now?: Date;
  storePath?: string;
  spawnImpl?: typeof spawnSync;
  fetchImpl?: typeof fetch;
};

export type CodexRouteTestOptions = {
  bindingId: string;
  level: PetEventLevel;
  token?: string;
  url?: string;
  now?: Date;
  storePath?: string;
  spawnImpl?: typeof spawnSync;
  fetchImpl?: typeof fetch;
};

type BindingStatus = "candidate" | "active" | "stale" | "expired";

type SafeCandidate = {
  candidateId: string;
  terminalAppName: string;
  terminalBundleId: string;
  processId: number;
  processName: string;
  codexCliVersion?: string;
  ttySummary: string;
  sessionSummary: string;
  candidateObservedAt: string;
  expiresAt: string;
  bindingStatus: BindingStatus;
};

type SafeBinding = SafeCandidate & {
  bindingId: string;
  petInstanceId: string;
  bindingCreatedAt: string;
  lastValidatedAt: string;
  bindingStatus: BindingStatus;
};

type Store = {
  candidates: SafeCandidate[];
  bindings: SafeBinding[];
};

const CANDIDATE_TTL_MS = 5 * 60 * 1000;
const BINDING_TTL_MS = 60 * 60 * 1000;

export async function previewCodexBinding(options: CodexBindPreviewOptions): Promise<CliResult> {
  const observedAt = options.now ?? new Date();
  const probe = await runCodexProbe({
    terminal: options.terminal,
    spawnImpl: options.spawnImpl
  });
  if (!probe.ok || !probe.probe) return probe;

  const candidate = candidateFromProbe(probe, observedAt);
  if (!candidate) {
    return bindingFailure("candidate_invalid", "candidate is invalid");
  }

  const store = readStore(options.storePath);
  store.candidates = [
    ...store.candidates.filter((item) => item.expiresAt > observedAt.toISOString()),
    candidate
  ].slice(-20);
  writeStore(store, options.storePath);

  return {
    ok: true,
    exitCode: EXIT_CODES.success,
    codexBinding: candidate
  };
}

export async function confirmCodexBinding(options: CodexBindConfirmOptions): Promise<CliResult> {
  if (!isValidCandidateId(options.candidateId)) {
    return bindingFailure("candidate_id_invalid", "candidate id is invalid");
  }

  const now = options.now ?? new Date();
  const store = readStore(options.storePath);
  const candidate = store.candidates.find((item) => item.candidateId === options.candidateId);
  if (!candidate) {
    return bindingFailure("candidate_not_found", "candidate not found", { candidateId: options.candidateId });
  }
  if (candidate.expiresAt <= now.toISOString()) {
    candidate.bindingStatus = "expired";
    writeStore(store, options.storePath);
    return bindingFailure("candidate_expired", "candidate expired", candidate);
  }

  const revalidated = revalidateCandidateProcess(candidate, options.spawnImpl ?? spawnSync);
  if (!revalidated) {
    return bindingFailure("candidate_not_active", "candidate is not active", candidate);
  }

  const attached = await attachCodex({
    token: options.token,
    url: options.url,
    name: options.name ?? "Codex Cat",
    fetchImpl: options.fetchImpl
  });
  if (!attached.ok || !attached.instanceId) return attached;

  const binding: SafeBinding = {
    ...candidate,
    bindingId: `bind_${randomUUID().replace(/-/g, "").slice(0, 24)}`,
    petInstanceId: attached.instanceId,
    bindingCreatedAt: now.toISOString(),
    lastValidatedAt: now.toISOString(),
    expiresAt: new Date(now.getTime() + BINDING_TTL_MS).toISOString(),
    bindingStatus: "active"
  };
  store.bindings = [
    ...store.bindings.filter((item) => item.bindingId !== binding.bindingId),
    binding
  ].slice(-50);
  store.candidates = store.candidates.filter((item) => item.candidateId !== candidate.candidateId);
  writeStore(store, options.storePath);

  return {
    ok: true,
    exitCode: EXIT_CODES.success,
    instanceId: attached.instanceId,
    displayName: attached.displayName,
    windowLabel: attached.windowLabel,
    codexBinding: binding
  };
}

export async function routeCodexBindingTest(options: CodexRouteTestOptions): Promise<CliResult> {
  if (!isValidBindingId(options.bindingId)) {
    return bindingFailure("binding_id_invalid", "binding id is invalid", { bindingId: options.bindingId });
  }
  if (!isValidLevel(options.level)) {
    return bindingFailure("level_invalid", "level is invalid", { bindingId: options.bindingId });
  }

  const now = options.now ?? new Date();
  const store = readStore(options.storePath);
  const binding = store.bindings.find((item) => item.bindingId === options.bindingId);
  if (!binding) {
    return bindingFailure("binding_not_found", "binding not found", { bindingId: options.bindingId });
  }
  if (binding.terminalBundleId !== "com.apple.Terminal") {
    return bindingFailure("terminal_mismatch", "terminal mismatch", binding);
  }
  if (binding.bindingStatus !== "active" || binding.expiresAt <= now.toISOString()) {
    binding.bindingStatus = "stale";
    writeStore(store, options.storePath);
    return bindingFailure("binding_stale", "binding is stale", binding);
  }
  if (!revalidateCandidateProcess(binding, options.spawnImpl ?? spawnSync)) {
    binding.bindingStatus = "stale";
    writeStore(store, options.storePath);
    return bindingFailure("candidate_not_active", "candidate is not active", binding);
  }

  const listed = await listInstances({
    token: options.token,
    url: options.url,
    fetchImpl: options.fetchImpl
  });
  if (!listed.ok) return { ...listed, codexBinding: binding };
  const petExists = listed.instances?.some((item) => item.instanceId === binding.petInstanceId) === true;
  if (!petExists) {
    return bindingFailure("pet_instance_not_found", "pet instance not found", binding);
  }

  const routed = await notify({
    token: options.token,
    url: options.url,
    instance: binding.petInstanceId,
    fetchImpl: options.fetchImpl,
    event: {
      source: { id: "codex.local", kind: "codex", name: "Codex" },
      level: options.level,
      title: "Codex manual route test",
      sound: "none",
      metadata: {
        codexBinding: "terminal-app-manual-route-test",
        bindingId: binding.bindingId,
        routeTest: "true",
        lifecycleEvidence: "false"
      }
    }
  });
  return {
    ...routed,
    instanceId: binding.petInstanceId,
    codexBinding: {
      ...binding,
      lastValidatedAt: now.toISOString()
    }
  };
}

function candidateFromProbe(result: CliResult, observedAt: Date): SafeCandidate | undefined {
  const probe = result.probe;
  if (
    !probe ||
    probe.terminalBundleId !== "com.apple.Terminal" ||
    probe.processName !== "codex" ||
    probe.verdict !== "candidate" ||
    !probe.terminalAppName ||
    !probe.processId ||
    !probe.ttySummary ||
    !probe.sessionSummary
  ) {
    return undefined;
  }
  return {
    candidateId: `cand_${randomUUID().replace(/-/g, "").slice(0, 24)}`,
    terminalAppName: probe.terminalAppName,
    terminalBundleId: probe.terminalBundleId,
    processId: probe.processId,
    processName: "codex",
    codexCliVersion: probe.codexCliVersion,
    ttySummary: probe.ttySummary,
    sessionSummary: probe.sessionSummary,
    candidateObservedAt: observedAt.toISOString(),
    expiresAt: new Date(observedAt.getTime() + CANDIDATE_TTL_MS).toISOString(),
    bindingStatus: "candidate"
  };
}

function revalidateCandidateProcess(candidate: SafeCandidate, spawnImpl: typeof spawnSync) {
  const processInfo = spawnImpl("ps", ["-p", String(candidate.processId), "-o", "comm=,tty="], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 64 * 1024
  }) as ProbeResult;
  if (processInfo.status !== 0) return false;
  const match = String(processInfo.stdout || "").trim().match(/^(\S+)\s+(\S+)$/);
  if (!match) return false;
  const [, command, tty] = match;
  if (redactedSummary(tty, "tty") !== candidate.ttySummary) return false;
  if (redactedSummary(tty, "session") !== candidate.sessionSummary) return false;

  const commandName = command.split("/").pop() ?? command;
  if (/^codex(?:\.js)?$/i.test(commandName)) return true;
  if (!/^(?:node|nodejs|npm|npx|env|n)$/i.test(commandName)) return false;

  const args = spawnImpl("ps", ["-p", String(candidate.processId), "-o", "args="], {
    encoding: "utf8",
    timeout: 3000,
    maxBuffer: 64 * 1024
  }) as ProbeResult;
  if (args.status !== 0) return false;
  return codexArgsSignature(String(args.stdout || ""));
}

function bindingFailure(reasonCode: string, reason: string, codexBinding?: CliResult["codexBinding"]): CliResult {
  return {
    ok: false,
    exitCode: EXIT_CODES.localValidation,
    reasonCode,
    reason,
    codexBinding
  };
}

function readStore(path = defaultStorePath()): Store {
  if (!existsSync(path)) return { candidates: [], bindings: [] };
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8")) as Partial<Store>;
    return {
      candidates: Array.isArray(parsed.candidates) ? parsed.candidates.filter(isSafeCandidate) : [],
      bindings: Array.isArray(parsed.bindings) ? parsed.bindings.filter(isSafeBinding) : []
    };
  } catch {
    return { candidates: [], bindings: [] };
  }
}

function writeStore(store: Store, path = defaultStorePath()) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(store, null, 2)}\n`, { mode: 0o600 });
}

function defaultStorePath() {
  if (process.env.AGENT_DESKTOP_PET_BINDING_STORE) {
    return process.env.AGENT_DESKTOP_PET_BINDING_STORE;
  }
  const appId = "com.agentdesktoppet.desktop";
  if (process.platform === "darwin") {
    return join(homedir(), "Library", "Application Support", appId, "codex-bindings.json");
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return join(base, appId, "codex-bindings.json");
}

type ProbeResult = ReturnType<typeof spawnSync>;

function redactedSummary(value: string | undefined, prefix: string) {
  if (!value) return undefined;
  const safe = value.replace(/^\/dev\//, "");
  if (!/^[A-Za-z0-9._/-]{1,64}$/.test(safe)) return undefined;
  const digest = createHash("sha256").update(safe).digest("hex").slice(0, 12);
  return `${prefix}_${digest}`;
}

function codexArgsSignature(args: string) {
  const normalized = args.replace(/\\/g, "/").toLowerCase();
  return (
    normalized.includes("@openai/codex") ||
    normalized.includes("/codex/bin/") ||
    normalized.includes("/codex-cli/")
  );
}

function isSafeCandidate(value: unknown): value is SafeCandidate {
  const item = value as SafeCandidate;
  return Boolean(
    item &&
    isValidCandidateId(item.candidateId) &&
    item.terminalBundleId === "com.apple.Terminal" &&
    typeof item.processId === "number" &&
    item.processName === "codex" &&
    /^tty_[a-f0-9]{12}$/.test(item.ttySummary) &&
    /^session_[a-f0-9]{12}$/.test(item.sessionSummary) &&
    typeof item.candidateObservedAt === "string" &&
    typeof item.expiresAt === "string"
  );
}

function isSafeBinding(value: unknown): value is SafeBinding {
  const item = value as SafeBinding;
  return Boolean(
    isSafeCandidate(item) &&
    /^bind_[A-Za-z0-9]{1,64}$/.test(item.bindingId) &&
    /^[A-Za-z0-9._-]{1,64}$/.test(item.petInstanceId) &&
    typeof item.bindingCreatedAt === "string" &&
    typeof item.lastValidatedAt === "string" &&
    item.bindingStatus === "active"
  );
}

function isValidCandidateId(value: string) {
  return /^cand_[A-Za-z0-9]{1,64}$/.test(value);
}

function isValidBindingId(value: string) {
  return /^bind_[A-Za-z0-9]{1,64}$/.test(value);
}

function isValidLevel(value: string): value is PetEventLevel {
  return ["idle", "thinking", "running", "need_input", "success", "error"].includes(value);
}
