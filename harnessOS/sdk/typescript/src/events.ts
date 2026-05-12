import type { EventSubscription } from "./models.js";

export function nativeEventSourceUrl(subscription: EventSubscription): string {
  return subscription.nativeEventSourceUrl();
}

export function fetchStreamRequest(
  subscription: EventSubscription,
  capabilityToken?: string,
): { url: string; headers: Record<string, string> } {
  const headers: Record<string, string> = {};
  if (capabilityToken) {
    headers.Authorization = `Bearer ${capabilityToken}`;
  }
  return { url: subscription.eventsourceUrl, headers };
}
