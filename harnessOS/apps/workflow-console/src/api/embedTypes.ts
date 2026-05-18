import type { AgentTalkAllowedAction } from "./agentTalkTypes.js";

export interface WorkflowConsoleEmbedDefinition {
  schemaVersion: "v4.0-c";
  embedId: string;
  appId: string;
  defaultProjectId: string;
  defaultWorkspaceId: string;
  capabilityMode: "bff";
  transportMode: "bff_proxy";
  allowedEventChannels: string[];
  allowedActions: AgentTalkAllowedAction[];
  demo_only: true;
  fixture_only: true;
  not_runtime_e2e: true;
}

export interface WorkflowConsoleEmbedBootstrap {
  sessionId?: string;
  threadId?: string;
  bff_eventsource_url: string;
  allowedActions: AgentTalkAllowedAction[];
  demo_only: true;
  fixture_only: true;
  not_runtime_e2e: true;
}
