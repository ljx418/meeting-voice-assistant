#!/usr/bin/env node
import { createInterface } from "node:readline";
import { stdin, stdout } from "node:process";
import { petGetCapabilities, petGetState, petListInstances, petNotify } from "./bridge.js";

const TOOLS = [
  {
    name: "pet_notify",
    description: "Send a structured PetEvent through the local Agent Desktop Pet HTTP bridge.",
    inputSchema: {
      type: "object",
      properties: {
        instanceId: { type: "string" },
        event: { type: "object" }
      },
      required: ["event"],
      additionalProperties: false
    }
  },
  {
    name: "pet_list_instances",
    description: "List sanitized desktop pet instances through the local HTTP bridge.",
    inputSchema: {
      type: "object",
      properties: {},
      additionalProperties: false
    }
  },
  {
    name: "pet_get_capabilities",
    description: "Read public Agent Desktop Pet capabilities.",
    inputSchema: {
      type: "object",
      properties: {
        instanceId: { type: "string" }
      },
      additionalProperties: false
    }
  },
  {
    name: "pet_get_state",
    description: "Read sanitized runtime state for one instance or all instances.",
    inputSchema: {
      type: "object",
      properties: {
        instanceId: { type: "string" }
      },
      additionalProperties: false
    }
  }
] as const;

type JsonRpcRequest = {
  jsonrpc?: string;
  id?: string | number | null;
  method?: string;
  params?: unknown;
};

const rl = createInterface({ input: stdin, crlfDelay: Infinity });

rl.on("line", async (line) => {
  if (!line.trim()) return;
  let request: JsonRpcRequest;
  try {
    request = JSON.parse(line);
  } catch {
    write({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } });
    return;
  }

  try {
    const response = await handleRequest(request);
    if (response) write(response);
  } catch {
    write({
      jsonrpc: "2.0",
      id: request.id ?? null,
      error: { code: -32603, message: "Internal error" }
    });
  }
});

async function handleRequest(request: JsonRpcRequest) {
  const id = request.id ?? null;
  if (request.method === "initialize") {
    return {
      jsonrpc: "2.0",
      id,
      result: {
        protocolVersion: "2024-11-05",
        capabilities: { tools: {} },
        serverInfo: { name: "agent-desktop-pet-mcp", version: "0.1.0" }
      }
    };
  }
  if (request.method === "notifications/initialized") return undefined;
  if (request.method === "tools/list") {
    return { jsonrpc: "2.0", id, result: { tools: TOOLS } };
  }
  if (request.method === "tools/call") {
    const params = isRecord(request.params) ? request.params : {};
    const name = typeof params.name === "string" ? params.name : "";
    const args = isRecord(params.arguments) ? params.arguments : {};
    const result = await callTool(name, args);
    return {
      jsonrpc: "2.0",
      id,
      result: {
        isError: result.ok !== true,
        content: [{ type: "text", text: JSON.stringify(result) }]
      }
    };
  }
  return {
    jsonrpc: "2.0",
    id,
    error: { code: -32601, message: "Method not found" }
  };
}

async function callTool(name: string, args: Record<string, unknown>) {
  if (name === "pet_notify") return petNotify(args);
  if (name === "pet_list_instances") return petListInstances(args);
  if (name === "pet_get_capabilities") return petGetCapabilities(args);
  if (name === "pet_get_state") return petGetState(args);
  return { ok: false, reasonCode: "tool_not_found", reason: "tool was not found" };
}

function write(value: unknown) {
  stdout.write(`${JSON.stringify(value)}\n`);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
