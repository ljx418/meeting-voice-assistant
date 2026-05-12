import assert from "node:assert/strict";
import { test } from "node:test";

import {
  ApprovalConflictError,
  AuthRequiredError,
  CapabilityToken,
  EventSubscription,
  HarnessOSClient,
  MethodForbiddenError,
  Scope,
  ScopeMismatchError,
  TransportError,
  fetchStreamRequest,
  nativeEventSourceUrl,
} from "../dist/index.js";

const FORBIDDEN_EXPORTS = [
  "MeetingClient",
  "KnowledgeClient",
  "generateMinutes",
  "ingestDocument",
  "runMeetingWorkflow",
  "generateVideo",
  "analyzePortfolio",
  "processRecording",
  "searchKnowledgeBase",
];

class MockTransport {
  constructor(responses) {
    this.responses = [...responses];
    this.requests = [];
  }

  async request(payload, options) {
    this.requests.push({ payload, options });
    return this.responses.shift() ?? { id: "ok", result: { ok: true } };
  }
}

test("public API surface excludes business wrappers", async () => {
  const api = await import("../dist/index.js");
  for (const name of FORBIDDEN_EXPORTS) {
    assert.equal(Object.hasOwn(api, name), false, name);
  }
  assert.equal(typeof api.HarnessOSClient, "function");
  assert.equal(typeof api.Scope, "function");
  assert.equal(typeof api.RpcError, "function");
  assert.equal(typeof api.EventSubscription, "function");
});

test("rpc injects scope and bearer token", async () => {
  const transport = new MockTransport([{ id: "1", result: { session_id: "sess_1" } }]);
  const client = new HarnessOSClient({
    baseUrl: "http://localhost:8000",
    capabilityToken: new CapabilityToken("cap-secret-token"),
    scope: new Scope({ app_id: "reference_app", project_id: "demo", workspace_id: "local" }),
    transport,
  });

  const result = await client.sessionStart({ model: "demo" });
  assert.equal(result.session_id, "sess_1");
  assert.equal(transport.requests[0].payload.method, "session.start");
  assert.deepEqual(transport.requests[0].payload.params.scope, {
    app_id: "reference_app",
    project_id: "demo",
    workspace_id: "local",
  });
  assert.equal(transport.requests[0].options.headers.Authorization, "Bearer cap-secret-token");
  assert.equal(client.toString().includes("cap-secret-token"), false);
});

test("low-level rpc rejects forbidden and unknown methods", async () => {
  const client = new HarnessOSClient({ baseUrl: "http://localhost:8000", transport: new MockTransport([]) });
  for (const method of [
    "meeting.process_recording",
    "knowledge.search",
    "approval.approve",
    "approval.reject",
    "pack.execute_stub",
    "workflow.execute_stub",
    "method.list",
    "unknown.method",
  ]) {
    await assert.rejects(() => client.rpc(method, { include_forbidden: true }), MethodForbiddenError);
  }
});

test("scope override conflict is rejected locally", async () => {
  const client = new HarnessOSClient({
    baseUrl: "http://localhost:8000",
    scope: new Scope({ app_id: "reference_app" }),
    transport: new MockTransport([{ id: "1", result: { session_id: "sess_1" } }]),
  });
  await client.sessionStart({ scope: { app_id: "reference_app" } });
  assert.throws(() => client.sessionStart({ scope: { app_id: "other_app" } }), ScopeMismatchError);
});

test("JSON-RPC response validation and typed error mapping", async () => {
  await assert.rejects(
    () =>
      new HarnessOSClient({
        baseUrl: "http://localhost:8000",
        transport: new MockTransport([{ result: {}, error: { code: "INVALID_PARAMS" } }]),
      }).sessionStart(),
    TransportError,
  );
  await assert.rejects(
    () =>
      new HarnessOSClient({
        baseUrl: "http://localhost:8000",
        transport: new MockTransport([{ id: "x" }]),
      }).sessionStart(),
    TransportError,
  );
  await assert.rejects(
    () =>
      new HarnessOSClient({
        baseUrl: "http://localhost:8000",
        transport: new MockTransport([{ error: { code: "AUTH_REQUIRED", message: "missing bearer secret-token", data: { token: "abc" } } }]),
      }).sessionStart(),
    AuthRequiredError,
  );
  await assert.rejects(
    () =>
      new HarnessOSClient({
        baseUrl: "http://localhost:8000",
        transport: new MockTransport([{ error: { code: "APPROVAL_CONFLICT", message: "Bearer cap-secret-token" } }]),
      }).approvalRespond({ approvalId: "appr_1", decision: "reject" }),
    ApprovalConflictError,
  );
});

test("eventsSubscribe maps descriptor and redacts subscription token", async () => {
  const transport = new MockTransport([
    {
      id: "1",
      result: {
        subscription_id: "sub_1",
        transport: "eventsource",
        eventsource_url: "/v1/events/subscribe?subscription_token=sub-secret&channels=chat",
        subscription_token: "sub-secret",
        replay_cursor: "cursor_1",
        expires_at: "2026-05-12T00:00:00+00:00",
        allowed_channels: ["chat"],
      },
    },
  ]);
  const client = new HarnessOSClient({ baseUrl: "http://localhost:8000", capabilityToken: "cap-secret-token", transport });
  const subscription = await client.eventsSubscribe({ channels: ["chat"] });
  assert.equal(subscription.eventsourceUrl.startsWith("http://localhost:8000/v1/events/subscribe"), true);
  assert.deepEqual(subscription.allowedChannels, ["chat"]);
  assert.equal(subscription.toString().includes("sub-secret"), false);
  assert.equal(JSON.stringify(subscription).includes("sub-secret"), false);
  assert.equal(nativeEventSourceUrl(subscription).includes("subscription_token="), true);
});

test("absolute EventSource URL is preserved", () => {
  const subscription = EventSubscription.fromResult(
    {
      subscription_id: "sub_abs",
      eventsource_url: "https://example.test/events?subscription_token=sub-secret",
      subscription_token: "sub-secret",
      replay_cursor: "cursor_abs",
    },
    "http://localhost:8000",
  );
  assert.equal(subscription.eventsourceUrl, "https://example.test/events?subscription_token=sub-secret");
});

test("native EventSource helper has no Authorization header while fetch stream may use bearer", async () => {
  const subscription = EventSubscription.fromResult(
    {
      subscription_id: "sub_1",
      eventsource_url: "/v1/events/subscribe?subscription_token=sub-secret",
      subscription_token: "sub-secret",
      replay_cursor: "cursor_1",
    },
    "http://localhost:8000",
  );
  assert.equal(typeof nativeEventSourceUrl(subscription), "string");
  const fetchRequest = fetchStreamRequest(subscription, "cap-secret-token");
  assert.equal(fetchRequest.headers.Authorization, "Bearer cap-secret-token");
});

test("integration smoke wrappers use default methods", async () => {
  const transport = new MockTransport([
    { result: { session_id: "sess_1" } },
    { result: { session_id: "sess_1", turn_id: "turn_1" } },
    {
      result: {
        subscription_id: "sub_1",
        eventsource_url: "/v1/events/subscribe?subscription_token=sub-secret",
        subscription_token: "sub-secret",
        replay_cursor: "cursor_1",
        allowed_channels: ["chat"],
      },
    },
    { result: { artifacts: [], count: 0 } },
    { result: { jobs: [], count: 0 } },
    { result: { approval: { approval_id: "appr_1" }, status: "approved", idempotent: false } },
    { result: { connector: { connector_id: "remote_comfyui" }, health: { status: "blocked" } } },
    { result: { packs: [], count: 0 } },
  ]);
  const client = new HarnessOSClient({ baseUrl: "http://localhost:8000", transport });
  await client.sessionStart();
  await client.turnStart({ input: "hello" });
  await client.eventsSubscribe({ channels: ["chat"] });
  await client.artifactList();
  await client.jobList();
  await client.approvalRespond({ approvalId: "appr_1", decision: "approve" });
  await client.connectorHealth({ connectorId: "remote_comfyui" });
  await client.packList();
  assert.deepEqual(
    transport.requests.map((request) => request.payload.method),
    [
      "session.start",
      "turn.start",
      "events.subscribe",
      "artifact.list",
      "job.list",
      "approval.respond",
      "connector.health",
      "pack.list",
    ],
  );
});
