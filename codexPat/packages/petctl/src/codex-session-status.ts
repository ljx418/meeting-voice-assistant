import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join } from "node:path";
import { EXIT_CODES, type CliResult } from "./output.js";

export type ManagedSessionMode = "exec" | "tui" | "legacy";
export type ManagedSessionMonitor = "none" | "jsonl" | "hooks";
export type ManagedSessionStatus = "active" | "stale" | "unknown";

type SessionRecord = {
  instanceId: string;
  bindingId: string;
  mode: ManagedSessionMode;
  monitor: ManagedSessionMonitor;
  status: ManagedSessionStatus;
  lastEventKind?: string;
  lastSeenAt: string;
};

type SessionStore = {
  sessions: SessionRecord[];
};

export type TouchSessionOptions = {
  instanceId: string;
  bindingId: string;
  mode: ManagedSessionMode;
  monitor: ManagedSessionMonitor;
  status?: ManagedSessionStatus;
  lastEventKind?: string;
  now?: Date;
  storePath?: string;
};

export type SessionStatusOptions = {
  instanceId?: string;
  now?: Date;
  storePath?: string;
};

const STALE_AFTER_MS = 10 * 60 * 1000;

export function touchManagedSession(options: TouchSessionOptions) {
  if (!isValidInstanceId(options.instanceId) || !isValidBindingId(options.bindingId)) return;
  const now = options.now ?? new Date();
  const store = readSessionStore(options.storePath);
  const record: SessionRecord = {
    instanceId: options.instanceId,
    bindingId: options.bindingId,
    mode: options.mode,
    monitor: options.monitor,
    status: options.status ?? "active",
    lastEventKind: safeEventKind(options.lastEventKind),
    lastSeenAt: now.toISOString()
  };
  store.sessions = [
    ...store.sessions.filter((item) => item.instanceId !== options.instanceId && item.bindingId !== options.bindingId),
    record
  ].slice(-50);
  writeSessionStore(store, options.storePath);
}

export function getManagedSessionStatus(options: SessionStatusOptions = {}): CliResult {
  const now = options.now ?? new Date();
  const store = readSessionStore(options.storePath);
  const candidates = options.instanceId
    ? store.sessions.filter((item) => item.instanceId === options.instanceId)
    : store.sessions;
  const record = candidates.sort((a, b) => b.lastSeenAt.localeCompare(a.lastSeenAt))[0];
  if (!record) {
    return {
      ok: true,
      exitCode: EXIT_CODES.success,
      codexSession: { status: "unknown" }
    };
  }
  const lastSeen = Date.parse(record.lastSeenAt);
  const status = Number.isFinite(lastSeen) && now.getTime() - lastSeen <= STALE_AFTER_MS
    ? record.status
    : "stale";
  return {
    ok: true,
    exitCode: EXIT_CODES.success,
    instanceId: record.instanceId,
    codexSession: {
      instanceId: record.instanceId,
      bindingId: redactBindingId(record.bindingId),
      mode: record.mode,
      monitor: record.monitor,
      status,
      lastEventKind: record.lastEventKind,
      lastSeenAt: record.lastSeenAt
    }
  };
}

function readSessionStore(path = defaultSessionStorePath()): SessionStore {
  if (!existsSync(path)) return { sessions: [] };
  try {
    const parsed = JSON.parse(readFileSync(path, "utf8")) as Partial<SessionStore>;
    return {
      sessions: Array.isArray(parsed.sessions) ? parsed.sessions.filter(isSessionRecord) : []
    };
  } catch {
    return { sessions: [] };
  }
}

function writeSessionStore(store: SessionStore, path = defaultSessionStorePath()) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${JSON.stringify(store, null, 2)}\n`, { mode: 0o600 });
}

function defaultSessionStorePath() {
  if (process.env.AGENT_DESKTOP_PET_SESSION_STORE) return process.env.AGENT_DESKTOP_PET_SESSION_STORE;
  const appId = "com.agentdesktoppet.desktop";
  if (process.platform === "darwin") {
    return join(homedir(), "Library", "Application Support", appId, "codex-sessions.json");
  }
  const base = process.env.XDG_CONFIG_HOME || join(homedir(), ".config");
  return join(base, appId, "codex-sessions.json");
}

function redactBindingId(bindingId: string) {
  const digest = createHash("sha256").update(bindingId).digest("hex").slice(0, 12);
  return `binding_${digest}`;
}

function safeEventKind(value: string | undefined) {
  if (!value) return undefined;
  return /^[A-Za-z0-9._:-]{1,64}$/.test(value) ? value : "unknown";
}

function isSessionRecord(value: unknown): value is SessionRecord {
  const item = value as SessionRecord;
  return Boolean(
    item &&
    isValidInstanceId(item.instanceId) &&
    isValidBindingId(item.bindingId) &&
    ["exec", "tui", "legacy"].includes(item.mode) &&
    ["none", "jsonl", "hooks"].includes(item.monitor) &&
    ["active", "stale", "unknown"].includes(item.status) &&
    typeof item.lastSeenAt === "string" &&
    (item.lastEventKind === undefined || safeEventKind(item.lastEventKind) === item.lastEventKind)
  );
}

function isValidInstanceId(value: string) {
  return /^[A-Za-z0-9._-]{1,64}$/.test(value) && !value.includes("..");
}

function isValidBindingId(value: string) {
  return /^bind_[A-Za-z0-9_]{1,80}$/.test(value);
}
