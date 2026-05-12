export class HarnessOSError extends Error {
  constructor(message: string) {
    super(redactText(message));
    this.name = new.target.name;
  }
}

export class TransportError extends HarnessOSError {}

export class RpcError extends HarnessOSError {
  readonly code: string;
  readonly data: Record<string, unknown>;

  constructor(code: string, message: string, data: Record<string, unknown> = {}) {
    super(`${code}: ${redactText(message)}`);
    this.code = code;
    this.data = redactData(data);
  }
}

export class ProtocolError extends RpcError {}
export class InvalidParamsError extends ProtocolError {}
export class MethodNotFoundError extends ProtocolError {}
export class SessionNotFoundError extends ProtocolError {}
export class AuthRequiredError extends ProtocolError {}
export class AuthInvalidError extends ProtocolError {}
export class AuthForbiddenError extends ProtocolError {}
export class CapabilityDeniedError extends ProtocolError {}
export class ScopeMismatchError extends ProtocolError {}
export class MethodForbiddenError extends ProtocolError {}
export class ApprovalConflictError extends ProtocolError {}
export class ApprovalNotFoundError extends ProtocolError {}
export class ArtifactReadBlockedError extends ProtocolError {}
export class EventCursorInvalidError extends ProtocolError {}
export class PackNotFoundError extends ProtocolError {}
export class ConnectorNotFoundError extends ProtocolError {}

const ERROR_TYPES: Record<string, typeof ProtocolError> = {
  INVALID_PARAMS: InvalidParamsError,
  METHOD_NOT_FOUND: MethodNotFoundError,
  SESSION_NOT_FOUND: SessionNotFoundError,
  AUTH_REQUIRED: AuthRequiredError,
  AUTH_INVALID: AuthInvalidError,
  AUTH_FORBIDDEN: AuthForbiddenError,
  CAPABILITY_DENIED: CapabilityDeniedError,
  SCOPE_MISMATCH: ScopeMismatchError,
  METHOD_FORBIDDEN: MethodForbiddenError,
  APPROVAL_CONFLICT: ApprovalConflictError,
  APPROVAL_NOT_FOUND: ApprovalNotFoundError,
  ARTIFACT_READ_BLOCKED: ArtifactReadBlockedError,
  EVENT_CURSOR_INVALID: EventCursorInvalidError,
  PACK_NOT_FOUND: PackNotFoundError,
  CONNECTOR_NOT_FOUND: ConnectorNotFoundError,
};

export function errorFromRpc(payload: unknown): RpcError {
  const value = isRecord(payload) ? payload : {};
  const code = String(value.code || "RUNTIME_ERROR");
  const message = String(value.message || code);
  const data = isRecord(value.data) ? value.data : {};
  const ErrorType = ERROR_TYPES[code] || ProtocolError;
  return new ErrorType(code, message, data);
}

export function redactText(value: string): string {
  return value
    .replace(/\bAuthorization\s*:?\s*Bearer\s+[A-Za-z0-9._-]+/gi, "Authorization: Bearer [REDACTED]")
    .replace(/\bBearer\s+[A-Za-z0-9._-]{8,}\b/gi, "Bearer [REDACTED]")
    .replace(/\b([A-Za-z0-9_-]*token|sk|api[_-]?key|secret|password)\s*[:=]\s*['"]?[^'"\s,;]+/gi, "$1=[REDACTED]");
}

export function redactData(data: Record<string, unknown>): Record<string, unknown> {
  const redacted: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(data)) {
    const lower = key.toLowerCase();
    if (lower.includes("token") || lower === "authorization") {
      redacted[key] = "[REDACTED]";
    } else if (typeof value === "string") {
      redacted[key] = redactText(value);
    } else {
      redacted[key] = value;
    }
  }
  return redacted;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
