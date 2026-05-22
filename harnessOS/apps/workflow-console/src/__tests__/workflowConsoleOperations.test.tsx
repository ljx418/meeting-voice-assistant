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
    await client.proposePatch("wf_1", {
      source: "inspector",
      intent_type: "inspector_update",
      operation: "update_station_prompt",
      workflow_instance_id: "wfi_1",
      payload: { station_id: "station_b", prompt_patch: "优化分镜" },
    });
    await client.applyPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.rejectPatch("wf_1", "wfp_1", { workflow_instance_id: "wfi_1", user_confirmed: true, source: "editing_panel" });
    await client.publishWorkflow("wf_1", { version: "2.0.0", expected_draft_revision: 3, user_confirmed: true, source: "editing_panel" });
  } finally {
    globalThis.fetch = originalFetch;
  }
  assert.equal(calls.length, 8);
  assert(calls.slice(0, 4).every((call) => call.url.startsWith("/bff/instances/wfi_1/")));
  assert.equal(calls[4].url, "/bff/workflows/wf_1/patches");
  assert.equal(calls[5].url, "/bff/workflows/wf_1/patches/wfp_1/apply");
  assert.equal(calls[6].url, "/bff/workflows/wf_1/patches/wfp_1/reject");
  assert.equal(calls[7].url, "/bff/workflows/wf_1/publish");
  assert(calls.some((call) => call.body?.includes('"user_confirmed":true')));
  for (const call of calls) {
    assert(!call.url.includes("/v1/rpc"));
    assert(!call.url.includes("/v1/events/subscribe"));
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
