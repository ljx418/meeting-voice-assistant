import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { petGetCapabilities, petGetState, petListInstances, petNotify } from "./bridge.js";

describe("pet-mcp bridge", () => {
  it("posts pet_notify to the legacy default event route", async () => {
    let calledUrl = "";
    const result = await petNotify({
      event: {
        source: { id: "mcp.local", kind: "custom", name: "MCP Smoke" },
        level: "success",
        sound: "none"
      }
    }, {
      token: "secret",
      fetchImpl: async (input) => {
        calledUrl = String(input);
        return new Response(JSON.stringify({ ok: true, accepted: true, eventId: "evt_default", queued: true }), { status: 202 });
      }
    });
    assert.equal(result.ok, true);
    assert.equal(result.eventId, "evt_default");
    assert.equal(calledUrl, "http://127.0.0.1:17321/api/events");
  });

  it("posts pet_notify to an instance route", async () => {
    let calledUrl = "";
    const result = await petNotify({
      instanceId: "codex_123",
      event: {
        source: { id: "mcp.local", kind: "custom" },
        level: "running"
      }
    }, {
      token: "secret",
      fetchImpl: async (input) => {
        calledUrl = String(input);
        return new Response(JSON.stringify({ ok: true, accepted: true, eventId: "evt_instance" }), { status: 202 });
      }
    });
    assert.equal(result.ok, true);
    assert.equal(result.instanceId, "codex_123");
    assert.equal(calledUrl, "http://127.0.0.1:17321/api/instances/codex_123/events");
  });

  it("rejects invalid instance ids before HTTP", async () => {
    let called = false;
    const result = await petNotify({
      instanceId: "../../bad",
      event: {
        source: { id: "mcp.local", kind: "custom" },
        level: "success"
      }
    }, {
      token: "secret",
      fetchImpl: async () => {
        called = true;
        throw new Error("should not call");
      }
    });
    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "instance_id_invalid");
    assert.equal(called, false);
  });

  it("rejects payloads that attempt to set via", async () => {
    const result = await petNotify({
      event: {
        source: { id: "mcp.local", kind: "custom" },
        via: "mcp",
        level: "success"
      }
    }, { token: "secret" });
    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "schema_invalid");
  });

  it("lists sanitized instances without paths", async () => {
    const result = await petListInstances(undefined, {
      token: "secret",
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        instances: [{
          instanceId: "default",
          sourceKind: "system",
          sourceId: "system.local",
          displayName: "Default",
          windowLabel: "main",
          workspaceLabel: "/Users/example/secret",
          position: { x: 1, y: 2 },
          currentState: "idle",
          isDefault: true
        }],
        limits: { totalCount: 1, softLimit: 6, hardLimit: 12, overSoftLimit: false, atHardLimit: false }
      }), { status: 200 })
    });
    assert.equal(result.ok, true);
    const text = JSON.stringify(result);
    assert.equal(text.includes("/Users/"), false);
    assert.equal(text.includes("workspaceLabel"), false);
    assert.equal(text.includes("position"), false);
  });

  it("returns state for one instance", async () => {
    const result = await petGetState({ instanceId: "codex_123" }, {
      token: "secret",
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        instances: [
          { instanceId: "default", displayName: "Default", currentState: "idle", isDefault: true },
          { instanceId: "codex_123", displayName: "Codex", currentState: "need_input", isDefault: false }
        ]
      }), { status: 200 })
    });
    assert.equal(result.ok, true);
    assert.equal((result.instance as { currentState?: string }).currentState, "need_input");
  });

  it("reads public capabilities without token", async () => {
    const result = await petGetCapabilities(undefined, {
      fetchImpl: async () => new Response(JSON.stringify({
        levels: ["success"],
        sounds: { playback: true, acceptedIds: ["none"] }
      }), { status: 200 })
    });
    assert.equal(result.ok, true);
    assert.deepEqual((result.capabilities as { levels?: string[] }).levels, ["success"]);
  });
});
