import { ScopeMismatchError } from "./errors.js";

export interface ScopeValue {
  app_id?: string;
  project_id?: string | null;
  workspace_id?: string | null;
}

export class Scope {
  readonly appId: string;
  readonly projectId?: string;
  readonly workspaceId?: string;

  constructor(value: ScopeValue = {}) {
    this.appId = value.app_id || "default";
    this.projectId = optionalText(value.project_id);
    this.workspaceId = optionalText(value.workspace_id);
  }

  static from(value?: Scope | ScopeValue | null): Scope | undefined {
    if (value == null) return undefined;
    return value instanceof Scope ? value : new Scope(value);
  }

  toJSON(): ScopeValue {
    return {
      app_id: this.appId,
      project_id: this.projectId ?? null,
      workspace_id: this.workspaceId ?? null,
    };
  }

  ensureCompatible(override: Scope): void {
    const checks: Array<[string, string | undefined, string | undefined]> = [
      ["app_id", this.appId, override.appId],
      ["project_id", this.projectId, override.projectId],
      ["workspace_id", this.workspaceId, override.workspaceId],
    ];
    for (const [field, current, requested] of checks) {
      if (current != null && requested != null && current !== requested) {
        throw new ScopeMismatchError("SCOPE_MISMATCH", `scope override conflicts with default scope: ${field}`, { field });
      }
    }
  }

  toString(): string {
    return `Scope(app_id=${this.appId}, project_id=${this.projectId ?? "null"}, workspace_id=${this.workspaceId ?? "null"})`;
  }
}

export class CapabilityToken {
  readonly value: string;

  constructor(value: string) {
    this.value = value;
  }

  toString(): string {
    return "CapabilityToken(value=[REDACTED])";
  }

  toJSON(): string {
    return "[REDACTED]";
  }
}

export interface EventSubscriptionResult {
  subscription_id?: string;
  transport?: string;
  eventsource_url?: string;
  subscription_token?: string;
  replay_cursor?: string;
  expires_at?: string | null;
  allowed_channels?: string[];
}

export class EventSubscription {
  readonly subscriptionId: string;
  readonly transport: string;
  readonly eventsourceUrl: string;
  readonly subscriptionToken: string;
  readonly replayCursor: string;
  readonly expiresAt?: string;
  readonly allowedChannels: string[];

  constructor(value: {
    subscriptionId: string;
    transport: string;
    eventsourceUrl: string;
    subscriptionToken: string;
    replayCursor: string;
    expiresAt?: string;
    allowedChannels?: string[];
  }) {
    this.subscriptionId = value.subscriptionId;
    this.transport = value.transport;
    this.eventsourceUrl = value.eventsourceUrl;
    this.subscriptionToken = value.subscriptionToken;
    this.replayCursor = value.replayCursor;
    this.expiresAt = value.expiresAt;
    this.allowedChannels = value.allowedChannels || [];
  }

  static fromResult(result: EventSubscriptionResult, baseUrl: string): EventSubscription {
    return new EventSubscription({
      subscriptionId: String(result.subscription_id || ""),
      transport: String(result.transport || "eventsource"),
      eventsourceUrl: absoluteUrl(baseUrl, String(result.eventsource_url || "")),
      subscriptionToken: String(result.subscription_token || ""),
      replayCursor: String(result.replay_cursor || ""),
      expiresAt: optionalText(result.expires_at),
      allowedChannels: (result.allowed_channels || []).map(String),
    });
  }

  nativeEventSourceUrl(): string {
    return this.eventsourceUrl;
  }

  toString(): string {
    return `EventSubscription(subscriptionId=${this.subscriptionId}, transport=${this.transport}, eventsourceUrl=${redactedUrl(this.eventsourceUrl)}, subscriptionToken=[REDACTED], replayCursor=${this.replayCursor})`;
  }

  toJSON(): Record<string, unknown> {
    return {
      subscriptionId: this.subscriptionId,
      transport: this.transport,
      eventsourceUrl: redactedUrl(this.eventsourceUrl),
      subscriptionToken: "[REDACTED]",
      replayCursor: this.replayCursor,
      expiresAt: this.expiresAt,
      allowedChannels: this.allowedChannels,
    };
  }
}

function absoluteUrl(baseUrl: string, rawUrl: string): string {
  try {
    return new URL(rawUrl).toString();
  } catch {
    return new URL(rawUrl.replace(/^\//, ""), `${baseUrl.replace(/\/$/, "")}/`).toString();
  }
}

function redactedUrl(rawUrl: string): string {
  const url = new URL(rawUrl);
  const keys: string[] = [];
  url.searchParams.forEach((_value, key) => keys.push(key));
  for (const key of keys) {
    if (key.toLowerCase().includes("token")) {
      url.searchParams.set(key, "[REDACTED]");
    }
  }
  return url.toString();
}

function optionalText(value: unknown): string | undefined {
  if (value == null) return undefined;
  const text = String(value).trim();
  return text || undefined;
}
