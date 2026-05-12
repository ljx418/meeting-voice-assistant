import assert from "node:assert/strict";
import { test } from "node:test";
import React, { StrictMode } from "react";
import { act, create } from "react-test-renderer";

import {
  useApprovals,
  useArtifacts,
  useEvents,
  useHarnessSession,
  useJobs,
  useTurn,
} from "../dist/react/index.js";

const FORBIDDEN_EXPORTS = [
  "useMeetingMinutes",
  "useKnowledgeSearch",
  "useMeetingWorkflow",
  "useDocumentIngest",
  "useGenerateVideo",
  "useAnalyzePortfolio",
];

class MockClient {
  constructor() {
    this.calls = [];
    this.eventsDescriptor = {
      subscriptionId: "sub_1",
      replayCursor: "cursor_0",
      allowedChannels: ["chat"],
      nativeEventSourceUrl() {
        return "http://localhost:8000/v1/events/subscribe?subscription_token=sub-secret";
      },
      toString() {
        return "EventSubscription(subscriptionToken=[REDACTED])";
      },
      toJSON() {
        return { subscriptionToken: "[REDACTED]", eventsourceUrl: "http://localhost:8000/v1/events/subscribe?subscription_token=[REDACTED]" };
      },
    };
  }

  async sessionStart(params = {}) {
    this.calls.push(["sessionStart", params]);
    return { session_id: "sess_1" };
  }

  async turnStart(params = {}) {
    this.calls.push(["turnStart", params]);
    return { turn_id: "turn_1" };
  }

  async eventsSubscribe(params = {}) {
    this.calls.push(["eventsSubscribe", params]);
    return this.eventsDescriptor;
  }

  async artifactList(params = {}) {
    this.calls.push(["artifactList", params]);
    return { artifacts: [] };
  }

  async artifactReadMetadata(params = {}) {
    this.calls.push(["artifactReadMetadata", params]);
    return { artifact_id: params.artifactId };
  }

  async artifactLineage(params = {}) {
    this.calls.push(["artifactLineage", params]);
    return { roots: [], edges: [] };
  }

  async jobList(params = {}) {
    this.calls.push(["jobList", params]);
    return { jobs: [] };
  }

  async jobGet(params = {}) {
    this.calls.push(["jobGet", params]);
    return { job_id: params.jobId };
  }

  async approvalRespond(params = {}) {
    this.calls.push(["approvalRespond", params]);
    return { status: "approved", idempotent: false };
  }
}

function renderHook(useHook) {
  const holder = { current: undefined };
  function Probe() {
    holder.current = useHook();
    return null;
  }
  let renderer;
  act(() => {
    renderer = create(React.createElement(Probe));
  });
  return { holder, renderer };
}

class MockEventSource {
  constructor(url) {
    this.url = url;
    this.onopen = null;
    this.onmessage = null;
    this.onerror = null;
    this.closed = false;
  }

  close() {
    this.closed = true;
  }

  open() {
    this.onopen?.({});
  }

  message(data, lastEventId = "") {
    this.onmessage?.({ data: JSON.stringify(data), lastEventId });
  }

  fail() {
    this.onerror?.({});
  }
}

test("React public surface excludes business hooks", async () => {
  const api = await import("../dist/react/index.js");
  for (const name of FORBIDDEN_EXPORTS) {
    assert.equal(Object.hasOwn(api, name), false, name);
  }
  assert.equal(typeof api.useHarnessSession, "function");
  assert.equal(typeof api.useTurn, "function");
  assert.equal(typeof api.useEvents, "function");
});

test("useHarnessSession and useTurn do not auto-start", async () => {
  const client = new MockClient();
  const session = renderHook(() => useHarnessSession({ client }));
  assert.equal(session.holder.current.status, "idle");
  assert.deepEqual(client.calls, []);
  await act(async () => {
    await session.holder.current.startSession();
  });
  assert.equal(session.holder.current.status, "success");
  assert.deepEqual(client.calls.map(([name]) => name), ["sessionStart"]);

  const turn = renderHook(() => useTurn({ client }));
  assert.equal(turn.holder.current.status, "idle");
  assert.deepEqual(client.calls.map(([name]) => name), ["sessionStart"]);
  await act(async () => {
    await turn.holder.current.startTurn({ input: "hello" });
  });
  assert.deepEqual(client.calls.map(([name]) => name), ["sessionStart", "turnStart"]);
});

test("useEvents does not auto-connect unless enabled or connect is called", async () => {
  const client = new MockClient();
  const sources = [];
  const hook = renderHook(() =>
    useEvents({
      client,
      channels: ["chat"],
      eventSourceFactory: (url) => {
        const source = new MockEventSource(url);
        sources.push(source);
        return source;
      },
    }),
  );
  assert.equal(hook.holder.current.status, "idle");
  assert.deepEqual(client.calls, []);

  await act(async () => {
    await hook.holder.current.connect();
  });
  assert.equal(sources.length, 1);
  assert.equal(sources[0].url.includes("subscription_token=sub-secret"), true);
  assert.equal(sources[0].url.includes("Authorization"), false);
});

test("useEvents closes on unmount and dedupes events", async () => {
  const client = new MockClient();
  const sources = [];
  const hook = renderHook(() =>
    useEvents({
      client,
      channels: ["chat"],
      eventSourceFactory: (url) => {
        const source = new MockEventSource(url);
        sources.push(source);
        return source;
      },
    }),
  );
  await act(async () => {
    await hook.holder.current.connect();
  });
  act(() => {
    sources[0].message({ event_id: "evt_1", type: "turn.started", channel: "chat" }, "cursor_1");
    sources[0].message({ event_id: "evt_1", type: "turn.started", channel: "chat" }, "cursor_1");
  });
  assert.equal(hook.holder.current.events.length, 1);
  act(() => {
    hook.renderer.unmount();
  });
  assert.equal(sources[0].closed, true);
});

test("useEvents StrictMode enabled mount creates a single live EventSource", async () => {
  const client = new MockClient();
  const sources = [];
  const holder = { current: undefined };
  function Probe() {
    holder.current = useEvents({
      client,
      enabled: true,
      channels: ["chat"],
      eventSourceFactory: (url) => {
        const source = new MockEventSource(url);
        sources.push(source);
        return source;
      },
    });
    return null;
  }

  await act(async () => {
    create(React.createElement(StrictMode, null, React.createElement(Probe)));
  });
  assert.equal(sources.filter((source) => !source.closed).length, 1);
});

test("useEvents reconnect preserves cursor in URL", async () => {
  const client = new MockClient();
  const sources = [];
  const hook = renderHook(() =>
    useEvents({
      client,
      reconnect: false,
      channels: ["chat"],
      eventSourceFactory: (url) => {
        const source = new MockEventSource(url);
        sources.push(source);
        return source;
      },
    }),
  );
  await act(async () => {
    await hook.holder.current.connect();
  });
  act(() => {
    sources[0].message({ event_id: "evt_2", type: "turn.completed", channel: "chat" }, "cursor_2");
  });
  await act(async () => {
    await hook.holder.current.reconnect();
  });
  assert.equal(sources[1].url.includes("cursor=cursor_2"), true);
});

test("useApprovals only calls approval.respond", async () => {
  const client = new MockClient();
  const hook = renderHook(() => useApprovals({ client, pendingApprovals: [{ approval_id: "appr_1" }] }));
  assert.deepEqual(hook.holder.current.pendingApprovals, [{ approval_id: "appr_1" }]);
  await act(async () => {
    await hook.holder.current.respond({ approvalId: "appr_1", decision: "approve" });
  });
  assert.deepEqual(client.calls.map(([name]) => name), ["approvalRespond"]);
});

test("useArtifacts never calls artifact.read inline", async () => {
  const client = new MockClient();
  const hook = renderHook(() => useArtifacts({ client }));
  await act(async () => {
    await hook.holder.current.refresh();
    await hook.holder.current.readMetadata("art_1");
    await hook.holder.current.lineage({ artifactId: "art_1" });
  });
  assert.deepEqual(client.calls.map(([name]) => name), ["artifactList", "artifactReadMetadata", "artifactLineage"]);
});

test("useJobs has no default polling", async () => {
  const client = new MockClient();
  const hook = renderHook(() => useJobs({ client }));
  assert.equal(hook.holder.current.status, "idle");
  assert.deepEqual(client.calls, []);
  await act(async () => {
    await hook.holder.current.refresh();
    await hook.holder.current.get("job_1");
  });
  assert.deepEqual(client.calls.map(([name]) => name), ["jobList", "jobGet"]);
});

test("hook state and serialization redact subscription token", async () => {
  const client = new MockClient();
  const hook = renderHook(() =>
    useEvents({
      client,
      eventSourceFactory: (url) => new MockEventSource(url),
    }),
  );
  await act(async () => {
    await hook.holder.current.connect();
  });
  assert.equal(JSON.stringify(hook.holder.current.subscription).includes("sub-secret"), false);
});
