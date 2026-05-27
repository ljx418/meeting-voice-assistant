import { validatePetEvent, type PetEvent } from "@agent-desktop-pet/pet-protocol";
import { resolveToken, resolveUrl } from "./config.js";

export type BridgeOptions = {
  token?: string;
  url?: string;
  fetchImpl?: typeof fetch;
};

export type ToolResult = {
  ok: boolean;
  reasonCode?: string;
  reason?: string;
  [key: string]: unknown;
};

type BridgeResponse =
  | { ok: true; body: any }
  | { ok: false; reasonCode: string; reason: string };

type ParsedObject =
  | { ok: true; value: Record<string, unknown> }
  | { ok: false; reasonCode: string; reason: string };

export async function petNotify(params: unknown, options: BridgeOptions = {}): Promise<ToolResult> {
  const parsed = parseObject(params);
  if (!parsed.ok) return parsed;

  const event = parsed.value.event;
  const instanceId = optionalString(parsed.value.instanceId);
  if (instanceId && !isValidInstanceId(instanceId)) {
    return rejected("instance_id_invalid", "instance id is invalid");
  }
  if (hasVia(event)) {
    return rejected("schema_invalid", "payload must not include via");
  }

  const validation = validatePetEvent(event);
  if (!validation.valid) {
    return rejected("schema_invalid", "event failed PetEvent schema validation");
  }

  const path = instanceId
    ? `/api/instances/${encodeURIComponent(instanceId)}/events`
    : "/api/events";
  const result = await bridgeRequest(path, {
    method: "POST",
    body: event as PetEvent
  }, options);
  if (!result.ok) return result;

  return {
    ok: true,
    accepted: result.body?.accepted === true,
    eventId: stringOrUndefined(result.body?.eventId),
    queued: result.body?.queued === true,
    instanceId: instanceId || "default"
  };
}

export async function petListInstances(_params: unknown, options: BridgeOptions = {}): Promise<ToolResult> {
  const result = await bridgeRequest("/api/instances", { method: "GET" }, options);
  if (!result.ok) return result;
  return {
    ok: true,
    instances: sanitizeInstances(Array.isArray(result.body?.instances) ? result.body.instances : []),
    limits: sanitizeLimits(result.body?.limits)
  };
}

export async function petGetCapabilities(_params: unknown, options: BridgeOptions = {}): Promise<ToolResult> {
  const result = await publicRequest("/api/capabilities", options);
  if (!result.ok) return result;
  return {
    ok: true,
    capabilities: result.body
  };
}

export async function petGetState(params: unknown, options: BridgeOptions = {}): Promise<ToolResult> {
  const parsed = parseObject(params);
  const instanceId = parsed.ok ? optionalString(parsed.value.instanceId) : undefined;
  if (instanceId && !isValidInstanceId(instanceId)) {
    return rejected("instance_id_invalid", "instance id is invalid");
  }

  const listed = await petListInstances(undefined, options);
  if (!listed.ok) return listed;

  const instances = Array.isArray(listed.instances) ? listed.instances : [];
  if (!instanceId) {
    return { ok: true, instances };
  }

  const instance = instances.find((item) => isRecord(item) && item.instanceId === instanceId);
  if (!instance) {
    return rejected("instance_not_found", "instance was not found");
  }
  return { ok: true, instance };
}

type RequestOptions = {
  method: "GET" | "POST";
  body?: unknown;
};

async function bridgeRequest(path: string, request: RequestOptions, options: BridgeOptions): Promise<BridgeResponse> {
  const token = resolveToken(options.token);
  if (!token.value) return rejected("token_missing", "token not found");
  const headers: Record<string, string> = { Authorization: `Bearer ${token.value}` };
  if (request.body !== undefined) headers["Content-Type"] = "application/json";
  return requestJson(path, request, headers, options);
}

async function publicRequest(path: string, options: BridgeOptions): Promise<BridgeResponse> {
  return requestJson(path, { method: "GET" }, {}, options);
}

async function requestJson(path: string, request: RequestOptions, headers: Record<string, string>, options: BridgeOptions): Promise<BridgeResponse> {
  const url = resolveUrl(options.url).value!;
  const fetchImpl = options.fetchImpl ?? fetch;
  let response: Response;
  try {
    response = await fetchImpl(`${url}${path}`, {
      method: request.method,
      headers,
      body: request.body === undefined ? undefined : JSON.stringify(request.body)
    });
  } catch {
    return rejected("desktop_not_running", "desktop app is not reachable");
  }

  const body = await readJson(response);
  if (!response.ok || body?.ok === false) {
    return rejected(stringOrUndefined(body?.reasonCode) || statusReasonCode(response.status), safeReason(body?.reason));
  }
  return { ok: true, body };
}

async function readJson(response: Response): Promise<any> {
  try {
    return await response.json();
  } catch {
    return undefined;
  }
}

function parseObject(value: unknown): ParsedObject {
  if (isRecord(value)) return { ok: true, value };
  return rejected("schema_invalid", "tool parameters must be an object");
}

function sanitizeInstances(instances: unknown[]) {
  return instances.filter(isRecord).map((instance) => ({
    instanceId: stringOrUndefined(instance.instanceId),
    sourceKind: stringOrUndefined(instance.sourceKind),
    sourceId: stringOrUndefined(instance.sourceId),
    displayName: stringOrUndefined(instance.displayName),
    windowLabel: stringOrUndefined(instance.windowLabel),
    visible: typeof instance.visible === "boolean" ? instance.visible : undefined,
    currentState: stringOrUndefined(instance.currentState),
    catProfileId: stringOrUndefined(instance.catProfileId),
    lastEventAt: stringOrUndefined(instance.lastEventAt),
    isDefault: typeof instance.isDefault === "boolean" ? instance.isDefault : undefined
  }));
}

function sanitizeLimits(value: unknown) {
  if (!isRecord(value)) return undefined;
  return {
    totalCount: numberOrUndefined(value.totalCount),
    softLimit: numberOrUndefined(value.softLimit),
    hardLimit: numberOrUndefined(value.hardLimit),
    overSoftLimit: typeof value.overSoftLimit === "boolean" ? value.overSoftLimit : undefined,
    atHardLimit: typeof value.atHardLimit === "boolean" ? value.atHardLimit : undefined
  };
}

function rejected(reasonCode: string, reason: string): { ok: false; reasonCode: string; reason: string } {
  return { ok: false, reasonCode, reason };
}

function safeReason(value: unknown) {
  return typeof value === "string" ? value : "request failed";
}

function statusReasonCode(status: number) {
  if (status === 401) return "unauthorized";
  if (status === 429) return "rate_limited";
  if (status === 503) return "bridge_unavailable";
  if (status === 400) return "schema_invalid";
  if (status === 404) return "instance_not_found";
  return "unknown_error";
}

function hasVia(value: unknown) {
  return typeof value === "object" && value !== null && "via" in value;
}

function optionalString(value: unknown) {
  return typeof value === "string" && value.trim() ? value : undefined;
}

function stringOrUndefined(value: unknown) {
  return typeof value === "string" ? value : undefined;
}

function numberOrUndefined(value: unknown) {
  return typeof value === "number" ? value : undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isValidInstanceId(value: string) {
  return /^[A-Za-z0-9._-]{1,64}$/.test(value) && !value.includes("..");
}
