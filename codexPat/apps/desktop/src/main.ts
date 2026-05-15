import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { CAT_STATE_CONFIG, CAT_STATE_ORDER, labelForState, type CatState } from "./pet-states";
import { CatStateMachine, readStoredCatStateSnapshot, type CatStateSnapshot } from "./state-machine";
import "./styles.css";

type AppSettings = {
  muted: boolean;
  petVisible: boolean;
  petX: number | null;
  petY: number | null;
};

type WindowPosition = {
  x: number;
  y: number;
};

type ApiEventSummary = {
  id: string;
  sourceId?: string;
  level?: string;
  titlePreview?: string;
  messagePreview?: string;
  status: number;
  accepted: boolean;
  reasonCode?: string;
  reason?: string;
  receivedAt: string;
};

type BridgeDiagnostics = {
  enabled: boolean;
  listenAddress: string;
  queueLength: number;
  queueCapacity: number;
  acceptedEvents: ApiEventSummary[];
  rejectedEvents: ApiEventSummary[];
  lastAccepted?: ApiEventSummary | null;
  lastRejected?: ApiEventSummary | null;
  sound: {
    playbackAvailable: boolean;
    muted: boolean;
    cooldownMs: number;
    acceptedIds: string[];
    lastDecision?: {
      sound: string;
      played: boolean;
      reason: string;
      decidedAt: string;
    } | null;
  };
  hardwareLight: boolean;
  startupError?: string | null;
};

type AcceptedPetEvent = {
  source: {
    id: string;
    kind: string;
    name?: string;
  };
  via: "http";
  level: CatState;
  title?: string;
  message?: string;
  action?: string;
  sound?: string;
  durationMs?: number;
  hardware?: unknown;
  metadata?: unknown;
  receivedAt: string;
};

const STATE_CLASS_NAMES = Object.values(CAT_STATE_CONFIG).map((config) => config.cssClass);
const app = document.querySelector<HTMLDivElement>("#app");

if (!app) {
  throw new Error("Missing #app root element");
}

const appRoot = app;
const currentWindow = getCurrentWindow();
const windowLabel = currentWindow.label;

function isSettingsWindow() {
  return windowLabel === "settings";
}

async function getSettings(): Promise<AppSettings> {
  return invoke<AppSettings>("get_settings");
}

async function setMuted(muted: boolean): Promise<AppSettings> {
  return invoke<AppSettings>("set_muted", { muted });
}

async function getPetPosition(): Promise<WindowPosition> {
  return invoke<WindowPosition>("get_pet_position");
}

async function getApiDebugState(): Promise<BridgeDiagnostics> {
  return invoke<BridgeDiagnostics>("get_api_debug_state");
}

function renderPet(settings: AppSettings) {
  document.body.classList.add("pet-body");
  document.body.classList.remove("settings-body");
  appRoot.innerHTML = `
    <main class="pet-shell cat-state-idle" aria-label="Agent Desktop Pet">
      <button class="pet-stage" type="button" aria-label="Drag Agent Desktop Pet">
        <span class="cat" aria-hidden="true">
          <span class="cat-shadow"></span>
          <span class="cat-tail"></span>
          <span class="cat-body"></span>
          <span class="cat-head">
            <span class="cat-ear cat-ear-left"></span>
            <span class="cat-ear cat-ear-right"></span>
            <span class="cat-eye cat-eye-left"></span>
            <span class="cat-eye cat-eye-right"></span>
            <span class="cat-muzzle"></span>
          </span>
        </span>
      </button>
      <p class="pet-status" aria-live="polite">
        <span id="pet-state-label">Idle</span>
        <span id="pet-queue-label" class="pet-queue-label"></span>
        <span class="pet-muted-label">${settings.muted ? " · Muted" : ""}</span>
      </p>
      <nav class="debug-strip" aria-label="Local state debugger">
        ${CAT_STATE_ORDER.map((state) => `
          <button class="debug-state-button" type="button" data-state="${state}" title="Trigger ${labelForState(state)}">
            ${shortStateLabel(state)}
          </button>
        `).join("")}
      </nav>
    </main>
  `;

  const stateMachine = new CatStateMachine();
  const shell = appRoot.querySelector<HTMLElement>(".pet-shell");
  const stateLabel = appRoot.querySelector<HTMLElement>("#pet-state-label");
  const queueLabel = appRoot.querySelector<HTMLElement>("#pet-queue-label");

  stateMachine.subscribe((snapshot) => {
    updatePetStateUi(shell, stateLabel, queueLabel, snapshot);
  });

  listen<AcceptedPetEvent>("pet-event:accepted", (event) => {
    if (isCatState(event.payload.level)) {
      stateMachine.enqueue(event.payload.level, "pet_event");
    }
  }).catch((error) => console.error("failed to listen for pet events", error));

  appRoot.querySelectorAll<HTMLButtonElement>("[data-state]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      stateMachine.enqueue(button.dataset.state as CatState);
    });
  });

  const dragTarget = appRoot.querySelector<HTMLButtonElement>(".pet-stage");
  dragTarget?.addEventListener("pointerdown", async (event) => {
    if (event.button !== 0) {
      return;
    }
    event.preventDefault();
    shell?.classList.add("pet-dragging");
    stateMachine.setDragging(true);
    try {
      await currentWindow.startDragging();
    } finally {
      window.setTimeout(() => {
        shell?.classList.remove("pet-dragging");
        stateMachine.setDragging(false);
      }, 200);
    }
  });
}

async function renderSettings(settings: AppSettings) {
  document.body.classList.add("settings-body");
  document.body.classList.remove("pet-body");
  const position = await getPetPosition().catch(() => ({ x: 0, y: 0 }));
  const stateSnapshot = readStoredCatStateSnapshot();
  const apiDebugState = await getApiDebugState().catch(() => ({
    enabled: false,
    listenAddress: "127.0.0.1:17321",
    queueLength: 0,
    queueCapacity: 32,
    acceptedEvents: [],
    rejectedEvents: [],
    lastAccepted: null,
    lastRejected: null,
    sound: {
      playbackAvailable: false,
      muted: settings.muted,
      cooldownMs: 1200,
      acceptedIds: ["none", "success_chime", "warning_chime", "error_chime", "need_input_chime"],
      lastDecision: null
    },
    hardwareLight: false,
    startupError: "Unable to read API debug state"
  }));

  appRoot.innerHTML = `
    <main class="settings-panel">
      <header class="settings-header">
        <div>
          <h1>Agent Desktop Pet</h1>
          <p>Phase 3 local event bridge debug settings</p>
        </div>
      </header>

      <section class="settings-section">
        <div>
          <h2>Sound</h2>
          <p>Mute state is persisted across launches.</p>
        </div>
        <button class="primary-action" id="mute-toggle" type="button">
          ${settings.muted ? "Unmute" : "Mute"}
        </button>
      </section>

      <section class="settings-section">
        <div>
          <h2>Pet Position</h2>
          <p>Current window position: x=${Math.round(position.x)}, y=${Math.round(position.y)}</p>
        </div>
      </section>

      <section class="settings-section">
        <div>
          <h2>Pet State</h2>
          <p id="settings-state-summary">${settingsStateSummary(stateSnapshot)}</p>
        </div>
        <button class="secondary-action" id="state-refresh" type="button">Refresh</button>
      </section>

      <section class="settings-section api-debug-section">
        <div>
          <h2>Local HTTP API</h2>
          <p id="settings-api-summary">${apiDebugSummary(apiDebugState)}</p>
        </div>
        <button class="secondary-action" id="api-refresh" type="button">Refresh</button>
      </section>

      <section class="diagnostics-panel" id="diagnostics-panel">
        ${diagnosticsPanel(apiDebugState)}
      </section>

      <section class="settings-section muted-section" aria-disabled="true">
        <div>
          <h2>Cat Size</h2>
          <p>Size controls are reserved for a later phase.</p>
        </div>
        <input type="range" min="80" max="140" value="100" disabled aria-label="Cat size placeholder" />
      </section>

      <section class="event-empty">
        <h2>Event Log</h2>
        <p>Phase 3 only keeps the latest accepted and rejected HTTP event summaries. Full event log UI is not implemented.</p>
      </section>
    </main>
  `;

  appRoot.querySelector<HTMLButtonElement>("#mute-toggle")?.addEventListener("click", async () => {
    const updated = await setMuted(!settings.muted);
    await renderSettings(updated);
  });

  appRoot.querySelector<HTMLButtonElement>("#state-refresh")?.addEventListener("click", () => {
    const summary = appRoot.querySelector<HTMLElement>("#settings-state-summary");
    if (summary) {
      summary.textContent = settingsStateSummary(readStoredCatStateSnapshot());
    }
  });

  appRoot.querySelector<HTMLButtonElement>("#api-refresh")?.addEventListener("click", async () => {
    const summary = appRoot.querySelector<HTMLElement>("#settings-api-summary");
    const panel = appRoot.querySelector<HTMLElement>("#diagnostics-panel");
    const diagnostics = await getApiDebugState();
    if (summary) {
      summary.textContent = apiDebugSummary(diagnostics);
    }
    if (panel) {
      panel.innerHTML = diagnosticsPanel(diagnostics);
    }
  });
}

async function boot() {
  const settings = await getSettings();
  if (isSettingsWindow()) {
    await renderSettings(settings);
  } else {
    renderPet(settings);
  }
}

boot().catch((error) => {
  console.error(error);
  appRoot.innerHTML = `<pre class="boot-error">${String(error)}</pre>`;
});

function updatePetStateUi(
  shell: HTMLElement | null,
  stateLabel: HTMLElement | null,
  queueLabel: HTMLElement | null,
  snapshot: CatStateSnapshot
) {
  shell?.classList.remove(...STATE_CLASS_NAMES);
  shell?.classList.add(CAT_STATE_CONFIG[snapshot.current].cssClass);

  if (stateLabel) {
    stateLabel.textContent = labelForState(snapshot.current);
  }
  if (queueLabel) {
    queueLabel.textContent = snapshot.queueLength > 0 ? ` · Queue ${snapshot.queueLength}` : "";
  }
}

function settingsStateSummary(snapshot: CatStateSnapshot) {
  const locked = snapshot.locked ? ", locked" : "";
  const dragging = snapshot.dragging ? ", dragging" : "";
  return `Current pet state: ${labelForState(snapshot.current)}; behavior queue: ${snapshot.queueLength}${locked}${dragging}.`;
}

function shortStateLabel(state: CatState) {
  const labels: Record<CatState, string> = {
    idle: "Idle",
    thinking: "Think",
    running: "Run",
    success: "OK",
    warning: "Warn",
    error: "Err",
    need_input: "Input",
    sleeping: "Sleep"
  };
  return labels[state];
}

function isCatState(value: string): value is CatState {
  return value in CAT_STATE_CONFIG;
}

function apiDebugSummary(state: BridgeDiagnostics) {
  const startup = state.startupError ? ` startup error=${state.startupError};` : "";
  return `API enabled=${state.enabled}; listen=${state.listenAddress}; queue=${state.queueLength}/${state.queueCapacity};${startup} sound playback=${state.sound.playbackAvailable}; muted=${state.sound.muted}; hardware light=${state.hardwareLight}.`;
}

function diagnosticsPanel(state: BridgeDiagnostics) {
  return `
    <div class="diagnostics-header">
      <div>
        <h2>Event Diagnostics</h2>
        <p>Accepted and rejected summaries are in-memory only.</p>
      </div>
      <dl class="diagnostics-metrics">
        <div><dt>Queue</dt><dd>${state.queueLength}/${state.queueCapacity}</dd></div>
        <div><dt>Accepted</dt><dd>${state.acceptedEvents.length}</dd></div>
        <div><dt>Rejected</dt><dd>${state.rejectedEvents.length}</dd></div>
        <div><dt>Sound</dt><dd>${state.sound.playbackAvailable ? "available" : "off"}${state.sound.muted ? " / muted" : ""}</dd></div>
      </dl>
    </div>
    <div class="sound-diagnostics">
      <h3>Sound</h3>
      <p>Accepted IDs: ${state.sound.acceptedIds.map(escapeHtml).join(", ")}</p>
      <p>Cooldown: ${state.sound.cooldownMs}ms</p>
      <p>Last decision: ${soundDecisionLabel(state.sound.lastDecision)}</p>
    </div>
    <div class="event-lists">
      <div>
        <h3>Latest Accepted</h3>
        ${eventList(state.acceptedEvents, "No accepted events yet.")}
      </div>
      <div>
        <h3>Latest Rejected</h3>
        ${eventList(state.rejectedEvents, "No rejected events yet.")}
      </div>
    </div>
  `;
}

function soundDecisionLabel(decision: BridgeDiagnostics["sound"]["lastDecision"]) {
  if (!decision) {
    return "No sound decision yet.";
  }
  return `${decision.sound}; played=${decision.played}; reason=${decision.reason}`;
}

function eventList(events: ApiEventSummary[], emptyLabel: string) {
  if (events.length === 0) {
    return `<p class="diagnostics-empty">${emptyLabel}</p>`;
  }
  return `
    <ul class="event-summary-list">
      ${events.slice(0, 8).map((event) => `
        <li>
          <span class="event-summary-line">
            <strong>${escapeHtml(event.level ?? event.reasonCode ?? "event")}</strong>
            <span>${escapeHtml(event.sourceId ?? "unknown")}</span>
            <span>${event.status}</span>
          </span>
          <span class="event-summary-detail">
            ${escapeHtml(event.titlePreview ?? event.reason ?? "")}
            ${event.messagePreview ? ` · ${escapeHtml(event.messagePreview)}` : ""}
          </span>
        </li>
      `).join("")}
    </ul>
  `;
}

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (char) => {
    const entities: Record<string, string> = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      "\"": "&quot;",
      "'": "&#039;"
    };
    return entities[char] ?? char;
  });
}
