import assert from "node:assert/strict";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, it } from "node:test";
import { parseArgs, buildEventFromOptions } from "./args.js";
import { activateAssetPack, generateAssetPromptPack, importAssetPack, listAssetPacks } from "./assets.js";
import { confirmCodexBinding, previewCodexBinding, routeCodexBindingTest } from "./codex-bind.js";
import { runCodexDoctor } from "./codex-doctor.js";
import { getManagedSessionStatus, touchManagedSession } from "./codex-session-status.js";
import { resolveLaunchCommand } from "./codex-launch.js";
import { runCodexProbe } from "./codex-probe.js";
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

  it("parses codex launch wrapper args", () => {
    const args = parseArgs([
      "codex",
      "launch",
      "--name",
      "Codex Window A",
      "--monitor",
      "jsonl",
      "--bin",
      "node",
      "--no-title",
      "--",
      "fake-codex.mjs",
      "--demo"
    ]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "launch");
    assert.equal(args.name, "Codex Window A");
    assert.equal(args.monitor, "jsonl");
    assert.equal(args.bin, "node");
    assert.equal(args.noTitle, true);
    assert.deepEqual(args.passthrough, ["fake-codex.mjs", "--demo"]);
  });

  it("rejects invalid codex launch monitor", () => {
    assert.throws(() => parseArgs(["codex", "launch", "--monitor", "text"]), /--monitor must be none or jsonl/);
  });

  it("parses managed codex exec session args", () => {
    const args = parseArgs([
      "codex",
      "session",
      "start",
      "--mode",
      "exec",
      "--monitor",
      "jsonl",
      "--name",
      "V4.4 Exec Cat",
      "--json",
      "--",
      "codex",
      "exec",
      "--json",
      "redacted"
    ]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "session");
    assert.equal(args.sessionAction, "start");
    assert.equal(args.mode, "exec");
    assert.equal(args.monitor, "jsonl");
    assert.equal(args.name, "V4.4 Exec Cat");
    assert.deepEqual(args.passthrough, ["codex", "exec", "--json", "redacted"]);
  });

  it("parses managed codex tui hooks session args", () => {
    const args = parseArgs([
      "codex",
      "session",
      "start",
      "--mode",
      "tui",
      "--monitor",
      "hooks",
      "--name",
      "V4.4 TUI Cat",
      "--no-title",
      "--",
      "codex"
    ]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "session");
    assert.equal(args.sessionAction, "start");
    assert.equal(args.mode, "tui");
    assert.equal(args.monitor, "hooks");
    assert.equal(args.noTitle, true);
    assert.deepEqual(args.passthrough, ["codex"]);
  });

  it("parses managed codex session status args", () => {
    const args = parseArgs(["codex", "session", "status", "--instance", "codex_1", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "session");
    assert.equal(args.sessionAction, "status");
    assert.equal(args.instance, "codex_1");
    assert.equal(args.json, true);
  });

  it("drops duplicated codex binary token for managed tui launch", () => {
    const command = resolveLaunchCommand({
      bin: "codex",
      monitor: "hooks",
      sessionMode: "tui",
      passthrough: ["codex"],
      noTitle: true
    });
    assert.equal(command.bin, "codex");
    assert.deepEqual(command.args, []);
  });

  it("rejects incompatible managed codex session monitor", () => {
    assert.throws(
      () => parseArgs(["codex", "session", "start", "--mode", "exec", "--monitor", "hooks", "--", "codex"]),
      /--mode exec requires --monitor jsonl/
    );
    assert.throws(
      () => parseArgs(["codex", "session", "start", "--mode", "tui", "--monitor", "jsonl", "--", "codex"]),
      /--mode tui requires --monitor hooks or none/
    );
  });

  it("parses codex doctor args", () => {
    const args = parseArgs(["codex", "doctor", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "doctor");
    assert.equal(args.json, true);
  });

  it("parses codex active window probe args", () => {
    const args = parseArgs(["codex", "probe", "active-window", "--terminal", "terminal", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "probe");
    assert.equal(args.probeTarget, "active-window");
    assert.equal(args.terminal, "terminal");
    assert.equal(args.json, true);
  });

  it("parses codex bind preview args", () => {
    const args = parseArgs(["codex", "bind", "active-window", "--terminal", "terminal", "--preview", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "bind");
    assert.equal(args.bindAction, "active-window");
    assert.equal(args.terminal, "terminal");
    assert.equal(args.preview, true);
    assert.equal(args.json, true);
  });

  it("requires explicit preview for codex bind active-window", () => {
    assert.throws(
      () => parseArgs(["codex", "bind", "active-window", "--terminal", "terminal"]),
      /confirmation_required/
    );
  });

  it("parses codex bind confirm args", () => {
    const args = parseArgs(["codex", "bind", "confirm", "--candidate", "cand_abc", "--name", "V4.2 Cat", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "bind");
    assert.equal(args.bindAction, "confirm");
    assert.equal(args.candidate, "cand_abc");
    assert.equal(args.name, "V4.2 Cat");
    assert.equal(args.json, true);
  });

  it("parses codex route test args", () => {
    const args = parseArgs(["codex", "route", "test", "--binding", "bind_abc", "--level", "running", "--json"]);
    assert.equal(args.command, "codex");
    assert.equal(args.action, "route");
    assert.equal(args.routeAction, "test");
    assert.equal(args.binding, "bind_abc");
    assert.equal(args.level, "running");
    assert.equal(args.json, true);
  });

  it("rejects invalid codex probe terminal", () => {
    assert.throws(
      () => parseArgs(["codex", "probe", "active-window", "--terminal", "warp"]),
      /--terminal must be terminal or iterm2/
    );
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

  it("parses asset prompt pack args", () => {
    const args = parseArgs(["asset", "prompt-pack", "--name", "Mochi", "--description", "orange tabby", "--renderer", "gltf", "--json"]);
    assert.equal(args.command, "asset");
    assert.equal(args.action, "prompt-pack");
    assert.equal(args.name, "Mochi");
    assert.equal(args.renderer, "gltf");
    assert.equal(args.json, true);
  });

  it("parses asset import and activation args", () => {
    const imported = parseArgs(["asset", "import", "--manifest", "manifest.json", "--name", "Mochi", "--json"]);
    assert.equal(imported.command, "asset");
    assert.equal(imported.action, "import");
    assert.equal(imported.manifest, "manifest.json");
    const activated = parseArgs(["asset", "activate", "--pack", "mochi", "--instance", "codex_1", "--json"]);
    assert.equal(activated.command, "asset");
    assert.equal(activated.action, "activate");
    assert.equal(activated.pack, "mochi");
    assert.equal(activated.instance, "codex_1");
  });
});

describe("petctl personalized assets", () => {
  it("generates a sanitized prompt pack for all core actions", () => {
    const result = generateAssetPromptPack({
      name: "Mochi",
      description: "orange tabby with green eyes and fluffy tail",
      renderer: "gltf"
    });
    assert.equal(result.ok, true);
    assert.equal(result.assetPromptPack?.rendererTarget, "gltf");
    for (const action of ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"]) {
      assert.equal(typeof result.assetPromptPack?.prompts[action], "string");
    }
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("/Users/"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("api-token.json"), false);
  });

  it("imports, lists, and activates a valid local gltf asset pack without leaking paths", () => {
    const dir = mkdtempSync(join(tmpdir(), "pet-asset-"));
    try {
      writeFileSync(join(dir, "idle.glb"), "glb");
      writeFileSync(join(dir, "thinking.glb"), "glb");
      writeFileSync(join(dir, "running.glb"), "glb");
      writeFileSync(join(dir, "success.glb"), "glb");
      writeFileSync(join(dir, "warning.glb"), "glb");
      writeFileSync(join(dir, "error.glb"), "glb");
      writeFileSync(join(dir, "need_input.glb"), "glb");
      writeFileSync(join(dir, "sleeping.glb"), "glb");
      const manifest = validImportManifest();
      const manifestPath = join(dir, "manifest.json");
      writeFileSync(manifestPath, JSON.stringify(manifest));
      const storePath = join(dir, "store.json");
      const storageRoot = join(dir, "managed");

      const imported = importAssetPack({
        manifestPath,
        name: "Mochi",
        storePath,
        storageRoot,
        now: new Date("2026-05-28T00:00:00.000Z")
      });
      assert.equal(imported.ok, true);
      assert.equal(imported.assetImport?.packId, "mochi-gltf");
      assert.equal(imported.assetImport?.appManagedStorage, true);

      const listed = listAssetPacks({ storePath });
      assert.equal(listed.ok, true);
      assert.equal(listed.assetPacks?.length, 1);

      const activated = activateAssetPack({ packId: "mochi-gltf", instanceId: "codex_123", storePath });
      assert.equal(activated.ok, true);
      assert.equal(activated.assetActivation?.instanceId, "codex_123");

      const serialized = JSON.stringify({ imported, listed, activated });
      assert.equal(serialized.includes(dir), false);
      assert.equal(serialized.includes("/Users/"), false);
      assert.equal(serialized.includes("Authorization"), false);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("imports a valid local sprite asset pack", () => {
    const dir = mkdtempSync(join(tmpdir(), "pet-asset-sprite-"));
    try {
      for (const action of ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"]) {
        writeFileSync(join(dir, `${action}.png`), "png");
      }
      const manifest = validImportManifest("sprite");
      const manifestPath = join(dir, "manifest.json");
      writeFileSync(manifestPath, JSON.stringify(manifest));
      const storePath = join(dir, "store.json");
      const storageRoot = join(dir, "managed");

      const imported = importAssetPack({
        manifestPath,
        name: "Mochi Sprite",
        storePath,
        storageRoot,
        now: new Date("2026-05-28T00:00:00.000Z")
      });

      assert.equal(imported.ok, true);
      assert.equal(imported.assetImport?.packId, "mochi-sprite");
      assert.equal(imported.assetImport?.rendererKind, "sprite");
      assert.equal(imported.assetImport?.appManagedStorage, true);
      const serialized = JSON.stringify(imported);
      assert.equal(serialized.includes(dir), false);
      assert.equal(serialized.includes("/Users/"), false);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  it("rejects missing core actions and forbidden asset references", () => {
    const dir = mkdtempSync(join(tmpdir(), "pet-asset-bad-"));
    try {
      const storePath = join(dir, "store.json");
      const storageRoot = join(dir, "managed");
      const missingCore = validImportManifest();
      delete missingCore.actions.error;
      const missingPath = join(dir, "missing.json");
      writeFileSync(missingPath, JSON.stringify(missingCore));
      const missing = importAssetPack({ manifestPath: missingPath, storePath, storageRoot });
      assert.equal(missing.ok, false);
      assert.equal(missing.reasonCode, "core_action_missing");

      const forbidden = validImportManifest();
      forbidden.assets.idle.fileName = "../idle.glb";
      const forbiddenPath = join(dir, "forbidden.json");
      writeFileSync(forbiddenPath, JSON.stringify(forbidden));
      const rejected = importAssetPack({ manifestPath: forbiddenPath, storePath, storageRoot });
      assert.equal(rejected.ok, false);
      assert.equal(rejected.reasonCode, "asset_manifest_forbidden_content");
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});

describe("petctl codex bind", () => {
  it("previews a sanitized Terminal.app Codex candidate without creating an instance", async () => {
    const storePath = tempStorePath();
    const result = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: "75164 node ttys013\n",
        psCommTtyByPid: {
          75164: "node ttys013"
        },
        psArgsByPid: {
          75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js /Users/example/workspace"
        },
        codexVersion: "codex-cli 0.131.0\n"
      }) as any
    });

    assert.equal(result.ok, true);
    assert.equal(result.codexBinding?.bindingStatus, "candidate");
    assert.match(result.codexBinding?.candidateId ?? "", /^cand_/);
    assert.equal(result.codexBinding?.terminalBundleId, "com.apple.Terminal");
    assert.equal(result.codexBinding?.processName, "codex");
    assert.equal(result.codexBinding?.petInstanceId, undefined);
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("@openai/codex"), false);
    assert.equal(serialized.includes("/Users/"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("api-token.json"), false);
  });

  it("confirms a valid candidate and only calls the instance creation endpoint", async () => {
    const storePath = tempStorePath();
    const spawnImpl = fakeProbeSpawn({
      osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
      psStdout: "75164 node ttys013\n",
      psCommTtyByPid: {
        75164: "node ttys013"
      },
      psArgsByPid: {
        75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js"
      },
      codexVersion: "codex-cli 0.131.0\n"
    }) as any;
    const preview = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl
    });
    const candidateId = preview.codexBinding?.candidateId;
    assert.ok(candidateId);
    const calledUrls: string[] = [];

    const confirmed = await confirmCodexBinding({
      candidateId,
      name: "V4.2 Cat",
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:01:00.000Z"),
      spawnImpl,
      fetchImpl: async (input, init) => {
        calledUrls.push(String(input));
        assert.equal(init?.method, "POST");
        const payload = JSON.parse(String(init?.body));
        assert.equal(payload.displayName, "V4.2 Cat");
        return new Response(JSON.stringify({
          ok: true,
          created: true,
          instanceId: "codex_v42",
          displayName: "V4.2 Cat",
          windowLabel: "pet-codex_v42"
        }), { status: 200 });
      }
    });

    assert.equal(confirmed.ok, true);
    assert.equal(confirmed.instanceId, "codex_v42");
    assert.equal(confirmed.codexBinding?.petInstanceId, "codex_v42");
    assert.equal(confirmed.codexBinding?.bindingStatus, "active");
    assert.match(confirmed.codexBinding?.bindingId ?? "", /^bind_/);
    assert.deepEqual(calledUrls, ["http://127.0.0.1:17321/api/instances"]);
    const serialized = JSON.stringify(confirmed);
    assert.equal(serialized.includes("secret-token"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("/Users/"), false);
  });

  it("rejects expired candidates", async () => {
    const storePath = tempStorePath();
    const spawnImpl = fakeProbeSpawn({
      osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
      psStdout: "75164 node ttys013\n",
      psCommTtyByPid: {
        75164: "node ttys013"
      },
      psArgsByPid: {
        75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js"
      }
    }) as any;
    const preview = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl
    });

    const confirmed = await confirmCodexBinding({
      candidateId: preview.codexBinding!.candidateId!,
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:06:00.000Z"),
      spawnImpl,
      fetchImpl: async () => {
        throw new Error("should not create instance");
      }
    });

    assert.equal(confirmed.ok, false);
    assert.equal(confirmed.reasonCode, "candidate_expired");
  });

  it("rejects inactive candidates before creating an instance", async () => {
    const storePath = tempStorePath();
    const preview = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: "75164 node ttys013\n",
        psCommTtyByPid: {
          75164: "node ttys013"
        },
        psArgsByPid: {
          75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js"
        }
      }) as any
    });

    const confirmed = await confirmCodexBinding({
      candidateId: preview.codexBinding!.candidateId!,
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:01:00.000Z"),
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: "75164 zsh ttys013\n",
        psCommTtyByPid: {
          75164: "zsh ttys013"
        }
      }) as any,
      fetchImpl: async () => {
        throw new Error("should not create instance");
      }
    });

    assert.equal(confirmed.ok, false);
    assert.equal(confirmed.reasonCode, "candidate_not_active");
  });

  it("routes a manual test event only to the bound instance", async () => {
    const storePath = tempStorePath();
    const spawnImpl = fakeProbeSpawn({
      osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
      psStdout: "75164 node ttys013\n",
      psCommTtyByPid: {
        75164: "node ttys013"
      },
      psArgsByPid: {
        75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js"
      },
      codexVersion: "codex-cli 0.131.0\n"
    }) as any;
    const preview = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl
    });
    const confirmed = await confirmCodexBinding({
      candidateId: preview.codexBinding!.candidateId!,
      name: "V4.2 Cat",
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:01:00.000Z"),
      spawnImpl,
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        created: true,
        instanceId: "codex_v42",
        displayName: "V4.2 Cat",
        windowLabel: "pet-codex_v42"
      }), { status: 200 })
    });
    const bindingId = confirmed.codexBinding?.bindingId;
    assert.ok(bindingId);
    const calledUrls: string[] = [];

    const routed = await routeCodexBindingTest({
      bindingId,
      level: "running",
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:02:00.000Z"),
      spawnImpl,
      fetchImpl: async (input, init) => {
        calledUrls.push(String(input));
        if (String(input).endsWith("/api/instances")) {
          return new Response(JSON.stringify({
            ok: true,
            instances: [
              { instanceId: "default", displayName: "Agent Desktop Pet", isDefault: true, currentState: "idle" },
              { instanceId: "codex_v42", displayName: "V4.2 Cat", currentState: "idle" },
              { instanceId: "codex_other", displayName: "Other Cat", currentState: "idle" }
            ]
          }), { status: 200 });
        }
        assert.equal(String(input), "http://127.0.0.1:17321/api/instances/codex_v42/events");
        assert.equal(init?.method, "POST");
        const payload = JSON.parse(String(init?.body));
        assert.equal(payload.level, "running");
        assert.equal(payload.metadata.codexBinding, "terminal-app-manual-route-test");
        assert.equal(payload.metadata.lifecycleEvidence, "false");
        return new Response(JSON.stringify({
          ok: true,
          accepted: true,
          eventId: "evt_route_test",
          queued: true
        }), { status: 202 });
      }
    });

    assert.equal(routed.ok, true);
    assert.equal(routed.eventId, "evt_route_test");
    assert.equal(routed.instanceId, "codex_v42");
    assert.deepEqual(calledUrls, [
      "http://127.0.0.1:17321/api/instances",
      "http://127.0.0.1:17321/api/instances/codex_v42/events"
    ]);
    const serialized = JSON.stringify(routed);
    assert.equal(serialized.includes("secret-token"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("/Users/"), false);
  });

  it("does not route unknown or stale bindings", async () => {
    const storePath = tempStorePath();
    const unknown = await routeCodexBindingTest({
      bindingId: "bind_missing",
      level: "running",
      token: "secret-token",
      storePath,
      fetchImpl: async () => {
        throw new Error("should not call bridge");
      }
    });
    assert.equal(unknown.ok, false);
    assert.equal(unknown.reasonCode, "binding_not_found");

    const spawnImpl = fakeProbeSpawn({
      osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
      psStdout: "75164 node ttys013\n",
      psCommTtyByPid: {
        75164: "node ttys013"
      },
      psArgsByPid: {
        75164: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js"
      }
    }) as any;
    const preview = await previewCodexBinding({
      terminal: "terminal",
      storePath,
      now: new Date("2026-05-26T00:00:00.000Z"),
      spawnImpl
    });
    const confirmed = await confirmCodexBinding({
      candidateId: preview.codexBinding!.candidateId!,
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T00:01:00.000Z"),
      spawnImpl,
      fetchImpl: async () => new Response(JSON.stringify({
        ok: true,
        created: true,
        instanceId: "codex_v42"
      }), { status: 200 })
    });
    const stale = await routeCodexBindingTest({
      bindingId: confirmed.codexBinding!.bindingId!,
      level: "running",
      token: "secret-token",
      storePath,
      now: new Date("2026-05-26T01:02:00.000Z"),
      spawnImpl,
      fetchImpl: async () => {
        throw new Error("should not call bridge");
      }
    });
    assert.equal(stale.ok, false);
    assert.equal(stale.reasonCode, "binding_stale");
  });
});

describe("petctl codex probe", () => {
  it("returns a redacted Terminal.app candidate without leaking tty or paths", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys001\n",
        psStdout: "456 codex ttys001\n",
        codexVersion: "codex-cli test\n"
      }) as any
    });

    assert.equal(result.ok, true);
    assert.equal(result.probe?.terminalBundleId, "com.apple.Terminal");
    assert.equal(result.probe?.processId, 456);
    assert.equal(result.probe?.processName, "codex");
    assert.equal(result.probe?.verdict, "candidate");
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("/dev/ttys001"), false);
    assert.equal(serialized.includes("ttys001"), false);
    assert.equal(serialized.includes("/Users/"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("secret-token"), false);
  });

  it("returns permission denied without raw os output", async () => {
    const result = await runCodexProbe({
      terminal: "iterm2",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStatus: 1,
        osascriptStderr: "Not authorized to send Apple events to /Users/example"
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "permission_denied");
    assert.equal(result.probe?.permissionState, "denied");
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("Not authorized"), false);
    assert.equal(serialized.includes("/Users/example"), false);
  });

  it("returns unsupported terminal when focused app does not match", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Safari\ncom.apple.Safari\n321\n\n"
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "unsupported_terminal");
    assert.equal(result.probe?.verdict, "unsupported");
  });

  it("returns codex process not found for a terminal without codex on tty", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys002\n",
        psStdout: "456 zsh ttys002\n"
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "codex_process_not_found");
    assert.equal(result.probe?.ttySummary?.startsWith("tty_"), true);
  });

  it("detects Codex when the focused terminal runs the Node packaged CLI", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: [
          "72299 login ttys013",
          "72300 -zsh ttys013",
          "72328 node ttys013",
          "72486 node ttys013"
        ].join("\n"),
        psArgsByPid: {
          72328: "/usr/local/bin/node /usr/local/lib/node_modules/@openai/codex/bin/codex.js",
          72486: "node /Users/example/Desktop/workspace/codexPat/scripts/not-codex.js"
        },
        codexVersion: "codex-cli 0.131.0\n"
      }) as any
    });

    assert.equal(result.ok, true);
    assert.equal(result.probe?.processId, 72328);
    assert.equal(result.probe?.processName, "codex");
    assert.equal(result.probe?.codexCliVersion, "codex-cli 0.131.0");
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("@openai/codex"), false);
    assert.equal(serialized.includes("codex.js"), false);
    assert.equal(serialized.includes("/Users/"), false);
  });

  it("does not treat unrelated Node processes on the same tty as Codex", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: "72486 node ttys013\n",
        psArgsByPid: {
          72486: "node /Users/example/Desktop/workspace/codexPat/scripts/server.js --prompt secret"
        }
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "codex_process_not_found");
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("server.js"), false);
    assert.equal(serialized.includes("--prompt"), false);
    assert.equal(serialized.includes("/Users/example"), false);
  });

  it("does not treat a local codex.js filename as the OpenAI Codex CLI", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "darwin",
      spawnImpl: fakeProbeSpawn({
        osascriptStdout: "Terminal\ncom.apple.Terminal\n123\n/dev/ttys013\n",
        psStdout: "72486 node ttys013\n",
        psArgsByPid: {
          72486: "node ./codex.js"
        }
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "codex_process_not_found");
    assert.equal(JSON.stringify(result).includes("codex.js"), false);
  });

  it("blocks non-macos platforms", async () => {
    const result = await runCodexProbe({
      terminal: "terminal",
      platform: "linux",
      spawnImpl: fakeProbeSpawn({}) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.reasonCode, "unsupported_platform");
  });
});

describe("petctl codex doctor", () => {
  it("reports supported hook diagnostics without leaking sensitive values", async () => {
    const previousInstance = process.env.AGENT_DESKTOP_PET_INSTANCE_ID;
    process.env.AGENT_DESKTOP_PET_INSTANCE_ID = "codex_test";
    const result = await runCodexDoctor({
      token: "secret-token",
      fetchImpl: async () => new Response(JSON.stringify({ ok: true }), { status: 200 }),
      spawnImpl: ((command: string, args?: readonly string[]) => {
        if (command === "codex") {
          return { status: 0, stdout: "codex-cli test\n", stderr: "" };
        }
        if (args?.includes("--check")) {
          return { status: 0, stdout: "", stderr: "" };
        }
        return { status: 1, stdout: "", stderr: "" };
      }) as any
    });
    if (previousInstance === undefined) {
      delete process.env.AGENT_DESKTOP_PET_INSTANCE_ID;
    } else {
      process.env.AGENT_DESKTOP_PET_INSTANCE_ID = previousInstance;
    }

    assert.equal(result.ok, true);
    assert.equal(result.diagnostics?.some((diagnostic) => diagnostic.name === "hook_config" && diagnostic.status === "passed"), true);
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("secret-token"), false);
    assert.equal(serialized.includes("Authorization"), false);
    assert.equal(serialized.includes("/Users/"), false);
    assert.equal(serialized.includes("api-token.json"), false);
  });

  it("treats missing instance env and unavailable desktop as warnings", async () => {
    const previousInstance = process.env.AGENT_DESKTOP_PET_INSTANCE_ID;
    delete process.env.AGENT_DESKTOP_PET_INSTANCE_ID;
    const result = await runCodexDoctor({
      token: "secret-token",
      fetchImpl: async () => {
        throw new Error("offline");
      },
      spawnImpl: ((command: string, args?: readonly string[]) => {
        if (command === "codex") {
          return { status: 0, stdout: "codex-cli test\n", stderr: "" };
        }
        if (args?.includes("--check")) {
          return { status: 0, stdout: "", stderr: "" };
        }
        return { status: 1, stdout: "", stderr: "" };
      }) as any
    });
    if (previousInstance !== undefined) {
      process.env.AGENT_DESKTOP_PET_INSTANCE_ID = previousInstance;
    }

    assert.equal(result.ok, true);
    assert.equal(result.diagnostics?.find((diagnostic) => diagnostic.name === "instance_env")?.status, "warning");
    assert.equal(result.diagnostics?.find((diagnostic) => diagnostic.name === "instance_env")?.reasonCode, "binding_env_missing");
    assert.equal(result.diagnostics?.find((diagnostic) => diagnostic.name === "desktop_health")?.status, "warning");
  });

  it("reports strict managed startup diagnostics with stable reason codes", async () => {
    const result = await runCodexDoctor({
      token: "secret-token",
      strict: true,
      includeInstanceEnv: false,
      includeTrustHint: true,
      fetchImpl: async () => {
        throw new Error("offline");
      },
      spawnImpl: ((command: string, args?: readonly string[]) => {
        if (command === "codex") {
          return { status: 1, stdout: "", stderr: "" };
        }
        if (args?.includes("--check")) {
          return { status: 0, stdout: "", stderr: "" };
        }
        return { status: 1, stdout: "", stderr: "" };
      }) as any
    });

    assert.equal(result.ok, false);
    assert.equal(result.diagnostics?.some((diagnostic) => diagnostic.reasonCode === "codex_not_found"), true);
    assert.equal(result.diagnostics?.some((diagnostic) => diagnostic.reasonCode === "desktop_not_running"), true);
    assert.equal(result.diagnostics?.some((diagnostic) => diagnostic.reasonCode === "hook_trust_required"), true);
    assert.equal(result.diagnostics?.some((diagnostic) => diagnostic.reasonCode === "binding_env_missing"), false);
    const serialized = JSON.stringify(result);
    assert.equal(serialized.includes("secret-token"), false);
    assert.equal(serialized.includes("Authorization"), false);
  });
});

describe("petctl codex session status", () => {
  it("returns sanitized managed session status without raw binding id", () => {
    const storePath = tempStorePath();
    touchManagedSession({
      instanceId: "codex_status",
      bindingId: "bind_managed_abc123",
      mode: "tui",
      monitor: "hooks",
      status: "active",
      lastEventKind: "UserPromptSubmit",
      now: new Date("2026-05-27T00:00:00.000Z"),
      storePath
    });
    const result = getManagedSessionStatus({
      instanceId: "codex_status",
      now: new Date("2026-05-27T00:01:00.000Z"),
      storePath
    });

    assert.equal(result.ok, true);
    assert.equal(result.codexSession?.instanceId, "codex_status");
    assert.equal(result.codexSession?.mode, "tui");
    assert.equal(result.codexSession?.monitor, "hooks");
    assert.equal(result.codexSession?.status, "active");
    assert.equal(result.codexSession?.lastEventKind, "UserPromptSubmit");
    assert.match(result.codexSession?.bindingId ?? "", /^binding_[a-f0-9]{12}$/);
    assert.equal(JSON.stringify(result).includes("bind_managed_abc123"), false);
  });

  it("marks old managed sessions stale", () => {
    const storePath = tempStorePath();
    touchManagedSession({
      instanceId: "codex_stale",
      bindingId: "bind_managed_stale",
      mode: "exec",
      monitor: "jsonl",
      status: "active",
      lastEventKind: "turn.started",
      now: new Date("2026-05-27T00:00:00.000Z"),
      storePath
    });
    const result = getManagedSessionStatus({
      instanceId: "codex_stale",
      now: new Date("2026-05-27T00:30:00.000Z"),
      storePath
    });

    assert.equal(result.codexSession?.status, "stale");
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

function fakeProbeSpawn(options: {
  osascriptStatus?: number;
  osascriptStdout?: string;
  osascriptStderr?: string;
  psStdout?: string;
  psCommTtyByPid?: Record<number, string>;
  psArgsByPid?: Record<number, string>;
  codexVersion?: string;
}) {
  return (command: string, args?: readonly string[]) => {
    if (command === "osascript") {
      return {
        status: options.osascriptStatus ?? 0,
        stdout: options.osascriptStdout ?? "",
        stderr: options.osascriptStderr ?? ""
      };
    }
    if (command === "ps") {
      if (args?.[0] === "-p" && args[2] === "-o" && args[3] === "comm=,tty=") {
        const pid = Number(args[1]);
        const stdout = Number.isInteger(pid) ? options.psCommTtyByPid?.[pid] : undefined;
        return {
          status: stdout === undefined ? 1 : 0,
          stdout: stdout ?? "",
          stderr: ""
        };
      }
      if (args?.[0] === "-p" && args[2] === "-o" && args[3] === "args=") {
        const pid = Number(args[1]);
        const stdout = Number.isInteger(pid) ? options.psArgsByPid?.[pid] : undefined;
        return {
          status: stdout === undefined ? 1 : 0,
          stdout: stdout ?? "",
          stderr: ""
        };
      }
      return {
        status: 0,
        stdout: options.psStdout ?? "",
        stderr: ""
      };
    }
    if (command === "codex" && args?.[0] === "--version") {
      return {
        status: options.codexVersion === undefined ? 1 : 0,
        stdout: options.codexVersion ?? "",
        stderr: ""
      };
    }
    return { status: 1, stdout: "", stderr: "" };
  };
}

function tempStorePath() {
  const dir = mkdtempSync(join(tmpdir(), "petctl-bind-test-"));
  process.on("exit", () => {
    try {
      rmSync(dir, { recursive: true, force: true });
    } catch {
      // best effort cleanup
    }
  });
  return join(dir, "codex-bindings.json");
}

function validImportManifest(rendererKind: "gltf" | "sprite" = "gltf"): any {
  const extension = rendererKind === "sprite" ? "png" : "glb";
  const assets: Record<string, { assetId: string; kind: "gltf" | "sprite"; fileName: string }> = {};
  const actions: Record<string, { assetId: string; loop: boolean; priority: "base" | "transient" | "urgent"; durationMs?: number }> = {};
  for (const action of ["idle", "thinking", "running", "success", "warning", "error", "need_input", "sleeping"]) {
    assets[action] = { assetId: action, kind: rendererKind, fileName: `${action}.${extension}` };
    actions[action] = {
      assetId: action,
      loop: action === "idle" || action === "thinking" || action === "running" || action === "sleeping",
      priority: action === "error" || action === "need_input" ? "urgent" : action === "success" || action === "warning" ? "transient" : "base",
      durationMs: action === "error" || action === "need_input" ? 6000 : undefined
    };
  }
  return {
    schemaVersion: "5.8",
    packId: `mochi-${rendererKind}`,
    displayName: "Mochi",
    rendererKind,
    license: {
      type: "user-generated",
      attribution: "User provided generated asset"
    },
    assets,
    actions
  };
}
