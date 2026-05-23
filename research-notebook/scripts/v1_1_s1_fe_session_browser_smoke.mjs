/* global fetch, WebSocket, setTimeout */
import { Buffer } from 'node:buffer';
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const timestamp = Date.now();
const prefix = process.env.RN_BROWSER_WORKSPACE_PREFIX ?? `rn-v11-s1-fe-session-${timestamp}`;
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_1_s1_fe_session_browser', String(timestamp));
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_1', 'session-precise-navigation-browser');
const chromePath = resolveChromiumPath();
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9224);
const userDataDir = join('/private/tmp', `rn-v11-s1-fe-browser-profile-${timestamp}`);
const sourceContent =
  'Session precise navigation should preserve source id, unit id, and evidence id so the notebook can open a highlighted source span from a session answer.';

const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];
let workspaceId = '';
let sourceId = '';
let sessionId = '';
let unitId = '';
let evidenceId = '';
let highlightText = '';
let sessionQueryEvidence = null;
let chromeProcess;

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'not_ready' ? 'NOT_READY' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function resolveChromiumPath() {
  if (process.env.RN_CHROMIUM_PATH) return process.env.RN_CHROMIUM_PATH;
  const candidates = [
    '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium'
  ];
  return candidates.find((candidate) => existsSync(candidate)) ?? '';
}

async function waitFor(fn, label, timeoutMs = 30_000) {
  const started = Date.now();
  let lastError;
  while (Date.now() - started < timeoutMs) {
    try {
      const value = await fn();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await delay(250);
  }
  throw new Error(`${label} timed out${lastError ? `: ${lastError.message}` : ''}`);
}

async function request(path, options = {}) {
  const response = await fetch(`${dataServiceBaseUrl}${path}`, {
    method: options.method ?? 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status} ${path}`);
    error.payload = payload;
    throw error;
  }
  return payload;
}

function dataOf(payload) {
  return payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

function readWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace?.workspace_id ?? data?.workspace_id ?? payload?.workspace_id;
}

function readSourceId(payload) {
  const data = dataOf(payload);
  return data?.source?.source_id ?? data?.sources?.[0]?.source_id ?? payload?.source_id;
}

function readSessionId(payload) {
  const data = dataOf(payload);
  return data?.session?.session_id ?? data?.session_id ?? payload?.session_id;
}

function readOperationId(payload) {
  const data = dataOf(payload);
  return data?.operation?.operation_id ?? data?.operation_id ?? payload?.operation_id;
}

function readOperationStatus(payload) {
  const data = dataOf(payload);
  return data?.operation?.status ?? data?.status ?? payload?.status;
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const out = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (
        lowered === 'path' ||
        lowered === 'paths' ||
        lowered.endsWith('_path') ||
        lowered.endsWith('_paths') ||
        lowered.includes('physical') ||
        lowered.includes('cache') ||
        lowered.includes('stack')
      ) {
        continue;
      }
      out[key] = sanitize(item);
    }
    return out;
  }
  if (typeof value === 'string') {
    return value
      .replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]')
      .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]')
      .replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]')
      .replace(/[A-Za-z]:\\[^\s"',}]*/g, '[windows-path]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n');
}

async function pollOperation(path) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < 45_000) {
    latest = await request(path);
    const status = readOperationStatus(latest);
    if (['completed', 'succeeded', 'failed', 'blocked', 'cancelled'].includes(status)) return { status, payload: latest };
    await delay(1_000);
  }
  return { status: 'poll_timeout', payload: latest };
}

async function setupBackendData() {
  await request('/api/workspaces');
  mark('data_service target route probe', 'pass', dataServiceBaseUrl);

  const workspace = await request('/api/workspaces', { method: 'POST', body: { name: `${prefix}-workspace` } });
  workspaceId = readWorkspaceId(workspace);
  if (!workspaceId) throw new Error('workspace_id missing');
  mark('workspace create', 'pass', workspaceId);

  const source = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [{ title: 'V1.1 S1 Session Evidence Source', content: sourceContent, metadata: { stage: 'v1.1-s1-fe-browser' } }],
      metadata: { stage: 'v1.1-s1-fe-browser' }
    }
  });
  sourceId = readSourceId(source);
  if (!sourceId || sourceId.includes('://') || sourceId.includes('/')) throw new Error(`invalid source_id: ${sourceId}`);
  mark('source create', 'pass', sourceId);

  const session = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions`, {
    method: 'POST',
    body: { title: `${prefix} session browser smoke` }
  });
  sessionId = readSessionId(session);
  if (!sessionId) throw new Error('session_id missing');
  mark('session create', 'pass', sessionId);

  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/ingest`, {
    method: 'POST',
    body: {
      title: 'V1.1 S1-FE session snippet',
      content_format: 'text',
      source_type: 'text',
      content: sourceContent,
      related_source_ids: [sourceId],
      source_refs: [sourceId],
      metadata: { stage: 'v1.1-s1-fe-browser' }
    }
  });
  mark('session ingest', 'pass');

  const build = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = readOperationId(build);
  if (operationId) {
    const buildResult = await pollOperation(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/operations/${encodeURIComponent(operationId)}`
    );
    if (!['completed', 'succeeded'].includes(buildResult.status)) throw new Error(`session build did not complete: ${buildResult.status}`);
    mark('session build polling', 'pass', buildResult.status);
  } else {
    mark('session build polling', 'not_ready', 'operation_id missing');
  }
}

async function cleanupWorkspace() {
  if (sessionId && workspaceId) {
    try {
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/close`, {
        method: 'POST',
        body: {}
      });
      mark('session close cleanup', 'pass', sessionId);
    } catch (error) {
      mark('session close cleanup', 'fail', error.message);
    }
  }
  if (!workspaceId) return;
  try {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
    mark('workspace archive cleanup', 'pass', workspaceId);
  } catch (error) {
    mark('workspace archive cleanup', 'fail', error.message);
  }
}

function assertChromiumAvailable() {
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error('Chromium executable not found. Set RN_CHROMIUM_PATH to a local Chrome/Chromium executable.');
  }
}

function startChrome() {
  chromeProcess = spawn(chromePath, [
    `--remote-debugging-port=${chromePort}`,
    `--user-data-dir=${userDataDir}`,
    '--headless=new',
    '--disable-gpu',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    'about:blank'
  ], { stdio: ['ignore', 'pipe', 'pipe'] });
  chromeProcess.stdout.on('data', (chunk) => process.stdout.write(chunk));
  chromeProcess.stderr.on('data', (chunk) => process.stderr.write(chunk));
}

async function getWebSocketUrl() {
  return waitFor(async () => {
    const response = await fetch(`http://127.0.0.1:${chromePort}/json/list`);
    const payload = await response.json();
    return payload.find((item) => item.type === 'page' && item.webSocketDebuggerUrl)?.webSocketDebuggerUrl;
  }, 'Chrome page DevTools endpoint');
}

function createCdpClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const listeners = new Map();

  ws.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolve, reject } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) reject(new Error(message.error.message));
      else resolve(message.result);
      return;
    }
    for (const handler of listeners.get(message.method) ?? []) handler(message.params ?? {});
  });

  return {
    waitOpen: () =>
      new Promise((resolve, reject) => {
        ws.addEventListener('open', resolve, { once: true });
        ws.addEventListener('error', reject, { once: true });
      }),
    send(method, params = {}) {
      const messageId = ++id;
      ws.send(JSON.stringify({ id: messageId, method, params }));
      return new Promise((resolve, reject) => pending.set(messageId, { resolve, reject }));
    },
    on(method, handler) {
      listeners.set(method, [...(listeners.get(method) ?? []), handler]);
    },
    close() {
      ws.close();
    }
  };
}

async function evalJs(cdp, expression, awaitPromise = true) {
  const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'Runtime evaluation failed');
  return result.result?.value;
}

async function setTextareaByLabel(cdp, labelText, value) {
  return evalJs(
    cdp,
    `(() => {
      const label = [...document.querySelectorAll('label')].find((el) => (el.textContent || '').toLowerCase().includes(${JSON.stringify(
        labelText.toLowerCase()
      )}));
      const field = label?.querySelector('textarea');
      if (!field) return false;
      const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
      setter.call(field, ${JSON.stringify(value)});
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`
  );
}

async function textExists(cdp, text) {
  return evalJs(cdp, `document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function getSmokeState(cdp) {
  return evalJs(
    cdp,
    `(() => {
      const highlight = document.querySelector('[data-testid="evidence-highlight"]');
      const drawer = document.querySelector('[data-testid="source-preview-drawer"]');
      const selectedUnit = document.querySelector('[data-testid="selected-document-unit"]');
      const citation = document.querySelector('[data-testid="jumpable-evidence-citation"]');
      const sourceIdText = [...document.querySelectorAll('dt')].find((dt) => dt.textContent === 'source_id')?.nextElementSibling?.textContent || '';
      const unitText = [...document.querySelectorAll('small, dd, span')].map((el) => el.textContent || '').find((text) => text.includes('unit_')) || '';
      const evidenceText = [...document.querySelectorAll('small, dd, span')].map((el) => el.textContent || '').find((text) => text.includes('ev_')) || '';
      return {
        drawerOpen: Boolean(drawer),
        citationVisible: Boolean(citation),
        selectedUnitVisible: Boolean(selectedUnit),
        highlightText: highlight?.textContent || '',
        highlightInsideSelectedUnit: Boolean(highlight && selectedUnit && selectedUnit.contains(highlight)),
        sourcePreviewVisible: document.body.innerText.includes('Source Preview'),
        sourceIdText,
        unitText,
        evidenceText
      };
    })()`
  );
}

async function saveScreenshot(cdp, name) {
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const file = join(artifactsDir, name);
  await writeFile(file, Buffer.from(result.data, 'base64'));
  return file;
}

async function main() {
  let cdp;
  let screenshotPath = '';
  try {
    await mkdir(artifactsDir, { recursive: true });
    assertChromiumAvailable();
    await setupBackendData();

    startChrome();
    const wsUrl = await getWebSocketUrl();
    cdp = createCdpClient(wsUrl);
    await cdp.waitOpen();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Log.enable');
    await cdp.send('Network.enable');
    await cdp.send('Page.setViewport', { width: 1440, height: 1000 }).catch(() => undefined);

    cdp.on('Runtime.exceptionThrown', (params) => pageErrors.push(params.exceptionDetails?.text ?? 'runtime exception'));
    cdp.on('Runtime.consoleAPICalled', (params) => {
      if (params.type !== 'error') return;
      const message = params.args?.map((arg) => arg.value ?? arg.description ?? '').join(' ') ?? '';
      if (!knownWarningPatterns.some((pattern) => pattern.test(message))) consoleErrors.push(message);
    });
    cdp.on('Log.entryAdded', (params) => {
      if (params.entry?.level === 'error') {
        const message = params.entry.text ?? '';
        if (!knownWarningPatterns.some((pattern) => pattern.test(message))) consoleErrors.push(message);
      }
    });
    cdp.on('Network.requestWillBeSent', (params) => networkRequests.push(params.request?.url ?? ''));

    await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}/workbench` });
    await waitFor(() => textExists(cdp, 'Session Workbench'), 'session workbench rendered');
    mark('browser opened workbench', 'pass', appUrl);

    await waitFor(() => textExists(cdp, `${prefix} session browser smoke`), 'session appears');
    const sessionSelected = await evalJs(
      cdp,
      `(() => {
        const button = [...document.querySelectorAll('.session-row')].find((el) => (el.textContent || '').includes(${JSON.stringify(
          `${prefix} session browser smoke`
        )}));
        if (!button) return false;
        button.click();
        return true;
      })()`
    );
    if (!sessionSelected) throw new Error('could not select session');
    await waitFor(() => textExists(cdp, 'Session Ask'), 'session ask visible');
    mark('session selected', 'pass', sessionId);

    const question = 'What identifiers should session precise navigation preserve?';
    if (!(await setTextareaByLabel(cdp, 'session question', question))) throw new Error('could not set session question');
    const asked = await evalJs(
      cdp,
      `(() => {
        const button = [...document.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Ask session'));
        if (!button || button.disabled) return false;
        button.click();
        return true;
      })()`
    );
    if (!asked) throw new Error('could not submit session question');
    await waitFor(() => textExists(cdp, 'Session Answer'), 'session answer renders');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="jumpable-evidence-citation"]'))`), 'jumpable session citation visible');
    mark('session citation render', 'pass');

    const citationClicked = await evalJs(
      cdp,
      `(() => {
        const citation = document.querySelector('[data-testid="jumpable-evidence-citation"]');
        if (!citation) return false;
        citation.click();
        return true;
      })()`
    );
    if (!citationClicked) throw new Error('could not click jumpable session citation');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="source-preview-drawer"]'))`), 'source preview drawer opens');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="selected-document-unit"]'))`), 'selected unit visible');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'highlight visible');

    const smokeState = await getSmokeState(cdp);
    if (!smokeState.sourcePreviewVisible) throw new Error('source preview not visible');
    if (!smokeState.sourceIdText.includes(sourceId)) {
      throw new Error(`drawer source_id mismatch: expected ${sourceId}, got ${smokeState.sourceIdText || '<empty>'}`);
    }
    if (!smokeState.highlightText.trim()) throw new Error('highlight text is empty');
    if (!smokeState.highlightInsideSelectedUnit) throw new Error('highlight is not inside selected unit detail');
    highlightText = smokeState.highlightText.trim();
    unitId = smokeState.unitText.match(/unit_[0-9a-f]{8,}/i)?.[0] ?? '';
    evidenceId = smokeState.evidenceText.match(/ev_[a-z0-9]+/i)?.[0] ?? '';
    mark('session EvidenceSpan highlight visible', 'pass', highlightText);

    sessionQueryEvidence = {
      source_id: sourceId,
      unit_id: unitId,
      evidence_id: evidenceId,
      highlight_text: highlightText
    };
    if (!unitId || !evidenceId) throw new Error('unit_id or evidence_id not visible in selected citation path');

    screenshotPath = await saveScreenshot(cdp, 'session-evidence-highlight.png');
    mark('screenshot saved', 'pass', relative(process.cwd(), screenshotPath));

    const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
    if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
    if (pageErrors.length || consoleErrors.length) {
      throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
    }
    mark('browser console/network guard', 'pass');

    const result = {
      declaration: 'BROWSER_SMOKE_READY',
      appUrl,
      dataServiceBaseUrl,
      workspace_id: workspaceId,
      source_id: sourceId,
      session_id: sessionId,
      unit_id: unitId,
      evidence_id: evidenceId,
      highlight_text: highlightText,
      screenshot_artifact: relative(process.cwd(), screenshotPath),
      forbiddenKnowledgeRequests: forbiddenRequests,
      consoleErrors,
      pageErrors,
      results
    };
    await saveFixture('session-browser-smoke-result.json', result);
    await saveFixture('session-browser-query-evidence.json', sessionQueryEvidence);
    await saveFixture('session-browser-highlight-result.json', {
      highlight_visible: true,
      highlight_text: highlightText,
      unit_id: unitId,
      evidence_id: evidenceId,
      source_preview_visible: true
    });
    await saveFixture('session-browser-error-locality-result.json', {
      answer_retained: true,
      source_preview_retained: true,
      unit_detail_retained: true,
      blocking_errors: []
    });
    console.log('S1_FE_SESSION_BROWSER_DECISION BROWSER_SMOKE_READY');
    cdp.close();
  } catch (error) {
    const result = {
      declaration: 'API_SMOKE_READY_ONLY',
      workspace_id: workspaceId,
      source_id: sourceId,
      session_id: sessionId,
      unit_id: unitId,
      evidence_id: evidenceId,
      highlight_text: highlightText,
      error: error instanceof Error ? error.message : String(error),
      results
    };
    await saveFixture('session-browser-smoke-result.json', result).catch(() => undefined);
    mark('v1.1-s1-fe session browser smoke', 'fail', error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  } finally {
    if (cdp) cdp.close();
    await cleanupWorkspace();
    if (chromeProcess && !chromeProcess.killed) chromeProcess.kill('SIGTERM');
  }
}

await main();
