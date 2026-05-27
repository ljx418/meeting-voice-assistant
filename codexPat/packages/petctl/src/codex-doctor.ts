import { existsSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { spawnSync, type SpawnSyncReturns } from "node:child_process";
import { resolveToken, resolveUrl } from "./config.js";
import { EXIT_CODES, type CliResult } from "./output.js";

export type CodexDoctorOptions = {
  token?: string;
  url?: string;
  fetchImpl?: typeof fetch;
  spawnImpl?: typeof spawnSync;
  repoRoot?: string;
  strict?: boolean;
  includeInstanceEnv?: boolean;
  includeTrustHint?: boolean;
};

type Diagnostic = NonNullable<CliResult["diagnostics"]>[number];

const REQUIRED_HOOK_EVENTS = [
  "SessionStart",
  "UserPromptSubmit",
  "PreToolUse",
  "PermissionRequest",
  "PostToolUse",
  "Stop"
];

export async function runCodexDoctor(options: CodexDoctorOptions = {}): Promise<CliResult> {
  const repoRoot = options.repoRoot
    ? resolve(options.repoRoot)
    : process.env.CODEX_PET_PROJECT_ROOT
      ? resolve(process.env.CODEX_PET_PROJECT_ROOT)
      : resolve(new URL("../../..", import.meta.url).pathname);
  const spawnImpl = options.spawnImpl ?? spawnSync;
  const diagnostics: Diagnostic[] = [];

  diagnostics.push(codexVersionDiagnostic(spawnImpl, options.strict === true));
  diagnostics.push(hookConfigDiagnostic(repoRoot));
  diagnostics.push(hookWrapperDiagnostic(repoRoot, spawnImpl));
  if (options.includeInstanceEnv !== false) {
    diagnostics.push(instanceEnvDiagnostic());
  }
  if (options.includeTrustHint === true) {
    diagnostics.push(hookTrustDiagnostic());
  }
  diagnostics.push(tokenDiagnostic(options.token, options.strict === true));
  diagnostics.push(await desktopHealthDiagnostic(options, options.fetchImpl ?? fetch, options.strict === true));

  const hardFailure = diagnostics.find((diagnostic) => diagnostic.status === "failed");
  return {
    ok: !hardFailure,
    exitCode: hardFailure ? EXIT_CODES.localValidation : EXIT_CODES.success,
    reasonCode: hardFailure?.reasonCode,
    reason: hardFailure ? "codex hook diagnostics failed" : undefined,
    diagnostics
  };
}

function codexVersionDiagnostic(spawnImpl: typeof spawnSync, strict: boolean): Diagnostic {
  const result = spawnImpl("codex", ["--version"], { encoding: "utf8" });
  if (result.status !== 0) {
    return {
      name: "codex_cli",
      status: strict ? "failed" : "warning",
      reasonCode: "codex_not_found",
      detail: "codex cli unavailable"
    };
  }
  return {
    name: "codex_cli",
    status: "passed",
    detail: sanitizeDetail(String(result.stdout || result.stderr || "").trim() || "version detected")
  };
}

function hookConfigDiagnostic(repoRoot: string): Diagnostic {
  const hookConfigPath = join(repoRoot, ".codex", "hooks.json");
  if (!existsSync(hookConfigPath)) {
    return {
      name: "hook_config",
      status: "failed",
      reasonCode: "hook_config_missing",
      detail: "project hook config missing"
    };
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(readFileSync(hookConfigPath, "utf8"));
  } catch {
    return {
      name: "hook_config",
      status: "failed",
      reasonCode: "hook_config_invalid_json",
      detail: "project hook config is invalid json"
    };
  }

  const hooks = typeof parsed === "object" && parsed !== null && "hooks" in parsed ? (parsed as { hooks?: unknown }).hooks : undefined;
  if (!hooks || typeof hooks !== "object" || Array.isArray(hooks)) {
    return {
      name: "hook_config",
      status: "failed",
      reasonCode: "hook_schema_invalid",
      detail: "project hook config does not match supported schema"
    };
  }

  for (const event of REQUIRED_HOOK_EVENTS) {
    const groups = (hooks as Record<string, unknown>)[event];
    if (!Array.isArray(groups) || groups.length === 0) {
      return {
        name: "hook_config",
        status: "failed",
        reasonCode: "hook_event_missing",
        detail: `${event} missing`
      };
    }
    const hasCommand = groups.some((group) => {
      if (!group || typeof group !== "object") return false;
      const commands = (group as { hooks?: unknown }).hooks;
      return Array.isArray(commands) && commands.some((command) => {
        if (!command || typeof command !== "object") return false;
        const record = command as { type?: unknown; command?: unknown; timeout?: unknown };
        return record.type === "command"
          && typeof record.command === "string"
          && record.command.includes("scripts/codex-pet-hook.mjs")
          && record.command.includes(event)
          && (record.timeout === undefined || typeof record.timeout === "number");
      });
    });
    if (!hasCommand) {
      return {
        name: "hook_config",
        status: "failed",
        reasonCode: "hook_command_missing",
        detail: `${event} command missing`
      };
    }
  }

  return {
    name: "hook_config",
    status: "passed",
    detail: "supported schema detected"
  };
}

function hookWrapperDiagnostic(repoRoot: string, spawnImpl: typeof spawnSync): Diagnostic {
  const wrapperPath = join(repoRoot, "scripts", "codex-pet-hook.mjs");
  if (!existsSync(wrapperPath)) {
    return {
      name: "hook_wrapper",
      status: "failed",
      reasonCode: "hook_wrapper_missing",
      detail: "hook wrapper missing"
    };
  }

  const result = spawnImpl(process.execPath, ["--check", wrapperPath], { encoding: "utf8" }) as SpawnSyncReturns<string>;
  if (result.status !== 0) {
    return {
      name: "hook_wrapper",
      status: "failed",
      reasonCode: "hook_wrapper_syntax_invalid",
      detail: "hook wrapper syntax check failed"
    };
  }
  return {
    name: "hook_wrapper",
    status: "passed",
    detail: "syntax check passed"
  };
}

function instanceEnvDiagnostic(): Diagnostic {
  const value = process.env.AGENT_DESKTOP_PET_INSTANCE_ID;
  if (!value) {
    return {
      name: "instance_env",
      status: "warning",
      reasonCode: "binding_env_missing",
      detail: "instance env missing"
    };
  }
  if (!/^[A-Za-z0-9._-]{1,64}$/.test(value) || value.includes("..")) {
    return {
      name: "instance_env",
      status: "failed",
      reasonCode: "instance_id_invalid",
      detail: "instance env invalid"
    };
  }
  return {
    name: "instance_env",
    status: "passed",
    detail: "instance env present"
  };
}

function hookTrustDiagnostic(): Diagnostic {
  return {
    name: "hook_trust",
    status: "warning",
    reasonCode: "hook_trust_required",
    detail: "run /hooks and trust project hooks before lifecycle acceptance"
  };
}

function tokenDiagnostic(cliToken: string | undefined, strict: boolean): Diagnostic {
  const resolution = resolveToken(cliToken);
  if (!resolution.value) {
    return {
      name: "token",
      status: strict ? "failed" : "warning",
      reasonCode: "token_missing",
      detail: "token missing"
    };
  }
  return {
    name: "token",
    status: "passed",
    detail: `token source ${resolution.source ?? "unknown"}`
  };
}

async function desktopHealthDiagnostic(options: CodexDoctorOptions, fetchImpl: typeof fetch, strict: boolean): Promise<Diagnostic> {
  const url = resolveUrl(options.url).value!;
  try {
    const response = await fetchImpl(`${url}/api/health`);
    const body = await safeJson(response);
    if (response.ok && body?.ok === true) {
      return {
        name: "desktop_health",
        status: "passed",
        detail: "health ok"
      };
    }
    return {
      name: "desktop_health",
      status: strict ? "failed" : "warning",
      reasonCode: "desktop_health_not_ok",
      detail: "desktop health not ok"
    };
  } catch {
    return {
      name: "desktop_health",
      status: strict ? "failed" : "warning",
      reasonCode: "desktop_not_running",
      detail: "desktop unavailable"
    };
  }
}

async function safeJson(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function sanitizeDetail(value: string) {
  return value
    .replace(/Bearer\s+[A-Za-z0-9._~+/=-]+/gi, "Bearer [redacted]")
    .replace(/\/Users\/[^\s"]+/g, "[local-path]")
    .replace(/[A-Za-z]:\\[^\s"]+/g, "[local-path]")
    .replace(/api-token\.json/g, "[token-file]")
    .slice(0, 120);
}
