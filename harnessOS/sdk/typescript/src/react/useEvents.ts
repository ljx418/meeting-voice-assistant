import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { fetchStreamRequest } from "../events.js";
import type { EventSubscription } from "../models.js";
import type { EventHookStatus, EventSourceFactory, EventSourceLike, HookEventRecord, UseEventsOptions } from "./types.js";

export interface UseEventsResult {
  status: EventHookStatus;
  events: HookEventRecord[];
  error?: unknown;
  subscription?: EventSubscription;
  connect(): Promise<EventSubscription>;
  close(): void;
  reconnect(): Promise<EventSubscription>;
}

export function useEvents(options: UseEventsOptions): UseEventsResult {
  const [status, setStatus] = useState<EventHookStatus>("idle");
  const [events, setEvents] = useState<HookEventRecord[]>([]);
  const [error, setError] = useState<unknown>();
  const [subscription, setSubscription] = useState<EventSubscription>();
  const subscriptionRef = useRef<EventSubscription | undefined>();
  const sourceRef = useRef<EventSourceLike | null>(null);
  const connectingRef = useRef<Promise<EventSubscription> | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cursorRef = useRef<string | undefined>();
  const seenRef = useRef<Set<string>>(new Set());

  const dedupe = options.dedupe !== false;
  const reconnectEnabled = options.reconnect !== false;
  const reconnectDelayMs = options.reconnectDelayMs ?? 250;

  const close = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
    connectingRef.current = null;
  }, []);

  const connect = useCallback(async () => {
    if (sourceRef.current && subscriptionRef.current) return subscriptionRef.current;
    if (connectingRef.current) return connectingRef.current;
    setStatus("loading");
    setError(undefined);
    const promise = options.client
      .eventsSubscribe({
        channels: options.channels,
        mode: options.mode,
        scope: options.scope,
      })
      .then((descriptor) => {
        subscriptionRef.current = descriptor;
        setSubscription(descriptor);
        cursorRef.current = cursorRef.current || descriptor.replayCursor;
        if (options.mode === "fetch") {
          fetchStreamRequest(descriptor, options.capabilityToken);
          setStatus("streaming");
          return descriptor;
        }
        const source = createEventSource(eventSourceUrlWithCursor(descriptor.nativeEventSourceUrl(), cursorRef.current), options.eventSourceFactory);
        sourceRef.current = source;
        source.onopen = () => setStatus("streaming");
        source.onmessage = (event) => {
          const parsed = parseEvent(event);
          const key = eventKey(parsed, event.lastEventId);
          cursorRef.current = event.lastEventId || parsed.cursor || cursorRef.current;
          if (dedupe && key && seenRef.current.has(key)) return;
          if (key) seenRef.current.add(key);
          setEvents((current) => [...current, parsed]);
        };
        source.onerror = (event) => {
          setError(event);
          source.close();
          sourceRef.current = null;
          if (reconnectEnabled) {
            setStatus("reconnecting");
            reconnectTimerRef.current = setTimeout(() => {
              connectingRef.current = null;
              void connect();
            }, reconnectDelayMs);
          } else {
            setStatus("error");
          }
        };
        return descriptor;
      })
      .catch((caught) => {
        setError(caught);
        setStatus("error");
        throw caught;
      })
      .finally(() => {
        connectingRef.current = null;
      });
    connectingRef.current = promise;
    return promise;
  }, [
    dedupe,
    options.capabilityToken,
    options.channels,
    options.client,
    options.eventSourceFactory,
    options.mode,
    options.scope,
    reconnectDelayMs,
    reconnectEnabled,
  ]);

  const reconnect = useCallback(async () => {
    close();
    setStatus("reconnecting");
    return connect();
  }, [close, connect]);

  useEffect(() => {
    if (!options.enabled) return undefined;
    void connect();
    return undefined;
  }, [connect, options.enabled]);

  useEffect(() => close, [close]);

  return useMemo(() => ({ status, events, error, subscription, connect, close, reconnect }), [close, connect, error, events, reconnect, status, subscription]);
}

function createEventSource(url: string, factory?: EventSourceFactory): EventSourceLike {
  if (factory) return factory(url);
  if (typeof EventSource === "undefined") {
    throw new Error("EventSource is not available; provide eventSourceFactory or use fetch mode");
  }
  return new EventSource(url) as EventSourceLike;
}

function parseEvent(event: MessageEvent<string>): HookEventRecord {
  try {
    const parsed = JSON.parse(event.data) as HookEventRecord;
    return parsed;
  } catch {
    return { data: event.data };
  }
}

function eventKey(event: HookEventRecord, lastEventId?: string): string | undefined {
  return String(event.event_id || event.id || lastEventId || event.cursor || "");
}

function eventSourceUrlWithCursor(rawUrl: string, cursor?: string): string {
  if (!cursor) return rawUrl;
  const url = new URL(rawUrl);
  url.searchParams.set("cursor", cursor);
  return url.toString();
}
