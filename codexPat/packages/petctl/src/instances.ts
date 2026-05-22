import { resolveToken, resolveUrl } from "./config.js";
import { EXIT_CODES, type CliResult } from "./output.js";

export type AttachOptions = {
  token?: string;
  url?: string;
  name?: string;
  workspaceLabel?: string;
  workspaceHash?: string;
  fetchImpl?: typeof fetch;
};

export type ListOptions = {
  token?: string;
  url?: string;
  fetchImpl?: typeof fetch;
};

export type DetachOptions = {
  token?: string;
  url?: string;
  instance: string;
  fetchImpl?: typeof fetch;
};

export async function attachCodex(options: AttachOptions): Promise<CliResult> {
  const displayName = options.name ?? "Codex Cat";
  if (!isValidDisplayName(displayName)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "display_name_invalid",
      reason: "display name is invalid"
    };
  }
  if (options.workspaceLabel !== undefined && !isValidWorkspaceLabel(options.workspaceLabel)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "workspace_label_invalid",
      reason: "workspace label is invalid"
    };
  }
  if (options.workspaceHash !== undefined && !isValidWorkspaceHash(options.workspaceHash)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "workspace_hash_invalid",
      reason: "workspace hash is invalid"
    };
  }

  const token = resolveToken(options.token);
  if (!token.value) {
    return tokenMissing();
  }

  const url = resolveUrl(options.url).value!;
  const fetchImpl = options.fetchImpl ?? fetch;
  let response: Response;
  try {
    response = await fetchImpl(`${url}/api/instances`, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token.value}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        sourceKind: "codex",
        sourceId: "codex.local",
        displayName,
        workspaceLabel: options.workspaceLabel,
        workspaceHash: options.workspaceHash
      })
    });
  } catch (error) {
    return desktopNotRunning(error);
  }

  const body = await readJson(response);
  if (response.ok && body?.ok === true && typeof body.instanceId === "string") {
    return {
      ok: true,
      exitCode: EXIT_CODES.success,
      instanceId: body.instanceId,
      displayName: typeof body.displayName === "string" ? body.displayName : displayName,
      windowLabel: typeof body.windowLabel === "string" ? body.windowLabel : undefined,
      exportCommand: typeof body.export === "string" ? body.export : `export AGENT_DESKTOP_PET_INSTANCE_ID=${body.instanceId}`,
      raw: body
    };
  }

  return rejected(response, body);
}

export async function listInstances(options: ListOptions): Promise<CliResult> {
  const token = resolveToken(options.token);
  if (!token.value) {
    return tokenMissing();
  }

  const url = resolveUrl(options.url).value!;
  const fetchImpl = options.fetchImpl ?? fetch;
  let response: Response;
  try {
    response = await fetchImpl(`${url}/api/instances`, {
      method: "GET",
      headers: {
        "Authorization": `Bearer ${token.value}`
      }
    });
  } catch (error) {
    return desktopNotRunning(error);
  }

  const body = await readJson(response);
  if (response.ok && body?.ok === true && Array.isArray(body.instances)) {
    return {
      ok: true,
      exitCode: EXIT_CODES.success,
      instances: body.instances,
      raw: body
    };
  }

  return rejected(response, body);
}

export async function detachInstance(options: DetachOptions): Promise<CliResult> {
  if (!isValidInstanceId(options.instance)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "instance_id_invalid",
      reason: "instance id is invalid"
    };
  }

  const token = resolveToken(options.token);
  if (!token.value) {
    return tokenMissing();
  }

  const url = resolveUrl(options.url).value!;
  const fetchImpl = options.fetchImpl ?? fetch;
  let response: Response;
  try {
    response = await fetchImpl(`${url}/api/instances/${encodeURIComponent(options.instance)}`, {
      method: "DELETE",
      headers: {
        "Authorization": `Bearer ${token.value}`
      }
    });
  } catch (error) {
    return desktopNotRunning(error);
  }

  const body = await readJson(response);
  if (response.ok && body?.ok === true && body.detached === true) {
    return {
      ok: true,
      exitCode: EXIT_CODES.success,
      instanceId: typeof body.instanceId === "string" ? body.instanceId : options.instance,
      windowLabel: typeof body.windowLabel === "string" ? body.windowLabel : undefined,
      raw: body
    };
  }

  return rejected(response, body);
}

async function readJson(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function tokenMissing(): CliResult {
  return {
    ok: false,
    exitCode: EXIT_CODES.tokenMissing,
    reasonCode: "token_missing",
    reason: "token not found; use --token or AGENT_DESKTOP_PET_TOKEN"
  };
}

function desktopNotRunning(error: unknown): CliResult {
  return {
    ok: false,
    exitCode: EXIT_CODES.desktopNotRunning,
    reasonCode: "desktop_not_running",
    reason: error instanceof Error ? error.message : "desktop app is not reachable"
  };
}

function rejected(response: Response, body: any): CliResult {
  const reasonCode = typeof body?.reasonCode === "string" ? body.reasonCode : statusReasonCode(response.status);
  const reason = typeof body?.reason === "string" ? body.reason : response.statusText || "request failed";
  return {
    ok: false,
    exitCode: exitCodeFor(response.status, reasonCode),
    reasonCode,
    reason
  };
}

function statusReasonCode(status: number) {
  if (status === 401) return "unauthorized";
  if (status === 429) return "rate_limited";
  if (status === 503) return "bridge_unavailable";
  if (status === 400) return "schema_invalid";
  if (status === 404) return "instance_not_found";
  return "unknown_error";
}

function exitCodeFor(status: number, reasonCode: string) {
  if (status === 401) return EXIT_CODES.unauthorized;
  if (status === 429 || reasonCode === "rate_limited" || reasonCode === "queue_full") return EXIT_CODES.rateLimited;
  if (status === 503 || reasonCode === "bridge_unavailable") return EXIT_CODES.bridgeUnavailable;
  if (status === 400 || status === 404) return EXIT_CODES.rejectedByBridge400;
  return EXIT_CODES.genericError;
}

function isValidDisplayName(value: string) {
  return value.length >= 1 && value.length <= 40 && !/[\u0000-\u001F\u007F/\\:]/.test(value);
}

function isValidWorkspaceLabel(value: string) {
  return value.length <= 80 && !/[\u0000-\u001F\u007F/\\:]/.test(value);
}

function isValidWorkspaceHash(value: string) {
  return /^[A-Za-z0-9_-]{1,128}$/.test(value);
}

function isValidInstanceId(value: string) {
  return /^[A-Za-z0-9._-]{1,64}$/.test(value) && !value.includes("..");
}
