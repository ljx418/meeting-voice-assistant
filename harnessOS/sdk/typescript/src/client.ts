import { MethodForbiddenError, TransportError, errorFromRpc } from "./errors.js";
import { CapabilityToken, EventSubscription, Scope, type EventSubscriptionResult, type ScopeValue } from "./models.js";
import { FetchJsonRpcTransport, type JsonRpcTransport } from "./transport.js";
import { isDefaultMethod, isForbiddenMethod, WRAPPER_METHODS } from "./protocolSnapshot.js";

type Params = Record<string, unknown>;

export interface HarnessOSClientOptions {
  baseUrl: string;
  capabilityToken?: string | CapabilityToken;
  scope?: Scope | ScopeValue;
  timeoutMs?: number;
  transport?: JsonRpcTransport;
}

export class HarnessOSClient {
  readonly baseUrl: string;
  readonly timeoutMs: number;
  readonly scope: Scope;
  private readonly capabilityToken?: string;
  private readonly transport: JsonRpcTransport;

  constructor(options: HarnessOSClientOptions) {
    this.baseUrl = options.baseUrl.replace(/\/$/, "");
    this.timeoutMs = options.timeoutMs ?? 30000;
    this.scope = Scope.from(options.scope) || new Scope();
    this.capabilityToken = options.capabilityToken instanceof CapabilityToken ? options.capabilityToken.value : options.capabilityToken;
    this.transport = options.transport || new FetchJsonRpcTransport(`${this.baseUrl}/v1/rpc`);
  }

  toString(): string {
    return `HarnessOSClient(baseUrl=${this.baseUrl}, capabilityToken=${this.capabilityToken ? "set" : "unset"}, scope=${this.scope.toString()})`;
  }

  async rpc(method: string, params: Params = {}): Promise<Record<string, unknown>> {
    this.ensureAllowedMethod(method, params);
    const payload = {
      id: `ts_sdk_${crypto.randomUUID()}`,
      method,
      params: this.withScope(params),
    };
    const headers: Record<string, string> = {};
    if (this.capabilityToken) {
      headers.Authorization = `Bearer ${this.capabilityToken}`;
    }
    const response = await this.transport.request(payload, { headers, timeoutMs: this.timeoutMs });
    return this.parseResponse(response);
  }

  sessionStart(params: { model?: string; scope?: Scope | ScopeValue } = {}): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.sessionStart, this.params({ model: params.model }, params.scope));
  }

  turnStart(params: { input: string; sessionId?: string; domain?: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>> {
    return this.rpc(
      WRAPPER_METHODS.turnStart,
      this.params({ input: params.input, session_id: params.sessionId, domain: params.domain }, params.scope),
    );
  }

  async eventsSubscribe(params: {
    channels?: string[];
    mode?: string;
    sessionId?: string;
    jobId?: string;
    artifactId?: string;
    approvalId?: string;
    traceId?: string;
    ttlSeconds?: number;
    scope?: Scope | ScopeValue;
  } = {}): Promise<EventSubscription> {
    const result = await this.rpc(
      WRAPPER_METHODS.eventsSubscribe,
      this.params(
        {
          channels: params.channels,
          mode: params.mode,
          session_id: params.sessionId,
          job_id: params.jobId,
          artifact_id: params.artifactId,
          approval_id: params.approvalId,
          trace_id: params.traceId,
          ttl_seconds: params.ttlSeconds,
        },
        params.scope,
      ),
    );
    return EventSubscription.fromResult(result as EventSubscriptionResult, this.baseUrl);
  }

  artifactList(params: { sessionId?: string; kind?: string; scope?: Scope | ScopeValue } = {}): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.artifactList, this.params({ session_id: params.sessionId, kind: params.kind }, params.scope));
  }

  artifactReadMetadata(params: { artifactId: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.artifactReadMetadata, this.params({ artifact_id: params.artifactId }, params.scope));
  }

  artifactRegisterExternal(params: { kind: string; externalAssetUri: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>> {
    return this.rpc(
      WRAPPER_METHODS.artifactRegisterExternal,
      this.params({ kind: params.kind, external_asset_uri: params.externalAssetUri }, params.scope),
    );
  }

  artifactLineage(params: { artifactId?: string; sessionId?: string; scope?: Scope | ScopeValue } = {}): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.artifactLineage, this.params({ artifact_id: params.artifactId, session_id: params.sessionId }, params.scope));
  }

  jobGet(params: { jobId: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.jobGet, this.params({ job_id: params.jobId }, params.scope));
  }

  jobList(params: { sessionId?: string; status?: string; scope?: Scope | ScopeValue } = {}): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.jobList, this.params({ session_id: params.sessionId, status: params.status }, params.scope));
  }

  approvalRespond(params: { approvalId: string; decision: "approve" | "reject"; reason?: string; scope?: Scope | ScopeValue }): Promise<Record<string, unknown>> {
    return this.rpc(
      WRAPPER_METHODS.approvalRespond,
      this.params({ approval_id: params.approvalId, decision: params.decision, reason: params.reason }, params.scope),
    );
  }

  connectorHealth(params: { connectorId: string }): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.connectorHealth, { connector_id: params.connectorId });
  }

  packList(): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.packList, {});
  }

  packGet(params: { appId?: string; packId?: string } = {}): Promise<Record<string, unknown>> {
    return this.rpc(WRAPPER_METHODS.packGet, clean({ app_id: params.appId, pack_id: params.packId }));
  }

  wrapperMethods(): Record<string, string> {
    return { ...WRAPPER_METHODS };
  }

  private params(params: Params, scope?: Scope | ScopeValue): Params {
    const payload = clean(params);
    const override = Scope.from(scope);
    if (override) {
      this.scope.ensureCompatible(override);
      payload.scope = override.toJSON();
    }
    return payload;
  }

  private withScope(params: Params): Params {
    const payload = clean(params);
    if ("scope" in payload) {
      const override = Scope.from(payload.scope as ScopeValue);
      if (override) this.scope.ensureCompatible(override);
      return payload;
    }
    payload.scope = this.scope.toJSON();
    return payload;
  }

  private ensureAllowedMethod(method: string, params: Params): void {
    if (
      isForbiddenMethod(method) ||
      !isDefaultMethod(method) ||
      (method === "method.list" && Boolean((params as { include_forbidden?: unknown }).include_forbidden))
    ) {
      throw new MethodForbiddenError("METHOD_FORBIDDEN", `method is not part of the SDK default surface: ${method}`, { method });
    }
  }

  private parseResponse(response: unknown): Record<string, unknown> {
    if (!isRecord(response)) {
      throw new TransportError("malformed JSON-RPC response: response must be an object");
    }
    const hasResult = "result" in response && response.result != null;
    const hasError = "error" in response && response.error != null;
    if (hasResult === hasError) {
      throw new TransportError("malformed JSON-RPC response: expected exactly one of result or error");
    }
    if (hasError) {
      throw errorFromRpc(response.error);
    }
    if (!isRecord(response.result)) {
      throw new TransportError("malformed JSON-RPC response: result must be an object");
    }
    return response.result;
  }
}

function clean(params: Params): Params {
  return Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined && value !== null));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
