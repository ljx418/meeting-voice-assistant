export async function bffJson(path: string, init: RequestInit = {}): Promise<unknown> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init.headers || {}),
    },
  });
  if (!response.ok) {
    throw new Error(`BFF request failed: ${response.status}`);
  }
  return response.json();
}

export function connectBffEvents(channels: string[], onMessage: (event: MessageEvent) => void): EventSource {
  const source = new EventSource(`/bff/events/subscribe?channels=${encodeURIComponent(channels.join(","))}`);
  source.onmessage = onMessage;
  return source;
}

export async function startSession(): Promise<unknown> {
  return bffJson("/bff/sessions", { method: "POST", body: JSON.stringify({ model: "reference" }) });
}

export async function startTurn(sessionId: string, input: string): Promise<unknown> {
  return bffJson("/bff/turns", { method: "POST", body: JSON.stringify({ session_id: sessionId, input }) });
}

export async function respondApproval(approvalId: string, decision: "approve" | "reject"): Promise<unknown> {
  return bffJson(`/bff/approvals/${approvalId}/respond`, {
    method: "POST",
    body: JSON.stringify({ decision }),
  });
}

export async function loadEmbedBootstrap(): Promise<unknown> {
  return bffJson("/bff/embed/bootstrap?channels=chat,job,artifact,approval");
}

