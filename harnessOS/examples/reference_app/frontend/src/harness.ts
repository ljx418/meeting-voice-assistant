import { EventSubscription, type HarnessOSClient, type Scope } from "@harnessos/client";

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

export function createBffStructuredClient(scope: Scope): HarnessOSClient {
  const client = {
    sessionStart: (params: { model?: string } = {}) => startSessionWithModel(params.model),
    turnStart: (params: { sessionId?: string; input: string }) => startTurn(params.sessionId || "", params.input),
    eventsSubscribe: async (params: { channels?: string[] } = {}) =>
      new EventSubscription({
        subscriptionId: "bff_local",
        transport: "eventsource",
        eventsourceUrl: `/bff/events/subscribe?channels=${encodeURIComponent((params.channels || ["chat", "job", "artifact", "approval"]).join(","))}`,
        subscriptionToken: "",
        replayCursor: "",
        allowedChannels: params.channels || ["chat", "job", "artifact", "approval"],
      }),
    artifactList: () => bffJson("/bff/artifacts"),
    artifactReadMetadata: (params: { artifactId: string }) => bffJson(`/bff/artifacts/${params.artifactId}/metadata`),
    artifactLineage: (params: { artifactId?: string } = {}) => bffJson(`/bff/artifacts/lineage${params.artifactId ? `?artifact_id=${encodeURIComponent(params.artifactId)}` : ""}`),
    jobList: () => bffJson("/bff/jobs"),
    jobGet: (params: { jobId: string }) => bffJson(`/bff/jobs/${params.jobId}`),
    approvalRespond: (params: { approvalId: string; decision: "approve" | "reject"; reason?: string }) => respondApproval(params.approvalId, params.decision),
    connectorHealth: (params: { connectorId: string }) => bffJson(`/bff/connectors/${params.connectorId}/health`),
    packList: () => bffJson("/bff/packs"),
    packGet: (params: { packId?: string } = {}) => bffJson(`/bff/packs/${params.packId || "reference_app_pack"}`),
    scope,
  };
  return client as unknown as HarnessOSClient;
}

async function startSessionWithModel(model?: string): Promise<unknown> {
  return bffJson("/bff/sessions", { method: "POST", body: JSON.stringify({ model: model || "reference" }) });
}
