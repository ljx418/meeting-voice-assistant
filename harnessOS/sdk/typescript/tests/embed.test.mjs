import assert from "node:assert/strict";
import { test } from "node:test";

import {
  sanitizeEmbedBootstrapForLog,
  validateEmbedDefinition,
  validateHostBusinessEvent,
} from "../dist/index.js";

const definition = {
  schemaVersion: "1",
  embedId: "reference_app_embed",
  appId: "reference_app",
  defaultProjectId: "demo",
  defaultWorkspaceId: "local",
  capabilityMode: "bff",
  transportMode: "bff_proxy",
  allowedEventChannels: ["chat", "job", "artifact", "approval"],
  allowedActions: ["session.start", "turn.start", "events.subscribe", "approval.respond", "artifact.read_metadata", "job.get", "pack.get"],
  initialView: "chat",
  tracePolicy: { enabled: false },
};

test("EmbedDefinition validates static production shape", () => {
  const validated = validateEmbedDefinition(definition);
  assert.equal(validated.capabilityMode, "bff");
  assert.equal(validated.transportMode, "bff_proxy");
  assert.deepEqual(validated.tracePolicy, { enabled: false });
});

test("EmbedDefinition rejects runtime fields and forbidden actions", () => {
  assert.throws(
    () => validateEmbedDefinition({ ...definition, metadata: { eventsourceUrl: "/v1/events/subscribe?subscription_token=secret" } }),
    /runtime or token field/,
  );
  assert.throws(
    () => validateEmbedDefinition({ ...definition, allowedActions: ["approval.approve"] }),
    /forbidden/,
  );
  assert.throws(
    () => validateEmbedDefinition({ ...definition, allowedActions: ["meeting.process_recording"] }),
    /business-specific/,
  );
});

test("EmbedBootstrap sanitizer redacts signed URL query", () => {
  const bootstrap = {
    embedDefinition: definition,
    eventSubscription: {
      eventsourceUrl: "/bff/events/subscribe?subscription_token=secret&channels=chat",
      replayCursor: "cursor_1",
      allowedChannels: ["chat"],
    },
  };
  const sanitized = sanitizeEmbedBootstrapForLog(bootstrap);
  assert.equal(JSON.stringify(sanitized).includes("secret"), false);
  assert.equal(sanitized.eventSubscription.eventsourceUrl.includes("subscription_token="), true);
});

test("HostBusinessEvent remains in reserved business namespace", () => {
  assert.equal(validateHostBusinessEvent({ type: "business.reference.updated", payload: {} }).type, "business.reference.updated");
  assert.throws(() => validateHostBusinessEvent({ type: "chat.updated", payload: {} }), /business/);
  assert.throws(() => validateHostBusinessEvent({ type: "business.meeting", payload: {} }), /platform-neutral/);
});
