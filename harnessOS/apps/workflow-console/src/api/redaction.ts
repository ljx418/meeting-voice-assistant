const SENSITIVE_KEY_PATTERN = /token|authorization|secret|raw_trace_payload|raw_artifact_content|raw_connector_payload/i;

export function redactValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => redactValue(item));
  }
  if (value && typeof value === "object") {
    const output: Record<string, unknown> = {};
    let redacted = false;
    for (const [key, nested] of Object.entries(value as Record<string, unknown>)) {
      if (SENSITIVE_KEY_PATTERN.test(key)) {
        redacted = true;
        continue;
      }
      output[key] = redactValue(nested);
    }
    if (redacted) {
      output.redacted = "[redacted]";
    }
    return output;
  }
  if (typeof value === "string" && looksSensitive(value)) {
    return "[redacted]";
  }
  return value;
}

export function safeText(value: unknown): string {
  const redacted = redactValue(value);
  if (typeof redacted === "string") return redacted;
  if (redacted === undefined || redacted === null) return "";
  return JSON.stringify(redacted);
}

function looksSensitive(value: string): boolean {
  return /bearer\s+[a-z0-9._-]+/i.test(value) || /capability_token|subscription_token|authorization|secret|raw_trace_payload|raw_artifact_content|raw_connector_payload/i.test(value);
}
