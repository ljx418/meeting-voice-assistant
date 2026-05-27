import { existsSync, readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export const DEFAULT_URL = "http://127.0.0.1:17321";

export type Resolution = {
  value?: string;
  source?: "cli" | "env" | "config" | "default";
};

export function resolveUrl(cliUrl?: string): Resolution {
  if (cliUrl) return { value: trimTrailingSlash(cliUrl), source: "cli" };
  if (process.env.AGENT_DESKTOP_PET_URL) {
    return { value: trimTrailingSlash(process.env.AGENT_DESKTOP_PET_URL), source: "env" };
  }
  return { value: DEFAULT_URL, source: "default" };
}

export function resolveToken(cliToken?: string): Resolution {
  if (cliToken) return { value: cliToken, source: "cli" };
  if (process.env.AGENT_DESKTOP_PET_TOKEN) return { value: process.env.AGENT_DESKTOP_PET_TOKEN, source: "env" };

  const configPath = tokenConfigPath();
  if (!configPath || !existsSync(configPath)) return {};

  try {
    const parsed = JSON.parse(readFileSync(configPath, "utf8")) as { token?: unknown };
    if (typeof parsed.token === "string" && parsed.token.trim()) {
      return { value: parsed.token, source: "config" };
    }
  } catch {
    return {};
  }
  return {};
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

function trimTrailingSlash(value: string) {
  return value.replace(/\/+$/, "");
}
