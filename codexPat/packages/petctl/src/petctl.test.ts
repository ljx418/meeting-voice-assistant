import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { parseArgs, buildEventFromOptions } from "./args.js";
import { notify } from "./notify.js";

describe("petctl args", () => {
  it("builds a valid default notify event", () => {
    const args = parseArgs(["notify", "--level", "success"]);
    const event = buildEventFromOptions(args.payloadOptions);
    assert.equal(event.source.id, "custom.local");
    assert.equal(event.source.kind, "custom");
    assert.equal(event.source.name, "petctl");
    assert.equal(event.level, "success");
    assert.equal(event.sound, "none");
  });

  it("rejects json mode combined with payload options", () => {
    assert.throws(() => parseArgs(["notify", "--json", "--level", "success"]), /--json cannot be combined/);
  });

  it("supports metadata key value pairs", () => {
    const args = parseArgs(["notify", "--level", "running", "--metadata", "task=build"]);
    const event = buildEventFromOptions(args.payloadOptions);
    assert.deepEqual(event.metadata, { task: "build" });
  });
});

describe("petctl notify", () => {
  it("does not send http when local validation fails", async () => {
    let called = false;
    const result = await notify({
      event: {
        source: { id: "custom.local", kind: "custom" },
        level: "nope"
      },
      token: "secret",
      fetchImpl: async () => {
        called = true;
        throw new Error("should not be called");
      }
    });
    assert.equal(result.exitCode, 3);
    assert.equal(called, false);
  });

  it("maps accepted bridge response", async () => {
    const result = await notify({
      event: {
        source: { id: "custom.local", kind: "custom" },
        level: "success"
      },
      token: "secret",
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        accepted: true,
        eventId: "evt_test",
        queued: true
      }), { status: 202 })
    });
    assert.equal(result.exitCode, 0);
    assert.equal(result.eventId, "evt_test");
  });

  it("maps unauthorized response", async () => {
    const result = await notify({
      event: {
        source: { id: "custom.local", kind: "custom" },
        level: "success"
      },
      token: "secret",
      fetchImpl: async () => new Response(JSON.stringify({
        ok: false,
        accepted: false,
        reasonCode: "auth_invalid",
        reason: "bad token"
      }), { status: 401 })
    });
    assert.equal(result.exitCode, 5);
    assert.equal(result.reasonCode, "auth_invalid");
  });
});
