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
  sourceId?: string | null;
  level?: string | null;
  titlePreview?: string | null;
  messagePreview?: string | null;
  status: number;
  accepted: boolean;
  reasonCode?: string | null;
  reasonField?: string | null;
  reason?: string | null;
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

type TokenStatus = "configured" | "missing" | "unreadable";

type DiagnosticsViewState = {
  diagnostics: BridgeDiagnostics;
  tokenStatus: TokenStatus;
  refreshedAt: Date;
  error?: string;
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
  const diagnosticsState = await readDiagnosticsViewState(settings);

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
          <h2>Diagnostics</h2>
          <p id="settings-api-summary">${apiDebugSummary(diagnosticsState)}</p>
        </div>
        <button class="secondary-action" id="api-refresh" type="button">Refresh</button>
      </section>

      <section class="diagnostics-panel" id="diagnostics-panel">
        ${diagnosticsPanel(diagnosticsState)}
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
    const refreshButton = appRoot.querySelector<HTMLButtonElement>("#api-refresh");
    refreshButton?.setAttribute("disabled", "true");
    const diagnostics = await readDiagnosticsViewState(settings);
    if (summary) {
      summary.textContent = apiDebugSummary(diagnostics);
    }
    if (panel) {
      panel.innerHTML = diagnosticsPanel(diagnostics);
      attachCopyButtons(panel);
    }
    refreshButton?.removeAttribute("disabled");
  });

  const diagnosticsPanelElement = appRoot.querySelector<HTMLElement>("#diagnostics-panel");
  if (diagnosticsPanelElement) {
    attachCopyButtons(diagnosticsPanelElement);
  }
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

async function readDiagnosticsViewState(settings: AppSettings): Promise<DiagnosticsViewState> {
  try {
    const diagnostics = await getApiDebugState();
    return {
      diagnostics,
      tokenStatus: deriveTokenStatus(diagnostics),
      refreshedAt: new Date()
    };
  } catch (error) {
    return {
      diagnostics: fallbackDiagnostics(settings, userFacingError(error)),
      tokenStatus: "unreadable",
      refreshedAt: new Date(),
      error: userFacingError(error)
    };
  }
}

function deriveTokenStatus(diagnostics: BridgeDiagnostics): TokenStatus {
  const startupError = diagnostics.startupError?.toLowerCase() ?? "";
  if (
    startupError.includes("missing") ||
    startupError.includes("not found") ||
    startupError.includes("no such file")
  ) {
    return "missing";
  }
  if (startupError.includes("token") || startupError.includes("permission")) {
    return "unreadable";
  }
  return "configured";
}

function fallbackDiagnostics(settings: AppSettings, error: string): BridgeDiagnostics {
  return {
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
    startupError: error
  };
}

function userFacingError(error: unknown) {
  if (error instanceof Error && error.message) {
    return error.message;
  }
  if (typeof error === "string" && error) {
    return error;
  }
  return "Unable to load diagnostics.";
}

function apiDebugSummary(state: DiagnosticsViewState) {
  if (state.error) {
    return `Diagnostics refresh failed: ${state.error}`;
  }
  const diagnostics = state.diagnostics;
  return `API ${diagnostics.enabled ? "enabled" : "disabled"}; ${diagnostics.listenAddress}; queue ${diagnostics.queueLength}/${diagnostics.queueCapacity}; token ${tokenStatusLabel(state.tokenStatus)}.`;
}

function diagnosticsPanel(viewState: DiagnosticsViewState) {
  const state = viewState.diagnostics;
  return `
    ${viewState.error ? `<p class="diagnostics-error">${escapeHtml(viewState.error)}</p>` : ""}
    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>Runtime health</h3>
        <p>Last refresh: ${escapeHtml(formatDate(viewState.refreshedAt))}</p>
      </div>
      <dl class="diagnostics-grid">
        <div><dt>API enabled</dt><dd>${state.enabled ? "yes" : "no"}</dd></div>
        <div><dt>Listen address</dt><dd>${escapeHtml(state.listenAddress)}</dd></div>
        <div><dt>Queue</dt><dd>${state.queueLength}/${state.queueCapacity}</dd></div>
        <div><dt>Hardware light</dt><dd>${state.hardwareLight ? "enabled" : "disabled"}</dd></div>
        <div><dt>Token status</dt><dd>${tokenStatusLabel(viewState.tokenStatus)}</dd></div>
        <div><dt>Startup</dt><dd>${state.startupError ? escapeHtml(state.startupError) : "ok"}</dd></div>
      </dl>
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>Sound</h3>
        <p>No file paths or bundle paths are exposed.</p>
      </div>
      <dl class="diagnostics-grid">
        <div><dt>Playback available</dt><dd>${state.sound.playbackAvailable ? "yes" : "no"}</dd></div>
        <div><dt>Muted</dt><dd>${state.sound.muted ? "yes" : "no"}</dd></div>
        <div><dt>Cooldown</dt><dd>${state.sound.cooldownMs}ms</dd></div>
        <div class="diagnostics-wide"><dt>Accepted IDs</dt><dd>${state.sound.acceptedIds.map(escapeHtml).join(", ")}</dd></div>
      </dl>
      ${soundDecisionBlock(state.sound.lastDecision)}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>Recent accepted events</h3>
        <p>Shows summaries only. Raw payload and metadata are not stored here.</p>
      </div>
      ${eventTable(state.acceptedEvents, "accepted")}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>Recent rejected events</h3>
        <p>Invalid payload bodies are not displayed.</p>
      </div>
      ${eventTable(state.rejectedEvents, "rejected")}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>Quick commands</h3>
        <p>Copy-only examples. The settings window never executes commands.</p>
      </div>
      <div class="quick-command-list">
        ${quickCommand("Health", "curl http://127.0.0.1:17321/api/health")}
        ${quickCommand("Capabilities", "curl http://127.0.0.1:17321/api/capabilities")}
        ${quickCommand("petctl success", "petctl notify --level success --title \"测试通过\" --sound success_chime")}
        ${quickCommand("Shell wrapper", "examples/shell/task-with-pet.sh -- pnpm test")}
        ${quickCommand("Node example", "node examples/node/notify-pet.mjs success")}
      </div>
    </section>
  `;
}

function soundDecisionBlock(decision: BridgeDiagnostics["sound"]["lastDecision"]) {
  if (!decision) {
    return `<p class="diagnostics-empty">暂无声音决策</p>`;
  }
  return `
    <dl class="diagnostics-grid sound-decision-grid">
      <div><dt>Last sound</dt><dd>${escapeHtml(decision.sound)}</dd></div>
      <div><dt>Played</dt><dd>${decision.played ? "yes" : "no"}</dd></div>
      <div><dt>Reason</dt><dd>${escapeHtml(decision.reason)}</dd></div>
      <div><dt>Decided at</dt><dd>${escapeHtml(formatTimestamp(decision.decidedAt))}</dd></div>
    </dl>
  `;
}

function eventTable(events: ApiEventSummary[], kind: "accepted" | "rejected") {
  if (events.length === 0) {
    return `<p class="diagnostics-empty">No ${kind} events yet.</p>`;
  }
  const rows = events.slice(0, 10).map((event) => {
    if (kind === "accepted") {
      return `
        <tr>
          <td>${escapeHtml(formatTimestamp(event.receivedAt))}</td>
          <td>${escapeHtml(event.sourceId ?? "unknown")}</td>
          <td>${escapeHtml(event.level ?? "")}</td>
          <td>${escapeHtml(event.titlePreview ?? "")}</td>
          <td>${escapeHtml(event.messagePreview ?? "")}</td>
          <td>${event.status}</td>
        </tr>
      `;
    }
    return `
      <tr>
        <td>${escapeHtml(formatTimestamp(event.receivedAt))}</td>
        <td>${escapeHtml(event.sourceId ?? "unknown")}</td>
        <td>${escapeHtml(event.level ?? "")}</td>
        <td>${event.status}</td>
        <td>${escapeHtml(event.reasonCode ?? "")}</td>
        <td>${escapeHtml(event.reasonField ?? "")}</td>
        <td>${escapeHtml(event.reason ?? "")}</td>
      </tr>
    `;
  }).join("");

  return `
    <div class="diagnostics-table-wrap">
      <table class="diagnostics-table">
        <thead>
          ${kind === "accepted" ? `
            <tr><th>receivedAt</th><th>sourceId</th><th>level</th><th>titlePreview</th><th>messagePreview</th><th>status</th></tr>
          ` : `
            <tr><th>receivedAt</th><th>sourceId</th><th>level</th><th>status</th><th>reasonCode</th><th>reasonField</th><th>reason</th></tr>
          `}
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function quickCommand(label: string, command: string) {
  return `
    <div class="quick-command">
      <span>${escapeHtml(label)}</span>
      <code>${escapeHtml(command)}</code>
      <button class="copy-command" type="button" data-copy="${escapeHtml(command)}">Copy</button>
    </div>
  `;
}

function attachCopyButtons(root: ParentNode) {
  root.querySelectorAll<HTMLButtonElement>("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = button.dataset.copy ?? "";
      try {
        await navigator.clipboard.writeText(value);
        button.textContent = "Copied";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1000);
      } catch {
        button.textContent = "Copy failed";
        window.setTimeout(() => {
          button.textContent = "Copy";
        }, 1400);
      }
    });
  });
}

function tokenStatusLabel(status: TokenStatus) {
  const labels: Record<TokenStatus, string> = {
    configured: "configured",
    missing: "missing",
    unreadable: "unreadable"
  };
  return labels[status];
}

function formatDate(date: Date) {
  return date.toLocaleString(undefined, {
    hour12: false,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

function formatTimestamp(value: string) {
  const millis = Number(value);
  if (!Number.isFinite(millis) || millis <= 0) {
    return value;
  }
  return new Date(millis).toLocaleTimeString(undefined, {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
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
