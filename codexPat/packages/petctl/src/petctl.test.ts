import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { parseArgs, buildEventFromOptions } from "./args.js";
import { attachCodex, detachInstance, listInstances } from "./instances.js";
import { notify } from "./notify.js";

describe("petctl args", () => {
  it("builds a valid default notify event", () => {
    const args = parseArgs(["notify", "--level", "success"]);
    assert.equal(args.command, "notify");
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
    assert.equal(args.command, "notify");
    const event = buildEventFromOptions(args.payloadOptions);
    assert.deepEqual(event.metadata, { task: "build" });
  });

  it("parses notify instance routing option", () => {
    const args = parseArgs(["notify", "--instance", "codex_123", "--level", "success"]);
    assert.equal(args.command, "notify");
    assert.equal(args.instance, "codex_123");
  });

  it("parses attach codex", () => {
    const args = parseArgs(["attach", "codex", "--name", "Codex A", "--json", "--print-env"]);
    assert.equal(args.command, "attach");
    assert.equal(args.target, "codex");
    assert.equal(args.name, "Codex A");
    assert.equal(args.json, true);
    assert.equal(args.printEnv, true);
  });

  it("parses list", () => {
    const args = parseArgs(["list", "--json"]);
    assert.equal(args.command, "list");
    assert.equal(args.json, true);
  });

  it("parses detach", () => {
    const args = parseArgs(["detach", "--instance", "codex_123", "--json"]);
    assert.equal(args.command, "detach");
    assert.equal(args.instance, "codex_123");
    assert.equal(args.json, true);
  });

  it("requires detach instance", () => {
    assert.throws(() => parseArgs(["detach"]), /requires --instance/);
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

  it("posts to instance endpoint when instance is set", async () => {
    let calledUrl = "";
    const result = await notify({
      event: {
        source: { id: "custom.local", kind: "custom" },
        level: "success"
      },
      token: "secret",
      instance: "codex_123",
      fetchImpl: async (input) => {
        calledUrl = String(input);
        return new Response(JSON.stringify({
          ok: true,
          accepted: true,
          eventId: "evt_instance",
          queued: true
        }), { status: 202 });
      }
    });
    assert.equal(result.exitCode, 0);
    assert.equal(calledUrl, "http://127.0.0.1:17321/api/instances/codex_123/events");
  });

  it("rejects invalid instance locally", async () => {
    let called = false;
    const result = await notify({
      event: {
        source: { id: "custom.local", kind: "custom" },
        level: "success"
      },
      token: "secret",
      instance: "../../bad",
      fetchImpl: async () => {
        called = true;
        throw new Error("should not be called");
      }
    });
    assert.equal(result.exitCode, 3);
    assert.equal(result.reasonCode, "instance_id_invalid");
    assert.equal(called, false);
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

describe("petctl attach/list", () => {
  it("attaches a codex instance", async () => {
    const result = await attachCodex({
      token: "secret",
      name: "Codex A",
      fetchImpl: async (_input, init) => {
        const payload = JSON.parse(String(init?.body));
        assert.equal(payload.sourceKind, "codex");
        assert.equal(payload.sourceId, "codex.local");
        assert.equal(payload.displayName, "Codex A");
        return new Response(JSON.stringify({
          ok: true,
          created: true,
          instanceId: "codex_123",
          displayName: "Codex A",
          windowLabel: "pet-codex_123",
          export: "export AGENT_DESKTOP_PET_INSTANCE_ID=codex_123"
        }), { status: 200 });
      }
    });
    assert.equal(result.exitCode, 0);
    assert.equal(result.instanceId, "codex_123");
  });

  it("rejects invalid attach display name locally", async () => {
    const result = await attachCodex({
      token: "secret",
      name: "bad/name"
    });
    assert.equal(result.exitCode, 3);
    assert.equal(result.reasonCode, "display_name_invalid");
  });

  it("lists instances", async () => {
    const result = await listInstances({
      token: "secret",
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        instances: [{ instanceId: "default", displayName: "Agent Desktop Pet", isDefault: true }]
      }), { status: 200 })
    });
    assert.equal(result.exitCode, 0);
    assert.equal(result.instances?.[0]?.instanceId, "default");
  });

  it("detaches an instance", async () => {
    let calledUrl = "";
    const result = await detachInstance({
      token: "secret",
      instance: "codex_123",
      fetchImpl: async (input, init) => {
        calledUrl = String(input);
        assert.equal(init?.method, "DELETE");
        return new Response(JSON.stringify({
          ok: true,
          detached: true,
          instanceId: "codex_123",
          windowLabel: "pet-codex_123"
        }), { status: 200 });
      }
    });
    assert.equal(result.exitCode, 0);
    assert.equal(result.instanceId, "codex_123");
    assert.equal(calledUrl, "http://127.0.0.1:17321/api/instances/codex_123");
  });

  it("rejects invalid detach instance locally", async () => {
    let called = false;
    const result = await detachInstance({
      token: "secret",
      instance: "../../bad",
      fetchImpl: async () => {
        called = true;
        throw new Error("should not be called");
      }
    });
    assert.equal(result.exitCode, 3);
    assert.equal(result.reasonCode, "instance_id_invalid");
    assert.equal(called, false);
  });
});
