import { TransportError } from "./errors.js";

export interface JsonRpcTransport {
  request(payload: Record<string, unknown>, options: { headers: Record<string, string>; timeoutMs: number }): Promise<unknown>;
}

export class FetchJsonRpcTransport implements JsonRpcTransport {
  readonly endpoint: string;

  constructor(endpoint: string) {
    this.endpoint = endpoint;
  }

  async request(payload: Record<string, unknown>, options: { headers: Record<string, string>; timeoutMs: number }): Promise<unknown> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), options.timeoutMs);
    try {
      const response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });
      const text = await response.text();
      try {
        return JSON.parse(text);
      } catch (error) {
        throw new TransportError("transport returned non JSON response");
      }
    } catch (error) {
      if (error instanceof TransportError) throw error;
      throw new TransportError(`transport request failed: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      clearTimeout(timer);
    }
  }
}
