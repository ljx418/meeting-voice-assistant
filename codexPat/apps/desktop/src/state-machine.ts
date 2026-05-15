import { CAT_STATE_CONFIG, type CatState } from "./pet-states";

export type BehaviorReason = "debug" | "pet_event";

export type BehaviorRequest = {
  state: CatState;
  requestedAt: number;
  reason: BehaviorReason;
};

export type CatStateSnapshot = {
  current: CatState;
  queueLength: number;
  locked: boolean;
  dragging: boolean;
};

type Subscriber = (snapshot: CatStateSnapshot) => void;

const MAX_QUEUE_LENGTH = 8;
const STORAGE_KEY = "agent-desktop-pet:cat-state-snapshot";

export class CatStateMachine {
  private current: CatState = "idle";
  private currentSince = Date.now();
  private lockUntil = 0;
  private isDragging = false;
  private queue: BehaviorRequest[] = [];
  private lastStartedAtByState = new Map<CatState, number>();
  private timer: number | undefined;
  private subscribers = new Set<Subscriber>();
  private pendingAfterDrag: CatState | undefined;

  subscribe(subscriber: Subscriber) {
    this.subscribers.add(subscriber);
    subscriber(this.snapshot());
    return () => this.subscribers.delete(subscriber);
  }

  enqueue(state: CatState, reason: BehaviorReason = "debug") {
    const request: BehaviorRequest = {
      state,
      requestedAt: Date.now(),
      reason
    };

    if (this.isOnCooldown(request.state, request.requestedAt)) {
      return;
    }

    if (this.canStartNow(request)) {
      this.start(request.state, request.requestedAt);
      return;
    }

    this.enqueueRequest(request);
    this.notify();
  }

  setDragging(dragging: boolean) {
    this.isDragging = dragging;
    if (!dragging && this.pendingAfterDrag) {
      const pending = this.pendingAfterDrag;
      this.pendingAfterDrag = undefined;
      this.start(pending, Date.now());
      return;
    }
    this.notify();
  }

  snapshot(): CatStateSnapshot {
    return {
      current: this.current,
      queueLength: this.queue.length,
      locked: Date.now() < this.lockUntil,
      dragging: this.isDragging
    };
  }

  destroy() {
    window.clearTimeout(this.timer);
    this.subscribers.clear();
  }

  private canStartNow(request: BehaviorRequest) {
    const now = request.requestedAt;
    const currentConfig = CAT_STATE_CONFIG[this.current];
    const nextConfig = CAT_STATE_CONFIG[request.state];

    if (request.state === this.current) {
      return false;
    }

    if (this.current === "sleeping" && request.state !== "sleeping") {
      return true;
    }

    if (now < this.lockUntil && nextConfig.priority <= CAT_STATE_CONFIG.running.priority) {
      return false;
    }

    if (nextConfig.priority > currentConfig.priority) {
      return true;
    }

    return this.current === "idle";
  }

  private enqueueRequest(request: BehaviorRequest) {
    if (request.state === "thinking" || request.state === "running") {
      this.queue = this.queue.filter((item) => item.state !== request.state);
    }

    if (this.queue.some((item) => item.state === request.state)) {
      return;
    }

    if (this.queue.length >= MAX_QUEUE_LENGTH) {
      const lowestIndex = this.queue.reduce((lowest, item, index, items) => {
        const itemPriority = CAT_STATE_CONFIG[item.state].priority;
        const lowestPriority = CAT_STATE_CONFIG[items[lowest].state].priority;
        return itemPriority < lowestPriority ? index : lowest;
      }, 0);

      const lowest = this.queue[lowestIndex];
      if (CAT_STATE_CONFIG[request.state].priority <= CAT_STATE_CONFIG[lowest.state].priority) {
        return;
      }
      this.queue.splice(lowestIndex, 1);
    }

    this.queue.push(request);
  }

  private start(state: CatState, now: number) {
    window.clearTimeout(this.timer);

    if (this.isDragging) {
      this.pendingAfterDrag = state;
      this.notify();
      return;
    }

    const config = CAT_STATE_CONFIG[state];
    this.current = state;
    this.currentSince = now;
    this.lockUntil = now + config.lockMs;
    this.lastStartedAtByState.set(state, now);

    if (config.durationMs !== "indefinite") {
      this.timer = window.setTimeout(() => this.completeCurrentState(), config.durationMs);
    } else {
      this.timer = undefined;
    }

    this.notify();
  }

  private completeCurrentState() {
    const next = this.dequeueNext();
    if (next) {
      this.start(next.state, Date.now());
      return;
    }

    const fallback = CAT_STATE_CONFIG[this.current].next;
    if (fallback !== this.current) {
      this.start(fallback, Date.now());
      return;
    }

    this.notify();
  }

  private dequeueNext() {
    if (this.queue.length === 0) {
      return undefined;
    }

    const sorted = [...this.queue].sort((a, b) => {
      const priorityDelta = CAT_STATE_CONFIG[b.state].priority - CAT_STATE_CONFIG[a.state].priority;
      return priorityDelta || a.requestedAt - b.requestedAt;
    });
    const next = sorted[0];
    this.queue = this.queue.filter((item) => item !== next);
    return next;
  }

  private isOnCooldown(state: CatState, now: number) {
    const lastStartedAt = this.lastStartedAtByState.get(state);
    if (!lastStartedAt) {
      return false;
    }
    return now - lastStartedAt < CAT_STATE_CONFIG[state].cooldownMs;
  }

  private notify() {
    const snapshot = this.snapshot();
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot));
    window.dispatchEvent(new CustomEvent<CatStateSnapshot>("cat-state-change", { detail: snapshot }));
    for (const subscriber of this.subscribers) {
      subscriber(snapshot);
    }
  }
}

export function readStoredCatStateSnapshot(): CatStateSnapshot {
  const fallback: CatStateSnapshot = {
    current: "idle",
    queueLength: 0,
    locked: false,
    dragging: false
  };

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return fallback;
  }

  try {
    return { ...fallback, ...JSON.parse(raw) };
  } catch {
    return fallback;
  }
}
