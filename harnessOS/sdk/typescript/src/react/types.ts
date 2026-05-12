import type { HarnessOSClient } from "../client.js";
import type { Scope, ScopeValue } from "../models.js";

export type ActionStatus = "idle" | "loading" | "success" | "error";
export type EventHookStatus = "idle" | "loading" | "streaming" | "reconnecting" | "error";

export interface HookClientOptions {
  client: HarnessOSClient;
  scope?: Scope | ScopeValue;
}

export interface HookActionState<T> {
  status: ActionStatus;
  data?: T;
  error?: unknown;
}

export interface HookEventRecord {
  id?: string;
  type?: string;
  channel?: string;
  cursor?: string;
  data?: unknown;
  [key: string]: unknown;
}

export interface EventSourceLike {
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent<string>) => void) | null;
  onerror: ((event: Event) => void) | null;
  close(): void;
}

export type EventSourceFactory = (url: string) => EventSourceLike;

export interface UseEventsOptions extends HookClientOptions {
  channels?: string[];
  enabled?: boolean;
  mode?: "native" | "fetch";
  capabilityToken?: string;
  eventSourceFactory?: EventSourceFactory;
  reconnect?: boolean;
  reconnectDelayMs?: number;
  dedupe?: boolean;
}
