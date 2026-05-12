const ALLOWED_EVENT_CHANNELS = new Set(["chat", "job", "artifact", "approval", "trace", "business"]);
const DEFAULT_TRACE_POLICY = { enabled: false };
const FORBIDDEN_ACTION_PREFIXES = ["meeting.", "knowledge."];
const FORBIDDEN_ACTIONS = new Set([
  "approval.approve",
  "approval.reject",
  "pack.execute_stub",
  "workflow.execute_stub",
  "method.list",
  "scope_mode=all",
]);

export type CapabilityMode = "bff" | "dev_direct";
export type TransportMode = "bff_proxy" | "direct_eventsource";
export type EmbedInitialView = "chat" | "jobs" | "artifacts" | "approvals";
export type EmbedUiState =
  | "idle"
  | "connecting"
  | "streaming"
  | "approval_required"
  | "auth_required"
  | "subscription_expired"
  | "blocked"
  | "failed"
  | "completed"
  | "reconnecting"
  | "closed";

export interface EmbedScope {
  appId?: string;
  projectId?: string;
  workspaceId?: string;
}

export interface EmbedDefinition {
  schemaVersion: string;
  embedId: string;
  appId: string;
  defaultProjectId?: string;
  defaultWorkspaceId?: string;
  capabilityMode: CapabilityMode;
  transportMode: TransportMode;
  allowedEventChannels: string[];
  allowedActions: string[];
  initialView?: EmbedInitialView;
  artifactPreviewPolicy?: Record<string, unknown>;
  approvalPolicy?: Record<string, unknown>;
  tracePolicy?: Record<string, unknown>;
  theme?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export interface EmbedBootstrap {
  embedDefinition: EmbedDefinition;
  session?: Record<string, unknown>;
  thread?: Record<string, unknown>;
  eventSubscription?: {
    eventsourceUrl: string;
    replayCursor?: string;
    allowedChannels: string[];
    expiresAt?: string;
  };
}

export interface HostBusinessEvent {
  type: `business.${string}`;
  payload: Record<string, unknown>;
  scope?: EmbedScope;
}

export function validateEmbedDefinition(definition: EmbedDefinition): EmbedDefinition {
  requireText(definition.schemaVersion, "schemaVersion");
  requireText(definition.embedId, "embedId");
  requireText(definition.appId, "appId");
  if (!["bff", "dev_direct"].includes(definition.capabilityMode)) {
    throw new Error("EmbedDefinition capabilityMode must be bff or dev_direct");
  }
  if (!["bff_proxy", "direct_eventsource"].includes(definition.transportMode)) {
    throw new Error("EmbedDefinition transportMode must be bff_proxy or direct_eventsource");
  }
  if (definition.capabilityMode === "bff" && definition.transportMode !== "bff_proxy") {
    throw new Error("Production embed default requires bff_proxy transport");
  }
  for (const channel of definition.allowedEventChannels || []) {
    if (!ALLOWED_EVENT_CHANNELS.has(channel)) {
      throw new Error(`EmbedDefinition channel is not allowed: ${channel}`);
    }
  }
  for (const action of definition.allowedActions || []) {
    assertActionAllowed(action);
  }
  const json = JSON.stringify(definition);
  for (const forbidden of ["capabilityToken", "capability_token", "subscription_token", "eventsourceUrl", "eventsource_url", "sessionId", "session_id"]) {
    if (json.includes(forbidden)) {
      throw new Error(`EmbedDefinition must not contain runtime or token field: ${forbidden}`);
    }
  }
  return {
    ...definition,
    tracePolicy: definition.tracePolicy || DEFAULT_TRACE_POLICY,
  };
}

export function sanitizeEmbedBootstrapForLog(bootstrap: EmbedBootstrap): EmbedBootstrap {
  const subscription = bootstrap.eventSubscription
    ? {
        ...bootstrap.eventSubscription,
        eventsourceUrl: redactUrl(bootstrap.eventSubscription.eventsourceUrl),
      }
    : undefined;
  return {
    ...bootstrap,
    eventSubscription: subscription,
  };
}

export function validateHostBusinessEvent(event: HostBusinessEvent): HostBusinessEvent {
  if (!event.type.startsWith("business.") || event.type === "business.") {
    throw new Error("HostBusinessEvent type must use business.* namespace");
  }
  if (event.type === "business.meeting" || event.type === "business.knowledge") {
    throw new Error("HostBusinessEvent must remain platform-neutral in V3.5-H");
  }
  return event;
}

function assertActionAllowed(action: string): void {
  if (FORBIDDEN_ACTIONS.has(action) || action.includes("debug") || action.includes("admin")) {
    throw new Error(`EmbedDefinition action is forbidden: ${action}`);
  }
  if (FORBIDDEN_ACTION_PREFIXES.some((prefix) => action.startsWith(prefix))) {
    throw new Error(`EmbedDefinition action is business-specific: ${action}`);
  }
}

function requireText(value: unknown, field: string): void {
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`EmbedDefinition ${field} is required`);
  }
}

function redactUrl(rawUrl: string): string {
  try {
    const url = new URL(rawUrl, "http://local.invalid");
    const keys: string[] = [];
    url.searchParams.forEach((_value, key) => keys.push(key));
    for (const key of keys) {
      if (key.toLowerCase().includes("token")) {
        url.searchParams.set(key, "[REDACTED]");
      }
    }
    const value = url.toString();
    return rawUrl.startsWith("/") ? `${url.pathname}${url.search}` : value;
  } catch {
    return "[REDACTED_URL]";
  }
}
