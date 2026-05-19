import assert from "node:assert/strict";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

test("operation client uses structured BFF routes only", async () => {
  const calls: Array<{ url: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ url: String(input), body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ operation: "ok", status: "ok", resource: {} }), { status: 200 });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.respondApproval("wfi_1", "appr_1", { decision: "approve", user_confirmed: true, source: "approval_panel" });
    await client.updateContext("wfi_1", { op: "set", path: "business.note", value: "ok", expected_revision: 1 });
    await client.emitBusinessEvent("wfi_1", { event_type: "business.workflow.note_submitted", payload: { note: "ok" } });
    await client.listInstanceStationOutputs("wfi_1", "sr_1");
    await client.proposePatch("wf_1", { operation: "update_station_prompt" });
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls.length, 5);
  assert(calls.slice(0, 4).every((call) => call.url.startsWith("/bff/instances/wfi_1/")));
  assert.equal(calls[4].url, "/bff/workflows/wf_1/patches/propose");
  assert(calls.some((call) => call.body?.includes('"user_confirmed":true')));
  for (const call of calls) {
    assert(!call.url.includes("/v1/rpc"));
    assert(!call.url.includes("/v1/events/subscribe"));
    assert(!call.body?.includes("workflow.patch.apply"));
  }
});

test("event bridge client follows the BFF stream", () => {
  const originalEventSource = globalThis.EventSource;
  const urls: string[] = [];
  class FakeEventSource {
    onmessage: ((message: MessageEvent) => void) | null = null;
    constructor(url: string) {
      urls.push(url);
    }
    close() {}
  }
  globalThis.EventSource = FakeEventSource as unknown as typeof EventSource;
  try {
    const client = new WorkflowConsoleClient("/bff");
    const source = client.connectEvents(["approval", "workflow_patch"], () => undefined);
    source.close();
  } finally {
    globalThis.EventSource = originalEventSource;
  }
  assert.equal(urls.length, 1);
  assert(urls[0].startsWith("/bff/events/subscribe?"));
  assert(urls[0].includes("channels=approval%2Cworkflow_patch"));
  assert(urls[0].includes("follow=true"));
});
