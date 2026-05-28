#!/usr/bin/env node
import { parseArgs, buildEventFromOptions } from "./args.js";
import { activateAssetPack, generateAssetPromptPack, importAssetPack, listAssetPacks } from "./assets.js";
import { confirmCodexBinding, previewCodexBinding, routeCodexBindingTest } from "./codex-bind.js";
import { runCodexDoctor } from "./codex-doctor.js";
import { launchCodex } from "./codex-launch.js";
import { runCodexProbe } from "./codex-probe.js";
import { getManagedSessionStatus } from "./codex-session-status.js";
import { attachCodex, detachInstance, listInstances } from "./instances.js";
import { notify } from "./notify.js";
import { formatResult, EXIT_CODES } from "./output.js";

export async function main(argv = process.argv.slice(2)) {
  let pretty = false;
  try {
    const args = parseArgs(argv);
    pretty = args.pretty;
    let result;
    if (args.command === "attach") {
      result = await attachCodex({
        token: args.token,
        url: args.url,
        name: args.name,
        workspaceLabel: args.workspaceLabel,
        workspaceHash: args.workspaceHash
      });
      if (args.printEnv && result.ok && result.exportCommand) {
        console.log(result.exportCommand);
        return result.exitCode;
      }
      pretty = pretty || args.json;
    } else if (args.command === "list") {
      result = await listInstances({
        token: args.token,
        url: args.url
      });
      pretty = pretty || args.json;
    } else if (args.command === "detach") {
      if (!args.instance) {
        throw new Error("petctl detach requires --instance");
      }
      result = await detachInstance({
        token: args.token,
        url: args.url,
        instance: args.instance
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "launch") {
      result = await launchCodex({
        token: args.token,
        url: args.url,
        name: args.name,
        workspaceLabel: args.workspaceLabel,
        workspaceHash: args.workspaceHash,
        bin: args.bin,
        monitor: args.monitor,
        passthrough: args.passthrough,
        noTitle: args.noTitle
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "session" && args.sessionAction === "start") {
      result = await launchCodex({
        token: args.token,
        url: args.url,
        name: args.name,
        workspaceLabel: args.workspaceLabel,
        workspaceHash: args.workspaceHash,
        bin: args.bin,
        monitor: args.monitor,
        sessionMode: args.mode,
        passthrough: args.passthrough,
        noTitle: args.noTitle
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "session" && args.sessionAction === "status") {
      result = getManagedSessionStatus({
        instanceId: args.instance
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "doctor") {
      result = await runCodexDoctor({
        token: args.token,
        url: args.url,
        includeTrustHint: true
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "probe") {
      result = await runCodexProbe({
        terminal: args.terminal
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "bind" && args.bindAction === "active-window") {
      result = await previewCodexBinding({
        terminal: args.terminal
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "bind" && args.bindAction === "confirm") {
      if (!args.candidate) {
        throw new Error("petctl codex bind confirm requires --candidate");
      }
      result = await confirmCodexBinding({
        candidateId: args.candidate,
        name: args.name,
        token: args.token,
        url: args.url
      });
      pretty = pretty || args.json;
    } else if (args.command === "codex" && args.action === "route" && args.routeAction === "test") {
      if (!args.binding) {
        throw new Error("petctl codex route test requires --binding");
      }
      if (!args.level) {
        throw new Error("petctl codex route test requires --level");
      }
      result = await routeCodexBindingTest({
        bindingId: args.binding,
        level: args.level,
        token: args.token,
        url: args.url
      });
      pretty = pretty || args.json;
    } else if (args.command === "asset" && args.action === "prompt-pack") {
      result = generateAssetPromptPack({
        name: args.name ?? "",
        description: args.description ?? "",
        renderer: args.renderer
      });
      pretty = pretty || args.json;
    } else if (args.command === "asset" && args.action === "import") {
      result = importAssetPack({
        manifestPath: args.manifest ?? "",
        name: args.name
      });
      pretty = pretty || args.json;
    } else if (args.command === "asset" && args.action === "list") {
      result = listAssetPacks();
      pretty = pretty || args.json;
    } else if (args.command === "asset" && args.action === "activate") {
      result = activateAssetPack({
        packId: args.pack ?? "",
        instanceId: args.instance ?? ""
      });
      pretty = pretty || args.json;
    } else if (args.command === "notify") {
      const event = args.json ? await readStdinJson() : buildEventFromOptions(args.payloadOptions);
      result = await notify({
        event,
        token: args.token,
        url: args.url,
        instance: args.instance
      });
    } else {
      throw new Error("unsupported command");
    }
    writeResult(result, pretty);
    return result.exitCode;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const result = {
      ok: false,
      exitCode: EXIT_CODES.genericError,
      reasonCode: message === "confirmation_required" ? "confirmation_required" : "unknown_error",
      reason: message
    };
    writeResult(result, pretty);
    return result.exitCode;
  }
}

async function readStdinJson() {
  const chunks: Buffer[] = [];
  for await (const chunk of process.stdin) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  const raw = Buffer.concat(chunks).toString("utf8").trim();
  if (!raw) {
    throw new Error("--json requires stdin JSON payload");
  }
  return JSON.parse(raw);
}

function writeResult(result: Parameters<typeof formatResult>[0], pretty: boolean) {
  const line = formatResult(result, pretty);
  if (result.ok) {
    console.log(line);
  } else {
    console.error(line);
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const exitCode = await main();
  process.exitCode = exitCode;
}
