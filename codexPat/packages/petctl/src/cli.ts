#!/usr/bin/env node
import { parseArgs, buildEventFromOptions } from "./args.js";
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
    } else {
      const event = args.json ? await readStdinJson() : buildEventFromOptions(args.payloadOptions);
      result = await notify({
        event,
        token: args.token,
        url: args.url,
        instance: args.instance
      });
    }
    writeResult(result, pretty);
    return result.exitCode;
  } catch (error) {
    const result = {
      ok: false,
      exitCode: EXIT_CODES.genericError,
      reasonCode: "unknown_error",
      reason: error instanceof Error ? error.message : String(error)
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
