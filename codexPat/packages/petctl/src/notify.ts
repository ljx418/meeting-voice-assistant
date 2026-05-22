import { validatePetEvent, type PetEvent } from "@agent-desktop-pet/pet-protocol";
import { resolveToken, resolveUrl } from "./config.js";
import { EXIT_CODES, type CliResult } from "./output.js";

export type NotifyOptions = {
  event: unknown;
  token?: string;
  url?: string;
  instance?: string;
  fetchImpl?: typeof fetch;
};

export async function notify(options: NotifyOptions): Promise<CliResult> {
  if (hasVia(options.event)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "schema_invalid",
      reason: "payload must not include via"
    };
  }

  const validation = validatePetEvent(options.event);
  if (!validation.valid) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "schema_invalid",
      reason: validation.errors.map((error) => error.message).filter(Boolean).join("; ") || "local validation failed"
    };
  }

  const token = resolveToken(options.token);
  if (!token.value) {
    return {
      ok: false,
      exitCode: EXIT_CODES.tokenMissing,
      reasonCode: "token_missing",
      reason: "token not found; use --token or AGENT_DESKTOP_PET_TOKEN"
    };
  }

  const url = resolveUrl(options.url).value!;
  const instanceResolution = resolveInstance(options.instance);
  if (instanceResolution.value && !isValidInstanceId(instanceResolution.value)) {
    return {
      ok: false,
      exitCode: EXIT_CODES.localValidation,
      reasonCode: "instance_id_invalid",
      reason: "instance id is invalid"
    };
  }
  const fetchImpl = options.fetchImpl ?? fetch;
  const endpoint = instanceResolution.value
    ? `${url}/api/instances/${encodeURIComponent(instanceResolution.value)}/events`
    : `${url}/api/events`;

  let response: Response;
  try {
    response = await fetchImpl(endpoint, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token.value}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify(options.event as PetEvent)
    });
  } catch (error) {
    return {
      ok: false,
      exitCode: EXIT_CODES.desktopNotRunning,
      reasonCode: "desktop_not_running",
      reason: error instanceof Error ? error.message : "desktop app is not reachable"
    };
  }

  const body = await readJson(response);
  if (response.ok && body?.ok === true && body.accepted === true) {
    return {
      ok: true,
      exitCode: EXIT_CODES.success,
      eventId: typeof body.eventId === "string" ? body.eventId : undefined,
      queued: body.queued === true
    };
  }

  const reasonCode = typeof body?.reasonCode === "string" ? body.reasonCode : statusReasonCode(response.status);
  const reason = typeof body?.reason === "string" ? body.reason : response.statusText || "request failed";
  return {
    ok: false,
    exitCode: exitCodeFor(response.status, reasonCode),
    reasonCode,
    reason
  };
}

async function readJson(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function hasVia(value: unknown) {
  return typeof value === "object" && value !== null && "via" in value;
}

function resolveInstance(cliInstance?: string) {
  if (cliInstance) return { value: cliInstance, source: "cli" };
  if (process.env.AGENT_DESKTOP_PET_INSTANCE_ID) {
    return { value: process.env.AGENT_DESKTOP_PET_INSTANCE_ID, source: "env" };
  }
  return {};
}

function isValidInstanceId(value: string) {
  return /^[A-Za-z0-9._-]{1,64}$/.test(value) && !value.includes("..");
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
  if (status === 404 || reasonCode === "instance_not_found") return EXIT_CODES.rejectedByBridge400;
  if (status === 400) return EXIT_CODES.rejectedByBridge400;
  return EXIT_CODES.genericError;
}
