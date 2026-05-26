import assert from "node:assert/strict";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { describe, it } from "node:test";
import { parseArgs, buildEventFromOptions } from "./args.js";
import { confirmCodexBinding, previewCodexBinding } from "./codex-bind.js";
import { runCodexDoctor } from "./codex-doctor.js";
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
        psStdout: "75164 zsh ttys013\n"
      }) as any,
      fetchImpl: async () => {
        throw new Error("should not create instance");
      }
    });

    assert.equal(confirmed.ok, false);
    assert.equal(confirmed.reasonCode, "candidate_not_active");
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
    assert.equal(result.diagnostics?.find((diagnostic) => diagnostic.name === "desktop_health")?.status, "warning");
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
