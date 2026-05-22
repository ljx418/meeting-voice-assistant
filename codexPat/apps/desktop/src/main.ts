import { invoke } from "@tauri-apps/api/core";
import { listen } from "@tauri-apps/api/event";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { CAT_STATE_CONFIG, CAT_STATE_ORDER, labelForState, type CatState } from "./pet-states";
import { CatStateMachine, catStateStorageKey, readStoredCatStateSnapshot, type CatStateSnapshot } from "./state-machine";
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

type PetInstance = {
  instanceId: string;
  sourceKind: string;
  sourceId: string;
  displayName: string;
  windowLabel: string;
  workspaceLabel?: string | null;
  workspaceHash?: string | null;
  position: WindowPosition;
  visible: boolean;
  currentState: string;
  catProfileId: string;
  createdAt: string;
  updatedAt: string;
  lastEventAt?: string | null;
  isDefault: boolean;
};

type PetInstanceLimits = {
  totalCount: number;
  softLimit: number;
  hardLimit: number;
  overSoftLimit: boolean;
  atHardLimit: boolean;
};

type PetInstanceListResult = {
  instances: PetInstance[];
  limits: PetInstanceLimits;
};

type CatProfile = {
  id: string;
  name: string;
  description?: string;
  cssClass: string;
  previewColor?: string;
  builtIn: true;
};

type ApiEventSummary = {
  id: string;
  sourceId?: string | null;
  level?: string | null;
  titlePreview?: string | null;
  messagePreview?: string | null;
  targetInstanceId?: string | null;
  targetWindowLabel?: string | null;
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
  targetInstanceId?: string | null;
  targetWindowLabel?: string | null;
};

const STATE_CLASS_NAMES = Object.values(CAT_STATE_CONFIG).map((config) => config.cssClass);
const DEFAULT_CAT_PROFILE_ID = "default-cat";
const INSTANCE_FEEDBACK_TIMEOUT_MS = 2400;
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

async function getCurrentPetInstance(): Promise<PetInstance> {
  return invoke<PetInstance>("get_current_pet_instance");
}

async function listPetInstances(): Promise<PetInstance[]> {
  return invoke<PetInstance[]>("list_pet_instances");
}

async function getPetInstanceListResult(): Promise<PetInstanceListResult> {
  const instances = await listPetInstances();
  return {
    instances,
    limits: derivePetInstanceLimits(instances)
  };
}

async function listCatProfiles(): Promise<CatProfile[]> {
  return invoke<CatProfile[]>("list_cat_profiles");
}

async function createPetInstance(displayName?: string): Promise<PetInstance> {
  return invoke<PetInstance>("create_pet_instance", { displayName });
}

async function renamePetInstance(instanceId: string, displayName: string): Promise<PetInstance> {
  return invoke<PetInstance>("rename_pet_instance", { instanceId, displayName });
}

async function setPetInstanceProfile(instanceId: string, catProfileId: string): Promise<PetInstance> {
  return invoke<PetInstance>("set_pet_instance_profile", { instanceId, catProfileId });
}

async function setPetInstanceVisible(instanceId: string, visible: boolean): Promise<PetInstance> {
  return invoke<PetInstance>("set_pet_instance_visible", { instanceId, visible });
}

async function resetPetInstancePosition(instanceId: string): Promise<PetInstance> {
  return invoke<PetInstance>("reset_pet_instance_position", { instanceId });
}

async function detachPetInstance(instanceId: string): Promise<PetInstance[]> {
  return invoke<PetInstance[]>("detach_pet_instance", { instanceId });
}

async function renderPet(settings: AppSettings) {
  let instance = await getCurrentPetInstance().catch(() => defaultPetInstance());
  const profiles = await listCatProfiles().catch(() => defaultCatProfiles());
  const profileClass = catProfileClass(instance.catProfileId, profiles);
  document.documentElement.classList.remove("settings-root");
  document.body.classList.add("pet-body");
  document.body.classList.remove("settings-body");
  appRoot.innerHTML = `
    <main class="pet-shell cat-state-idle ${escapeHtml(profileClass)}" aria-label="Agent Desktop Pet">
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
        <span class="pet-name-label">${escapeHtml(instance.displayName)}</span>
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

  const stateMachine = new CatStateMachine(catStateStorageKey(instance.instanceId));
  const shell = appRoot.querySelector<HTMLElement>(".pet-shell");
  const stateLabel = appRoot.querySelector<HTMLElement>("#pet-state-label");
  const queueLabel = appRoot.querySelector<HTMLElement>("#pet-queue-label");
  const nameLabel = appRoot.querySelector<HTMLElement>(".pet-name-label");

  stateMachine.subscribe((snapshot) => {
    updatePetStateUi(shell, stateLabel, queueLabel, snapshot);
  });

  listen<AcceptedPetEvent>("pet-event:accepted", (event) => {
    if (shouldAcceptPetEvent(instance, event.payload) && isCatState(event.payload.level)) {
      stateMachine.enqueue(event.payload.level, "pet_event");
    }
  }).catch((error) => console.error("failed to listen for pet events", error));

  listen<PetInstance>("pet-instance:updated", (event) => {
    if (event.payload.instanceId !== instance.instanceId) {
      return;
    }
    instance = event.payload;
    applyCatProfileClass(shell, instance.catProfileId, profiles);
    if (nameLabel) {
      nameLabel.textContent = instance.displayName;
    }
  }).catch((error) => console.error("failed to listen for pet instance updates", error));

  appRoot.querySelectorAll<HTMLButtonElement>("[data-state]").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      stateMachine.enqueue(button.dataset.state as CatState);
    });
  });

  const dragTarget = appRoot.querySelector<HTMLElement>(".pet-shell");
  dragTarget?.addEventListener("pointerdown", async (event) => {
    if (event.button !== 0) {
      return;
    }
    const target = event.target instanceof HTMLElement ? event.target : null;
    if (!target || target.closest(".debug-strip")) {
      return;
    }
    if (!target.closest(".pet-stage") && !target.closest(".pet-status")) {
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
  }, { capture: true });
}

async function renderSettings(settings: AppSettings) {
  document.documentElement.classList.add("settings-root");
  document.body.classList.add("settings-body");
  document.body.classList.remove("pet-body");
  const position = await getPetPosition().catch(() => ({ x: 0, y: 0 }));
  const stateSnapshot = readStoredCatStateSnapshot();
  const diagnosticsState = await readDiagnosticsViewState(settings);
  const instanceResult = await getPetInstanceListResult().catch(() => {
    const instances = [defaultPetInstance()];
    return {
      instances,
      limits: derivePetInstanceLimits(instances)
    };
  });
  const { instances, limits } = instanceResult;
  const profiles = await listCatProfiles().catch(() => defaultCatProfiles());

  appRoot.innerHTML = `
    <main class="settings-panel">
      <header class="settings-header">
        <div>
          <h1>Agent Desktop Pet 设置</h1>
          <p>本地桌宠、多实例和事件桥诊断面板</p>
        </div>
      </header>

      <section class="settings-section">
        <div>
          <h2>声音</h2>
          <p>静音状态会在下次启动时保留。</p>
        </div>
        <button class="primary-action" id="mute-toggle" type="button">
          ${settings.muted ? "取消静音" : "静音"}
        </button>
      </section>

      <section class="settings-section">
        <div>
          <h2>桌宠位置</h2>
          <p>当前主窗口位置：x=${Math.round(position.x)}，y=${Math.round(position.y)}</p>
        </div>
      </section>

      <section class="settings-section">
        <div>
          <h2>桌宠状态</h2>
          <p id="settings-state-summary">${settingsStateSummary(stateSnapshot)}</p>
        </div>
        <button class="secondary-action" id="state-refresh" type="button">刷新</button>
      </section>

      <section class="settings-section api-debug-section">
        <div>
          <h2>多猫管理</h2>
          <p>${instanceLimitSummary(limits)}</p>
          ${limits.overSoftLimit ? `<p class="instance-limit-warning">${limits.atHardLimit ? "已达到 12 只猫上限，请先移除不用的实例猫。" : "当前猫较多，建议移除不用的实例猫。"}</p>` : ""}
        </div>
        <button class="secondary-action" id="instance-create" type="button" ${limits.atHardLimit ? "disabled" : ""}>创建 Codex 猫</button>
      </section>

      <section class="instance-list" id="instance-list">
        ${instanceList(instances, profiles)}
      </section>

      <section class="settings-section api-debug-section">
        <div>
          <h2>诊断</h2>
          <p id="settings-api-summary">${apiDebugSummary(diagnosticsState)}</p>
        </div>
        <button class="secondary-action" id="api-refresh" type="button">刷新</button>
      </section>

      <section class="diagnostics-panel" id="diagnostics-panel">
        ${diagnosticsPanel(diagnosticsState)}
      </section>

      <section class="settings-section muted-section" aria-disabled="true">
        <div>
          <h2>猫咪大小</h2>
          <p>大小控制保留给后续阶段。</p>
        </div>
        <input type="range" min="80" max="140" value="100" disabled aria-label="猫咪大小占位控件" />
      </section>

      <section class="event-empty">
        <h2>事件日志</h2>
        <p>当前只保留最近接收和拒绝的 HTTP 事件摘要，暂不提供完整事件日志界面。</p>
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

  appRoot.querySelector<HTMLButtonElement>("#instance-create")?.addEventListener("click", async () => {
    const nextName = `Codex Cat ${Math.max(1, instances.length)}`;
    try {
      await createPetInstance(nextName);
      await renderSettings(await getSettings());
    } catch (error) {
      window.alert(userFacingCreateInstanceError(error));
    }
  });

  appRoot.querySelectorAll<HTMLButtonElement>("[data-instance-detach]").forEach((button) => {
    button.addEventListener("click", async () => {
      const instanceId = button.dataset.instanceDetach;
      if (!instanceId) {
        return;
      }
      if (button.dataset.confirmDetach !== "true") {
        button.dataset.confirmDetach = "true";
        button.textContent = "确认移除";
        button.classList.add("is-danger-confirm");
        window.setTimeout(() => {
          if (button.isConnected && button.dataset.confirmDetach === "true") {
            button.dataset.confirmDetach = "false";
            button.textContent = "移除";
            button.classList.remove("is-danger-confirm");
          }
        }, 3000);
        return;
      }
      button.setAttribute("disabled", "true");
      try {
        await detachPetInstance(instanceId);
        await renderSettings(await getSettings());
      } catch {
        button.removeAttribute("disabled");
        button.dataset.confirmDetach = "false";
        button.textContent = "移除";
        button.classList.remove("is-danger-confirm");
        setInstanceFeedback(instanceId, "移除失败。", "error");
      }
    });
  });

  appRoot.querySelectorAll<HTMLButtonElement>("[data-instance-visible]").forEach((button) => {
    button.addEventListener("click", async () => {
      const instanceId = button.dataset.instanceVisible;
      const visible = button.dataset.visibleNext === "true";
      if (!instanceId) {
        return;
      }
      button.setAttribute("disabled", "true");
      try {
        await setPetInstanceVisible(instanceId, visible);
        await renderSettings(await getSettings());
        setInstanceFeedback(instanceId, visible ? "已显示" : "已隐藏");
      } catch {
        button.removeAttribute("disabled");
        setInstanceFeedback(instanceId, visible ? "显示失败。" : "隐藏失败。", "error");
      }
    });
  });

  appRoot.querySelectorAll<HTMLSelectElement>("[data-instance-profile]").forEach((select) => {
    select.addEventListener("change", async () => {
      const instanceId = select.dataset.instanceProfile;
      const profileId = select.value;
      if (!instanceId) {
        return;
      }
      select.setAttribute("disabled", "true");
      try {
        await setPetInstanceProfile(instanceId, profileId);
        await renderSettings(await getSettings());
        setInstanceFeedback(instanceId, "外观已更新");
      } catch {
        select.removeAttribute("disabled");
        setInstanceFeedback(instanceId, "外观更新失败。", "error");
      }
    });
  });

  appRoot.querySelectorAll<HTMLButtonElement>("[data-instance-reset]").forEach((button) => {
    button.addEventListener("click", async () => {
      const instanceId = button.dataset.instanceReset;
      if (!instanceId) {
        return;
      }
      button.setAttribute("disabled", "true");
      try {
        await resetPetInstancePosition(instanceId);
        await renderSettings(await getSettings());
        setInstanceFeedback(instanceId, "已重置位置");
      } catch {
        button.removeAttribute("disabled");
        setInstanceFeedback(instanceId, "重置位置失败。", "error");
      }
    });
  });

  appRoot.querySelectorAll<HTMLButtonElement>("[data-instance-rename]").forEach((button) => {
    button.addEventListener("click", async () => {
      const instanceId = button.dataset.instanceRename;
      if (!instanceId) {
        return;
      }
      const input = appRoot.querySelector<HTMLInputElement>(`[data-instance-name-input="${cssEscape(instanceId)}"]`);
      const name = input?.value.trim() ?? "";
      if (!input) {
        setInstanceFeedback(instanceId, "重命名失败。", "error");
        return;
      }
      const validationError = displayNameValidationError(name);
      if (validationError) {
        setInstanceFeedback(instanceId, validationError, "error");
        input.focus();
        return;
      }
      button.setAttribute("disabled", "true");
      try {
        const updated = await renamePetInstance(instanceId, name);
        updateInstanceNameInSettings(updated);
        setInstanceFeedback(instanceId, "已重命名");
      } catch {
        setInstanceFeedback(instanceId, "重命名失败。", "error");
      } finally {
        button.removeAttribute("disabled");
      }
    });
  });

  const instanceListElement = appRoot.querySelector<HTMLElement>("#instance-list");
  if (instanceListElement) {
    attachCopyButtons(instanceListElement);
  }

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
    await renderPet(settings);
  }
}

function defaultPetInstance(): PetInstance {
  return {
    instanceId: "default",
    sourceKind: "system",
    sourceId: "default",
    displayName: "Agent Desktop Pet",
    windowLabel: "main",
    workspaceHash: null,
    workspaceLabel: null,
    position: { x: 0, y: 0 },
    visible: true,
    currentState: "idle",
    catProfileId: "default-cat",
    createdAt: "legacy",
    updatedAt: "legacy",
    lastEventAt: null,
    isDefault: true
  };
}

function derivePetInstanceLimits(instances: PetInstance[]): PetInstanceLimits {
  const totalCount = instances.length;
  const softLimit = 6;
  const hardLimit = 12;
  return {
    totalCount,
    softLimit,
    hardLimit,
    overSoftLimit: totalCount >= softLimit,
    atHardLimit: totalCount >= hardLimit
  };
}

function instanceLimitSummary(limits: PetInstanceLimits) {
  const base = `管理本机桌面猫实例。当前 ${limits.totalCount}/${limits.hardLimit} 只；建议上限 ${limits.softLimit} 只。复制按钮只复制文本，本面板不会执行命令。`;
  if (limits.atHardLimit) {
    return `${base} 已达到 12 只猫上限，请先移除不用的实例猫。`;
  }
  return base;
}

function userFacingCreateInstanceError(error: unknown) {
  const value = userFacingError(error);
  if (value.includes("instance_limit_reached")) {
    return "已达到桌宠数量上限。请先移除不使用的猫，再创建新的猫。";
  }
  return value;
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
  const locked = snapshot.locked ? "，锁定中" : "";
  const dragging = snapshot.dragging ? "，拖拽中" : "";
  return `当前桌宠状态：${labelForState(snapshot.current)}；行为队列：${snapshot.queueLength}${locked}${dragging}。`;
}

function instanceList(instances: PetInstance[], profiles: CatProfile[]) {
  if (instances.length === 0) {
    return `<p class="diagnostics-empty">暂无桌宠实例。</p>`;
  }

  return `
    <div class="instance-list-grid">
      ${instances.map((instance) => `
        <article class="instance-card" data-instance-card="${escapeHtml(instance.instanceId)}">
          <div class="instance-card-main">
            <div class="instance-card-heading">
              <h3 data-instance-title="${escapeHtml(instance.instanceId)}">${escapeHtml(instance.displayName)}</h3>
              <span class="instance-badge">${instance.isDefault ? "默认猫 / 旧路由" : "Codex 实例猫 / 实例路由"}</span>
              <span class="instance-badge ${instance.visible ? "is-visible" : "is-hidden"}">${instance.visible ? "可见" : "已隐藏"}</span>
            </div>
            <dl class="instance-meta-grid">
              <div><dt>实例 ID</dt><dd>${escapeHtml(instance.instanceId)}</dd></div>
              <div><dt>窗口标签</dt><dd>${escapeHtml(instance.windowLabel)}</dd></div>
              <div><dt>当前状态</dt><dd>${escapeHtml(instanceStateLabel(instance.currentState))}</dd></div>
              <div><dt>外观</dt><dd>${escapeHtml(catProfileName(instance.catProfileId, profiles))}</dd></div>
              <div><dt>路由</dt><dd>${instance.isDefault ? "旧路由" : "实例路由"}</dd></div>
              <div><dt>最近事件</dt><dd>${escapeHtml(instance.lastEventAt ? formatTimestamp(instance.lastEventAt) : "暂无")}</dd></div>
            </dl>
            <label class="appearance-control">
              <span>外观</span>
              <select data-instance-profile="${escapeHtml(instance.instanceId)}" aria-label="${escapeHtml(instance.displayName)} 的外观">
                ${profiles.map((profile) => `
                  <option value="${escapeHtml(profile.id)}" ${normalizeCatProfileId(instance.catProfileId, profiles) === profile.id ? "selected" : ""}>
                    ${escapeHtml(profile.name)}
                  </option>
                `).join("")}
              </select>
            </label>
            ${instance.isDefault ? "" : `
              <label class="instance-name-control">
                <span>名称</span>
                <input
                  type="text"
                  value="${escapeHtml(instance.displayName)}"
                  maxlength="40"
                  data-instance-name-input="${escapeHtml(instance.instanceId)}"
                  aria-label="${escapeHtml(instance.displayName)} 的名称"
                />
              </label>
            `}
            <div class="instance-command-list">
              ${quickCommand("环境变量", `export AGENT_DESKTOP_PET_INSTANCE_ID=${instance.instanceId}`, "复制环境变量")}
              ${quickCommand("通知命令", `node packages/petctl/dist/cli.js notify --instance ${instance.instanceId} --level success --title "Codex success"`, "复制通知命令")}
            </div>
            <p class="instance-feedback" data-instance-feedback="${escapeHtml(instance.instanceId)}" aria-live="polite"></p>
          </div>
          <div class="instance-card-actions">
            <button class="secondary-action" type="button" data-instance-visible="${escapeHtml(instance.instanceId)}" data-visible-next="${instance.visible ? "false" : "true"}">${instance.visible ? "隐藏" : "显示"}</button>
            <button class="secondary-action" type="button" data-instance-reset="${escapeHtml(instance.instanceId)}">重置位置</button>
            ${instance.isDefault ? `
              <button class="secondary-action" type="button" disabled title="默认猫不可移除">默认猫不可移除</button>
            ` : `
              <button class="secondary-action" type="button" data-instance-rename="${escapeHtml(instance.instanceId)}">重命名</button>
              <button class="secondary-action" type="button" data-instance-detach="${escapeHtml(instance.instanceId)}">移除</button>
            `}
          </div>
        </article>
      `).join("")}
    </div>
  `;
}

function updateInstanceNameInSettings(instance: PetInstance) {
  const selector = cssEscape(instance.instanceId);
  const title = appRoot.querySelector<HTMLElement>(`[data-instance-title="${selector}"]`);
  const input = appRoot.querySelector<HTMLInputElement>(`[data-instance-name-input="${selector}"]`);
  const profileSelect = appRoot.querySelector<HTMLSelectElement>(`[data-instance-profile="${selector}"]`);
  if (title) {
    title.textContent = instance.displayName;
  }
  if (input) {
    input.value = instance.displayName;
    input.setAttribute("aria-label", `${instance.displayName} 的名称`);
  }
  if (profileSelect) {
    profileSelect.setAttribute("aria-label", `${instance.displayName} 的外观`);
  }
}

function setInstanceFeedback(instanceId: string, message: string, tone: "success" | "error" = "success") {
  const selector = cssEscape(instanceId);
  const feedback = appRoot.querySelector<HTMLElement>(`[data-instance-feedback="${selector}"]`);
  if (!feedback) {
    return;
  }
  feedback.textContent = message;
  feedback.classList.remove("is-success", "is-error");
  feedback.classList.add(tone === "error" ? "is-error" : "is-success");
  window.setTimeout(() => {
    if (feedback.isConnected && feedback.textContent === message) {
      feedback.textContent = "";
      feedback.classList.remove("is-success", "is-error");
    }
  }, INSTANCE_FEEDBACK_TIMEOUT_MS);
}

function cssEscape(value: string) {
  if ("CSS" in window && typeof CSS.escape === "function") {
    return CSS.escape(value);
  }
  return value.replace(/["\\]/g, "\\$&");
}

function defaultCatProfiles(): CatProfile[] {
  return [
    {
      id: DEFAULT_CAT_PROFILE_ID,
      name: "默认猫",
      description: "沉稳的灰蓝开发者猫。",
      cssClass: "cat-profile-default-cat",
      previewColor: "#8d99a8",
      builtIn: true
    }
  ];
}

function normalizeCatProfileId(catProfileId: string, profiles: CatProfile[]) {
  return profiles.some((profile) => profile.id === catProfileId)
    ? catProfileId
    : DEFAULT_CAT_PROFILE_ID;
}

function catProfileName(catProfileId: string, profiles: CatProfile[]) {
  const normalized = normalizeCatProfileId(catProfileId, profiles);
  return profiles.find((profile) => profile.id === normalized)?.name ?? "默认猫";
}

function catProfileClass(catProfileId: string, profiles: CatProfile[]) {
  const normalized = normalizeCatProfileId(catProfileId, profiles);
  return profiles.find((profile) => profile.id === normalized)?.cssClass ?? "cat-profile-default-cat";
}

function applyCatProfileClass(shell: HTMLElement | null, catProfileId: string, profiles: CatProfile[]) {
  if (!shell) {
    return;
  }
  shell.classList.remove(...profiles.map((profile) => profile.cssClass));
  shell.classList.add(catProfileClass(catProfileId, profiles));
}

function isValidDisplayName(value: string) {
  const trimmed = value.trim();
  return trimmed.length >= 1
    && trimmed.length <= 40
    && !/[\u0000-\u001F\u007F/\\:]/.test(trimmed)
    && !/(https?:\/\/|file:\/\/)/i.test(trimmed);
}

function displayNameValidationError(value: string) {
  const trimmed = value.trim();
  if (trimmed.length < 1) {
    return "名称不能为空。";
  }
  if (trimmed.length > 40) {
    return "名称不能超过 40 个字符。";
  }
  if (!isValidDisplayName(trimmed)) {
    return "名称包含不支持的字符。";
  }
  return null;
}

function instanceStateLabel(state: string) {
  const labels: Record<CatState, string> = {
    idle: "空闲",
    thinking: "思考中",
    running: "执行中",
    success: "完成",
    warning: "注意",
    error: "失败",
    need_input: "需要确认",
    sleeping: "休息中"
  };
  return isCatState(state) ? labels[state] : state;
}

function shouldAcceptPetEvent(instance: PetInstance, event: AcceptedPetEvent) {
  if (instance.isDefault) {
    return !event.targetInstanceId || event.targetInstanceId === "default";
  }
  return event.targetInstanceId === instance.instanceId;
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
  return "无法加载诊断信息。";
}

function apiDebugSummary(state: DiagnosticsViewState) {
  if (state.error) {
    return `诊断刷新失败：${state.error}`;
  }
  const diagnostics = state.diagnostics;
  return `API ${diagnostics.enabled ? "已启用" : "已停用"}；${diagnostics.listenAddress}；队列 ${diagnostics.queueLength}/${diagnostics.queueCapacity}；token ${tokenStatusLabel(state.tokenStatus)}。`;
}

function diagnosticsPanel(viewState: DiagnosticsViewState) {
  const state = viewState.diagnostics;
  return `
    ${viewState.error ? `<p class="diagnostics-error">${escapeHtml(viewState.error)}</p>` : ""}
    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>运行健康</h3>
        <p>上次刷新：${escapeHtml(formatDate(viewState.refreshedAt))}</p>
      </div>
      <dl class="diagnostics-grid">
        <div><dt>API 启用</dt><dd>${state.enabled ? "是" : "否"}</dd></div>
        <div><dt>监听地址</dt><dd>${escapeHtml(state.listenAddress)}</dd></div>
        <div><dt>队列</dt><dd>${state.queueLength}/${state.queueCapacity}</dd></div>
        <div><dt>硬件灯</dt><dd>${state.hardwareLight ? "已启用" : "未启用"}</dd></div>
        <div><dt>Token 状态</dt><dd>${tokenStatusLabel(viewState.tokenStatus)}</dd></div>
        <div><dt>启动状态</dt><dd>${state.startupError ? escapeHtml(state.startupError) : "正常"}</dd></div>
      </dl>
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>声音</h3>
        <p>不会显示声音文件路径或 bundle 路径。</p>
      </div>
      <dl class="diagnostics-grid">
        <div><dt>可播放</dt><dd>${state.sound.playbackAvailable ? "是" : "否"}</dd></div>
        <div><dt>静音</dt><dd>${state.sound.muted ? "是" : "否"}</dd></div>
        <div><dt>冷却时间</dt><dd>${state.sound.cooldownMs}ms</dd></div>
        <div class="diagnostics-wide"><dt>允许的 ID</dt><dd>${state.sound.acceptedIds.map(escapeHtml).join(", ")}</dd></div>
      </dl>
      ${soundDecisionBlock(state.sound.lastDecision)}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>最近接收事件</h3>
        <p>这里只显示摘要，不保存原始 payload 和完整 metadata。</p>
      </div>
      ${eventTable(state.acceptedEvents, "accepted")}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>最近拒绝事件</h3>
        <p>不会显示非法 payload 原文。</p>
      </div>
      ${eventTable(state.rejectedEvents, "rejected")}
    </section>

    <section class="diagnostics-block">
      <div class="diagnostics-block-heading">
        <h3>快捷命令</h3>
        <p>仅提供复制示例，设置窗口不会执行命令。</p>
      </div>
      <div class="quick-command-list">
        ${quickCommand("健康检查", "curl http://127.0.0.1:17321/api/health")}
        ${quickCommand("能力列表", "curl http://127.0.0.1:17321/api/capabilities")}
        ${quickCommand("petctl success", "petctl notify --level success --title \"测试通过\" --sound success_chime")}
        ${quickCommand("Shell 示例", "examples/shell/task-with-pet.sh -- pnpm test")}
        ${quickCommand("Node 示例", "node examples/node/notify-pet.mjs success")}
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
      <div><dt>最近声音</dt><dd>${escapeHtml(decision.sound)}</dd></div>
      <div><dt>已播放</dt><dd>${decision.played ? "是" : "否"}</dd></div>
      <div><dt>原因</dt><dd>${escapeHtml(decision.reason)}</dd></div>
      <div><dt>决策时间</dt><dd>${escapeHtml(formatTimestamp(decision.decidedAt))}</dd></div>
    </dl>
  `;
}

function eventTable(events: ApiEventSummary[], kind: "accepted" | "rejected") {
  if (events.length === 0) {
    return `<p class="diagnostics-empty">暂无${kind === "accepted" ? "接收" : "拒绝"}事件。</p>`;
  }
  const rows = events.slice(0, 10).map((event) => {
    if (kind === "accepted") {
      return `
        <tr>
          <td>${escapeHtml(formatTimestamp(event.receivedAt))}</td>
          <td>${escapeHtml(event.sourceId ?? "未知")}</td>
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
        <td>${escapeHtml(event.sourceId ?? "未知")}</td>
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
            <tr><th>接收时间</th><th>来源</th><th>级别</th><th>标题摘要</th><th>消息摘要</th><th>状态码</th></tr>
          ` : `
            <tr><th>接收时间</th><th>来源</th><th>级别</th><th>状态码</th><th>原因码</th><th>字段</th><th>原因</th></tr>
          `}
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function quickCommand(label: string, command: string, copyLabel = "复制") {
  return `
    <div class="quick-command">
      <span>${escapeHtml(label)}</span>
      <code>${escapeHtml(command)}</code>
      <button class="copy-command" type="button" data-copy="${escapeHtml(command)}" data-copy-label="${escapeHtml(copyLabel)}">${escapeHtml(copyLabel)}</button>
    </div>
  `;
}

function attachCopyButtons(root: ParentNode) {
  root.querySelectorAll<HTMLButtonElement>("[data-copy]").forEach((button) => {
    button.addEventListener("click", async () => {
      const value = button.dataset.copy ?? "";
      const originalLabel = button.dataset.copyLabel ?? button.textContent ?? "复制";
      try {
        await navigator.clipboard.writeText(value);
        button.textContent = "已复制";
        window.setTimeout(() => {
          button.textContent = originalLabel;
        }, 1000);
      } catch {
        button.textContent = "复制失败";
        window.setTimeout(() => {
          button.textContent = originalLabel;
        }, 1400);
      }
    });
  });
}

function tokenStatusLabel(status: TokenStatus) {
  const labels: Record<TokenStatus, string> = {
    configured: "已配置",
    missing: "缺失",
    unreadable: "不可读取"
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
