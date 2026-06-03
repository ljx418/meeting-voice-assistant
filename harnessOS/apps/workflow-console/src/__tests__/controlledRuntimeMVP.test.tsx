import assert from "node:assert/strict";
import test from "node:test";
import { WorkflowConsoleClient } from "../api/workflowConsoleClient.js";

test("controlled runtime client uses BFF-only V4.2 routes", async () => {
  const calls: Array<{ path: string; method: string; body?: string }> = [];
  const originalFetch = globalThis.fetch;
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({ path: String(input), method: init?.method || "GET", body: typeof init?.body === "string" ? init.body : undefined });
    return new Response(JSON.stringify({ workflow_instance_id: "wfi_v42", backed_by: "generic_controlled_runtime" }), {
      status: 200,
      headers: { "content-type": "application/json" },
    });
  }) as typeof fetch;
  try {
    const client = new WorkflowConsoleClient("/bff");
    await client.startControlledRuntimeLocalFolderSummary({
      folder_path: "tests/fixtures/desktop/技术分享",
      user_confirmed: true,
      source: "run_panel",
    });
    await client.rerunControlledRuntimeStation("wfi_v42", {
      station_id: "markdown_parse",
      user_confirmed: true,
      source: "run_panel",
    });
    await client.continueControlledRuntimeDownstream("wfi_v42", { user_confirmed: true, source: "run_panel" });
  } finally {
    globalThis.fetch = originalFetch;
  }

  assert.deepEqual(calls.map((call) => call.path), [
    "/bff/v4_2/runtime/workflows/local-folder-summary/start",
    "/bff/v4_2/runtime/instances/wfi_v42/rerun-station",
    "/bff/v4_2/runtime/instances/wfi_v42/continue-downstream",
  ]);
  assert(calls.every((call) => call.method === "POST"));
  assert(calls.every((call) => !call.path.includes("/v1/rpc")));
  assert(calls.every((call) => !call.path.includes("/v1/events/subscribe")));
  assert(calls.every((call) => call.body?.includes('"user_confirmed":true')));
  assert(calls.every((call) => !call.body?.includes('"source":"agent"')));
});
