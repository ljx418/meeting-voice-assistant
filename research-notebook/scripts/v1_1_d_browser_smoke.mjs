/* global fetch, WebSocket, setTimeout */
import { Buffer } from 'node:buffer';
import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const timestamp = Date.now();
const prefix = process.env.RN_BROWSER_WORKSPACE_PREFIX ?? `rn-v11d-browser-${timestamp}`;
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_1_d_browser', String(timestamp));
const chromePath =
  process.env.RN_CHROMIUM_PATH ??
  '/Users/Zhuanz/Library/Caches/ms-playwright/chromium-1223/chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing';
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9223);
const userDataDir = join('/private/tmp', `rn-v11d-browser-profile-${timestamp}`);

const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];
let workspaceId = '';
let sourceId = '';
let unitId = '';
let evidenceId = '';
let chromeProcess;

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'not_ready' ? 'NOT_READY' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
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

async function cleanupWorkspace() {
  if (!workspaceId) return;
  try {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
    mark('cleanup archive workspace', 'pass', workspaceId);
  } catch (error) {
    mark('cleanup archive workspace', 'fail', error.message);
  }
}

function assertChromiumAvailable() {
  if (!existsSync(chromePath)) {
    throw new Error(`Chromium executable not found: ${chromePath}`);
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
  ], {
    stdio: ['ignore', 'pipe', 'pipe']
  });
  chromeProcess.stdout.on('data', (chunk) => process.stdout.write(chunk));
  chromeProcess.stderr.on('data', (chunk) => process.stderr.write(chunk));
}

async function getWebSocketUrl() {
  return waitFor(async () => {
    const response = await fetch(`http://127.0.0.1:${chromePort}/json/list`);
    const payload = await response.json();
    const page = payload.find((item) => item.type === 'page' && item.webSocketDebuggerUrl);
    return page?.webSocketDebuggerUrl;
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
    const handlers = listeners.get(message.method) ?? [];
    for (const handler of handlers) handler(message.params ?? {});
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
      return new Promise((resolve, reject) => {
        pending.set(messageId, { resolve, reject });
      });
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
  const result = await cdp.send('Runtime.evaluate', {
    expression,
    awaitPromise,
    returnByValue: true
  });
  if (result.exceptionDetails) {
    throw new Error(result.exceptionDetails.text ?? 'Runtime evaluation failed');
  }
  return result.result?.value;
}

async function setFieldInForm(cdp, formLabel, fieldIndex, value, fieldSelector = 'input, textarea') {
  return evalJs(
    cdp,
    `(() => {
      const form = [...document.querySelectorAll('form')].find((el) => el.getAttribute('aria-label') === ${JSON.stringify(formLabel)});
      if (!form) return false;
      const field = [...form.querySelectorAll(${JSON.stringify(fieldSelector)})][${fieldIndex}];
      if (!field) return false;
      const proto = field.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
      setter.call(field, ${JSON.stringify(value)});
      field.dispatchEvent(new Event('input', { bubbles: true }));
      field.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`
  );
}

async function submitForm(cdp, formLabel) {
  return evalJs(
    cdp,
    `(() => {
      const form = [...document.querySelectorAll('form')].find((el) => el.getAttribute('aria-label') === ${JSON.stringify(formLabel)});
      if (!form) return false;
      const button = form.querySelector('button[type="submit"]');
      if (!button || button.disabled) return false;
      button.click();
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
        bodyText: document.body.innerText,
        drawerOpen: Boolean(drawer),
        citationVisible: Boolean(citation),
        selectedUnitVisible: Boolean(selectedUnit),
        highlightText: highlight?.textContent || '',
        highlightInsideSelectedUnit: Boolean(highlight && selectedUnit && selectedUnit.contains(highlight)),
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
  try {
    await mkdir(artifactsDir, { recursive: true });
    assertChromiumAvailable();

  await request('/api/workspaces');
  mark('data_service target route probe', 'pass', dataServiceBaseUrl);

  startChrome();
  const wsUrl = await getWebSocketUrl();
  const cdp = createCdpClient(wsUrl);
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
  cdp.on('Network.requestWillBeSent', (params) => {
    networkRequests.push(params.request?.url ?? '');
  });

  await cdp.send('Page.navigate', { url: appUrl });
  await waitFor(() => textExists(cdp, 'Personal knowledge workspaces'), 'app home rendered');
  mark('browser opened app', 'pass', appUrl);

  const workspaceName = `${prefix}-workspace`;
  if (!(await setFieldInForm(cdp, 'Create workspace', 0, workspaceName))) throw new Error('could not set workspace name');
  if (!(await submitForm(cdp, 'Create workspace'))) throw new Error('could not submit workspace form');
  await waitFor(() => evalJs(cdp, `location.pathname.startsWith('/workspaces/')`), 'workspace route after create');
  await waitFor(() => textExists(cdp, 'Source Library'), 'workspace page rendered');
  workspaceId = await evalJs(cdp, `location.pathname.split('/').filter(Boolean)[1] || ''`);
  mark('workspace create and enter', 'pass', workspaceId);

  const sourceTitle = `${prefix} EvidenceSpan source`;
  const sourceContent =
    'Queues absorb burst traffic during release validation. EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.';
  if (!(await setFieldInForm(cdp, 'Import source', 0, sourceTitle))) throw new Error('could not set source title');
  if (!(await setFieldInForm(cdp, 'Import source', 1, 'text'))) throw new Error('could not set source type');
  if (!(await setFieldInForm(cdp, 'Import source', 2, sourceContent))) throw new Error('could not set source content');
  if (!(await submitForm(cdp, 'Import source'))) throw new Error('could not submit source form');
  await waitFor(
    () =>
      evalJs(
        cdp,
        `Boolean([...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(sourceTitle)})))`
      ),
    'source appears'
  );
  mark('source import visible', 'pass', sourceTitle);

  await waitFor(
    () =>
      evalJs(
        cdp,
        `(() => {
          const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(sourceTitle)}));
          const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Preview'));
          return Boolean(button && !button.disabled);
        })()`
      ),
    'source preview button enabled'
  );
  const previewClicked = await evalJs(
    cdp,
    `(() => {
      const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(sourceTitle)}));
      const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Preview'));
      if (!button) return false;
      button.click();
      return true;
    })()`
  );
  if (!previewClicked) throw new Error('could not click source preview');
  await waitFor(() => textExists(cdp, 'Source Preview'), 'source preview drawer opens');
  await waitFor(() => textExists(cdp, 'Document Units'), 'document units visible');
  mark('source preview opens', 'pass');

  await waitFor(
    () => evalJs(cdp, `Boolean(document.querySelector('[data-testid="document-units-outline"] button'))`),
    'document units outline loaded'
  );
  const firstUnitClicked = await evalJs(
    cdp,
    `(() => {
      const button = document.querySelector('[data-testid="document-units-outline"] button');
      if (!button) return false;
      button.click();
      return true;
    })()`
  );
  if (!firstUnitClicked) throw new Error('could not click first unit');
  await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="selected-document-unit"]'))`), 'selected unit visible');
  mark('unit navigation visible', 'pass');

  const question =
    'What should EvidenceSpan navigation highlight during release validation?';
  if (!(await setFieldInForm(cdp, '', 0, question, '.ask-form textarea'))) {
    await evalJs(
      cdp,
      `(() => {
        const field = document.querySelector('.ask-form textarea');
        if (!field) return false;
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(field, ${JSON.stringify(question)});
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
        return true;
      })()`
    );
  }
  const asked = await evalJs(
    cdp,
    `(() => {
      const button = [...document.querySelectorAll('.ask-form button')].find((el) => (el.textContent || '').includes('Ask workspace'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
  if (!asked) throw new Error('could not submit workspace question');
  await waitFor(() => textExists(cdp, 'Answer'), 'answer renders');
  await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="jumpable-evidence-citation"]'))`), 'jumpable citation visible');
  mark('workspace query jumpable citation visible', 'pass');

  const citationClicked = await evalJs(
    cdp,
    `(() => {
      const citation = document.querySelector('[data-testid="jumpable-evidence-citation"]');
      if (!citation) return false;
      citation.click();
      return true;
    })()`
  );
  if (!citationClicked) throw new Error('could not click jumpable citation');
  await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'highlight visible');
  const smokeState = await getSmokeState(cdp);
  if (!smokeState.highlightText.trim()) throw new Error('highlight text is empty');
  if (!smokeState.highlightInsideSelectedUnit) throw new Error('highlight is not inside selected unit detail');
  sourceId = smokeState.sourceIdText.match(/src_[a-z0-9]+/i)?.[0] ?? '';
  unitId = smokeState.unitText.match(/unit_[0-9a-f]{8,}/i)?.[0] ?? '';
  evidenceId = smokeState.evidenceText.match(/ev_[a-z0-9]+/i)?.[0] ?? '';
  mark('evidence highlight visible', 'pass', smokeState.highlightText.trim());

  const screenshotPath = await saveScreenshot(cdp, 'evidence-highlight.png');
  mark('screenshot saved', 'pass', screenshotPath);

  const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
  if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
  if (pageErrors.length || consoleErrors.length) {
    throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
  }
  mark('browser console/network guard', 'pass');

  await writeFile(
    join(artifactsDir, 'browser-smoke-result.json'),
    JSON.stringify(
      {
        appUrl,
        dataServiceBaseUrl,
        workspaceId,
        sourceId,
        unitId,
        evidenceId,
        highlightText: smokeState.highlightText.trim(),
        screenshotPath,
        consoleErrors,
        pageErrors,
        forbiddenKnowledgeRequests: forbiddenRequests,
        results
      },
      null,
      2
    ) + '\n'
  );

  cdp.close();
  } catch (error) {
    mark('v1.1-d browser smoke', 'fail', error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  } finally {
    await cleanupWorkspace();
    if (chromeProcess && !chromeProcess.killed) chromeProcess.kill('SIGTERM');
  }
}

await main();
