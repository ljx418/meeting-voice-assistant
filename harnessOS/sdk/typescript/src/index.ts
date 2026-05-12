export { HarnessOSClient, type HarnessOSClientOptions } from "./client.js";
export {
  ApprovalConflictError,
  ApprovalNotFoundError,
  ArtifactReadBlockedError,
  AuthForbiddenError,
  AuthInvalidError,
  AuthRequiredError,
  CapabilityDeniedError,
  ConnectorNotFoundError,
  EventCursorInvalidError,
  HarnessOSError,
  InvalidParamsError,
  MethodForbiddenError,
  MethodNotFoundError,
  PackNotFoundError,
  ProtocolError,
  RpcError,
  ScopeMismatchError,
  SessionNotFoundError,
  TransportError,
} from "./errors.js";
export { CapabilityToken, EventSubscription, Scope, type ScopeValue } from "./models.js";
export { FetchJsonRpcTransport, type JsonRpcTransport } from "./transport.js";
export { fetchStreamRequest, nativeEventSourceUrl } from "./events.js";
export {
  sanitizeEmbedBootstrapForLog,
  validateEmbedDefinition,
  validateHostBusinessEvent,
  type CapabilityMode,
  type EmbedBootstrap,
  type EmbedDefinition,
  type EmbedInitialView,
  type EmbedScope,
  type EmbedUiState,
  type HostBusinessEvent,
  type TransportMode,
} from "./embed.js";
