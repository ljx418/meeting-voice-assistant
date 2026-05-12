export const DEFAULT_METHODS = new Set([
  "session.start",
  "turn.start",
  "events.subscribe",
  "artifact.list",
  "artifact.read_metadata",
  "artifact.register_external",
  "artifact.lineage",
  "job.get",
  "job.list",
  "approval.respond",
  "connector.health",
  "pack.list",
  "pack.get",
]);

export const FORBIDDEN_PATTERNS = ["meeting.", "knowledge."];

export const FORBIDDEN_METHODS = new Set([
  "approval.approve",
  "approval.reject",
  "workflow.execute_stub",
  "pack.execute_stub",
  "meeting.process_recording",
  "meeting.process_audio_dir",
  "meeting.analyze_text",
  "meeting.capabilities",
  "method.list",
]);

export const WRAPPER_METHODS = {
  sessionStart: "session.start",
  turnStart: "turn.start",
  eventsSubscribe: "events.subscribe",
  artifactList: "artifact.list",
  artifactReadMetadata: "artifact.read_metadata",
  artifactRegisterExternal: "artifact.register_external",
  artifactLineage: "artifact.lineage",
  jobGet: "job.get",
  jobList: "job.list",
  approvalRespond: "approval.respond",
  connectorHealth: "connector.health",
  packList: "pack.list",
  packGet: "pack.get",
} as const;

export type WrapperName = keyof typeof WRAPPER_METHODS;
export type DefaultMethod = (typeof WRAPPER_METHODS)[WrapperName];

export function isDefaultMethod(method: string): boolean {
  return DEFAULT_METHODS.has(method);
}

export function isForbiddenMethod(method: string): boolean {
  return FORBIDDEN_METHODS.has(method) || FORBIDDEN_PATTERNS.some((prefix) => method.startsWith(prefix));
}
