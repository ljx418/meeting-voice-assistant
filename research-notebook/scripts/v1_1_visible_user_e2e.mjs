/* global fetch, WebSocket, setTimeout */

import { Buffer } from 'node:buffer';
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const timestamp = Date.now();
const prefix = process.env.RN_BROWSER_WORKSPACE_PREFIX ?? `rn-v11-visible-user-${timestamp}`;
const chromePath = resolveChromiumPath();
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9230);
const stepDelayMs = Number(process.env.RN_VISIBLE_E2E_STEP_DELAY_MS ?? 900);
const keepBrowserOpen = process.env.RN_VISIBLE_E2E_KEEP_BROWSER_OPEN !== '0';
const userDataDir = join('/private/tmp', `rn-v11-visible-user-e2e-profile-${timestamp}`);
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_1_visible_user_e2e', String(timestamp));
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_1', 'visible-user-e2e');

const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];
const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const screenshots = [];
const sourceResults = [];
let chromeProcess;
let workspaceId = '';
let sessionId = '';
let cdp;

const sourceCases = [
  {
    sourceType: 'text',
    title: `${prefix} Text Evidence Source`,
    content:
      'Visible user evidence navigation should keep the answer, source preview, document unit, and highlighted evidence span visible.',
    question: 'What should visible user evidence navigation keep visible?',
    anchor: 'answer, source preview'
  },
  {
    sourceType: 'markdown',
    title: `${prefix} Markdown Evidence Source`,
    content: '# Visible Markdown Evidence\n\nvisiblemarkdownanchor evidence should be highlighted from markdown source.',
    question: 'What should visiblemarkdownanchor evidence do?',
    anchor: 'visiblemarkdownanchor'
  },
  {
    sourceType: 'json',
    title: `${prefix} JSON Evidence Source`,
    content: JSON.stringify({ summary: 'visiblejsonanchor evidence should be highlighted from json source', status: 'supported' }),
    question: 'What should visiblejsonanchor evidence do?',
    anchor: 'visiblejsonanchor'
  }
];

const sessionContent =
  'Visible session precise navigation should preserve source id, unit id, and evidence id so a session answer can open a highlighted source span.';

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

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'not_ready' ? 'NOT_READY' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pause(label) {
  if (stepDelayMs > 0) await delay(stepDelayMs);
  if (label) console.log(`VIEW ${label}`);
}

async function waitFor(fn, label, timeoutMs = 45_000) {
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
  await writeFile(join(fixtureDir, name), `${JSON.stringify(sanitize(payload), null, 2)}\n`);
}

function assertChromeAvailable() {
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error(
      'Chrome executable not found. Set RN_CHROMIUM_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" or another local Chrome path.'
    );
  }
}

function startChrome() {
  chromeProcess = spawn(
    chromePath,
    [
      `--remote-debugging-port=${chromePort}`,
      `--user-data-dir=${userDataDir}`,
      '--window-size=1440,1000',
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-background-networking',
      'about:blank'
    ],
    { stdio: ['ignore', 'pipe', 'pipe'] }
  );
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

async function evalJs(expression, awaitPromise = true) {
  const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'Runtime evaluation failed');
  return result.result?.value;
}

async function setFieldInForm(formLabel, fieldIndex, value, fieldSelector = 'input, textarea') {
  return evalJs(
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

async function submitForm(formLabel) {
  return evalJs(
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

async function setTextareaByLabel(labelText, value) {
  return evalJs(
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

async function textExists(text) {
  return evalJs(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function clickButtonByText(text, rootSelector = 'body') {
  return evalJs(
    `(() => {
      const root = document.querySelector(${JSON.stringify(rootSelector)}) || document.body;
      const button = [...root.querySelectorAll('button, a')].find((el) => (el.textContent || '').includes(${JSON.stringify(text)}));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function closeDrawer() {
  await evalJs(
    `(() => {
      const drawer = document.querySelector('[data-testid="source-preview-drawer"], .trace-drawer');
      const button = drawer && [...drawer.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Close'));
      if (button) button.click();
      return true;
    })()`
  ).catch(() => false);
  await pause('close drawer');
}

async function importSource(sourceCase) {
  if (!(await setFieldInForm('Import source', 0, sourceCase.title))) throw new Error(`could not set ${sourceCase.sourceType} source title`);
  if (!(await setFieldInForm('Import source', 1, sourceCase.sourceType))) throw new Error(`could not set ${sourceCase.sourceType} source type`);
  if (!(await setFieldInForm('Import source', 2, sourceCase.content))) throw new Error(`could not set ${sourceCase.sourceType} source content`);
  await pause(`filled ${sourceCase.sourceType} source form`);
  if (!(await submitForm('Import source'))) throw new Error(`could not submit ${sourceCase.sourceType} source`);
  await waitFor(() => textExists(sourceCase.title), `${sourceCase.sourceType} source appears`);
  await pause(`${sourceCase.sourceType} source visible in Source Library`);
  mark(`${sourceCase.sourceType} source import visible`, 'pass', sourceCase.title);
}

async function clickPreviewForSource(title) {
  return evalJs(
    `(() => {
      const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(title)}));
      const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Preview'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function clickTraceForSource(title) {
  return evalJs(
    `(() => {
      const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(title)}));
      const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Trace'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function selectFirstUnit() {
  await waitFor(() => evalJs(`Boolean(document.querySelector('[data-testid="document-units-outline"] button'))`), 'document units outline loaded');
  const clicked = await evalJs(
    `(() => {
      const button = document.querySelector('[data-testid="document-units-outline"] button');
      if (!button) return false;
      button.click();
      return true;
    })()`
  );
  if (!clicked) throw new Error('could not click first unit');
  await waitFor(() => evalJs(`Boolean(document.querySelector('[data-testid="selected-document-unit"]'))`), 'selected unit visible');
}

async function askWorkspace(question) {
  await evalJs(
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
  await pause('filled workspace question');
  return clickButtonByText('Ask workspace', '.ask-form');
}

async function clickLatestJumpableCitation(anchor) {
  return evalJs(
    `(() => {
      const citations = [...document.querySelectorAll('[data-testid="jumpable-evidence-citation"]')];
      const citation = citations.reverse().find((el) => (el.textContent || '').includes(${JSON.stringify(anchor)})) || citations[0];
      if (!citation) return false;
      citation.click();
      return true;
    })()`
  );
}

async function getHighlightState() {
  return evalJs(
    `(() => {
      const highlight = document.querySelector('[data-testid="evidence-highlight"]');
      const drawer = document.querySelector('[data-testid="source-preview-drawer"]');
      const selectedUnit = document.querySelector('[data-testid="selected-document-unit"]');
      const sourceIdTexts = [...document.querySelectorAll('dt')]
        .filter((dt) => dt.textContent === 'source_id')
        .map((dt) => dt.nextElementSibling?.textContent || '')
        .filter(Boolean);
      const unitText = [...document.querySelectorAll('small, dd, span')].map((el) => el.textContent || '').find((text) => text.includes('unit_')) || '';
      const evidenceText = [...document.querySelectorAll('small, dd, span')].map((el) => el.textContent || '').find((text) => text.includes('ev_')) || '';
      return {
        drawerOpen: Boolean(drawer),
        selectedUnitVisible: Boolean(selectedUnit),
        highlightText: highlight?.textContent || '',
        highlightInsideSelectedUnit: Boolean(highlight && selectedUnit && selectedUnit.contains(highlight)),
        sourcePreviewVisible: document.body.innerText.includes('Source Preview'),
        sourceIdText: sourceIdTexts[sourceIdTexts.length - 1] || '',
        unitText,
        evidenceText
      };
    })()`
  );
}

async function saveScreenshot(name) {
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const file = join(artifactsDir, name);
  await writeFile(file, Buffer.from(result.data, 'base64'));
  screenshots.push(relative(process.cwd(), file));
  return file;
}

async function verifySourcePreviewUnitAndEvidence(sourceCase) {
  await waitFor(() => clickPreviewForSource(sourceCase.title), `${sourceCase.sourceType} preview button clickable`);
  await waitFor(() => textExists('Source Preview'), `${sourceCase.sourceType} drawer opens`);
  await waitFor(() => textExists('Document Units'), `${sourceCase.sourceType} units visible`);
  await pause(`${sourceCase.sourceType} Source Preview Drawer visible`);
  await selectFirstUnit();
  await pause(`${sourceCase.sourceType} DocumentUnit selected`);
  mark(`${sourceCase.sourceType} preview and unit visible`, 'pass');

  await closeDrawer();
  const citationCountBeforeAsk = await evalJs(`document.querySelectorAll('[data-testid="jumpable-evidence-citation"]').length`);
  if (!(await askWorkspace(sourceCase.question))) throw new Error(`could not ask ${sourceCase.sourceType} question`);
  await waitFor(
    () => evalJs(`document.querySelectorAll('[data-testid="jumpable-evidence-citation"]').length > ${Number(citationCountBeforeAsk)}`),
    `${sourceCase.sourceType} citation rendered`
  );
  await waitFor(() => clickLatestJumpableCitation(sourceCase.anchor), `${sourceCase.sourceType} citation clicked`);
  await waitFor(() => evalJs(`Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), `${sourceCase.sourceType} highlight visible`);
  await pause(`${sourceCase.sourceType} EvidenceSpan highlight visible`);
  const state = await getHighlightState();
  if (!state.highlightText.trim()) throw new Error(`${sourceCase.sourceType} highlight text is empty`);
  if (!state.highlightInsideSelectedUnit) throw new Error(`${sourceCase.sourceType} highlight is not inside selected unit detail`);
  const screenshot = await saveScreenshot(`${sourceCase.sourceType}-evidence-highlight.png`);
  const sourceId = state.sourceIdText.match(/src_[a-z0-9]+/i)?.[0] ?? '';
  const unitId = state.unitText.match(/unit_[0-9a-f]{8,}/i)?.[0] ?? '';
  const evidenceId = state.evidenceText.match(/ev_[a-z0-9]+/i)?.[0] ?? '';
  sourceResults.push({
    source_type: sourceCase.sourceType,
    source_id: sourceId,
    unit_id: unitId,
    evidence_id: evidenceId,
    highlight_text: state.highlightText.trim(),
    screenshot_artifact: relative(process.cwd(), screenshot)
  });
  mark(`${sourceCase.sourceType} evidence highlight visible`, 'pass', state.highlightText.trim());
  await closeDrawer();
}

async function verifySourceTrace(sourceCase) {
  await waitFor(() => clickTraceForSource(sourceCase.title), 'source trace button clickable');
  await waitFor(() => textExists('Source Trace'), 'source trace drawer opens');
  await waitFor(() => evalJs(`document.body.innerText.includes('Trace summary') || document.body.innerText.includes('Provenance')`), 'trace content visible');
  await pause('Source Trace drawer visible');
  await saveScreenshot('source-trace.png');
  mark('source trace drawer visible', 'pass', sourceCase.title);
  await closeDrawer();
}

async function runSessionPath() {
  await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}/workbench` });
  await waitFor(() => textExists('Session Workbench'), 'session workbench rendered');
  await pause('Session Workbench visible');

  const sessionTitle = `${prefix} Session`;
  if (!(await setFieldInForm('Create session', 0, sessionTitle))) throw new Error('could not set session title');
  await pause('filled session title');
  if (!(await submitForm('Create session'))) throw new Error('could not create session');
  await waitFor(() => textExists(sessionTitle), 'session visible');
  sessionId = await evalJs(
    `(() => {
      const text = document.body.innerText;
      const match = text.match(/session_[a-z0-9_:-]+/i);
      return match?.[0] || '';
    })()`
  );
  await pause('created and selected session');
  mark('session create visible', 'pass', sessionTitle);

  if (!(await setTextareaByLabel('snippet or context', sessionContent))) throw new Error('could not set session snippet');
  await pause('filled session snippet');
  if (!(await clickButtonByText('Ingest snippet'))) throw new Error('could not ingest session snippet');
  await waitFor(() => textExists('Needs build') || textExists('Ready') || textExists('Active'), 'session ingest reflected');
  mark('session ingest visible', 'pass');

  if (!(await clickButtonByText('Build session'))) throw new Error('could not start session build');
  await waitFor(() => textExists('Session build status: completed') || textExists('Ready'), 'session build completed', 60_000);
  await pause('session build completed');
  mark('session build visible', 'pass');

  const question = 'What identifiers should visible session precise navigation preserve?';
  if (!(await setTextareaByLabel('session question', question))) throw new Error('could not set session question');
  await pause('filled session question');
  if (!(await clickButtonByText('Ask session'))) throw new Error('could not ask session');
  await waitFor(() => textExists('Session Answer'), 'session answer renders');
  await waitFor(() => evalJs(`Boolean(document.querySelector('[data-testid="jumpable-evidence-citation"]'))`), 'session jumpable citation visible');
  await waitFor(() => clickLatestJumpableCitation(''), 'session citation clicked');
  await waitFor(() => evalJs(`Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'session highlight visible');
  await pause('session EvidenceSpan highlight visible');
  const state = await getHighlightState();
  if (!state.highlightText.trim()) throw new Error('session highlight text is empty');
  if (!state.highlightInsideSelectedUnit) throw new Error('session highlight is not inside selected unit detail');
  const screenshot = await saveScreenshot('session-evidence-highlight.png');
  mark('session evidence highlight visible', 'pass', state.highlightText.trim());
  await saveFixture('session-citation-result.json', {
    session_id: sessionId,
    highlight_text: state.highlightText.trim(),
    screenshot_artifact: relative(process.cwd(), screenshot)
  });
  await closeDrawer();
}

async function cleanupWorkspace() {
  if (!workspaceId) return;
  try {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
    mark('workspace archive cleanup', 'pass', workspaceId);
  } catch (error) {
    mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
  }
}

async function main() {
  try {
    await mkdir(artifactsDir, { recursive: true });
    await mkdir(fixtureDir, { recursive: true });
    assertChromeAvailable();
    await request('/api/workspaces');
    mark('data_service target route probe', 'pass', dataServiceBaseUrl);

    startChrome();
    const wsUrl = await getWebSocketUrl();
    cdp = createCdpClient(wsUrl);
    await cdp.waitOpen();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Log.enable');
    await cdp.send('Network.enable');

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

    await cdp.send('Page.navigate', { url: appUrl });
    await waitFor(() => textExists('Personal knowledge workspaces'), 'app home rendered');
    await pause('Home page visible');
    mark('visible Chrome opened app', 'pass', appUrl);

    const workspaceName = `${prefix} Workspace`;
    if (!(await setFieldInForm('Create workspace', 0, workspaceName))) throw new Error('could not set workspace name');
    await pause('filled workspace name');
    if (!(await submitForm('Create workspace'))) throw new Error('could not create workspace');
    await waitFor(() => evalJs(`location.pathname.startsWith('/workspaces/')`), 'workspace route after create');
    await waitFor(() => textExists('Source Library'), 'workspace page rendered');
    workspaceId = await evalJs(`location.pathname.split('/').filter(Boolean)[1] || ''`);
    await pause('Workspace page visible');
    mark('workspace create and enter', 'pass', workspaceId);

    for (const sourceCase of sourceCases) {
      await importSource(sourceCase);
      await verifySourcePreviewUnitAndEvidence(sourceCase);
    }

    await verifySourceTrace(sourceCases[0]);
    await runSessionPath();

    const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
    if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
    if (pageErrors.length || consoleErrors.length) {
      throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
    }
    mark('browser console/network guard', 'pass');

    const summary = {
      declaration: 'VISIBLE_USER_E2E_PASS',
      app_url: appUrl,
      data_service_base_url: dataServiceBaseUrl,
      workspace_id: workspaceId,
      session_id: sessionId,
      chrome_path: chromePath,
      keep_browser_open: keepBrowserOpen,
      source_results: sourceResults,
      screenshot_artifacts: screenshots,
      forbidden_knowledge_requests: forbiddenRequests,
      console_errors: consoleErrors,
      page_errors: pageErrors,
      results
    };
    await saveFixture('visible-user-e2e-summary.json', summary);
    await saveFixture('workspace-citation-result.json', sourceResults.find((item) => item.source_type === 'text') ?? {});
    await saveFixture('markdown-json-result.json', sourceResults.filter((item) => item.source_type === 'markdown' || item.source_type === 'json'));
    await saveFixture('source-trace-result.json', {
      source_trace_visible: true,
      screenshot_artifact: screenshots.find((item) => item.includes('source-trace'))
    });
    await writeFile(join(artifactsDir, 'visible-user-e2e-result.json'), `${JSON.stringify(summary, null, 2)}\n`);
    await writeFile(
      join(artifactsDir, 'console-network-summary.json'),
      `${JSON.stringify({ console_errors: consoleErrors, page_errors: pageErrors, network_requests: networkRequests }, null, 2)}\n`
    );

    console.log('V1_1_VISIBLE_USER_E2E_DECISION PASS');
  } catch (error) {
    mark('v1.1 visible user e2e', 'fail', error instanceof Error ? error.message : String(error));
    await saveFixture('visible-user-e2e-summary.json', {
      declaration: 'VISIBLE_USER_E2E_FAIL',
      workspace_id: workspaceId,
      session_id: sessionId,
      error: error instanceof Error ? error.message : String(error),
      results
    }).catch(() => undefined);
    process.exitCode = 1;
  } finally {
    await cleanupWorkspace();
    if (cdp && !keepBrowserOpen) cdp.close();
    if (chromeProcess && !chromeProcess.killed && !keepBrowserOpen) chromeProcess.kill('SIGTERM');
    if (keepBrowserOpen) {
      console.log(`VISIBLE_CHROME_LEFT_OPEN remote_debugging_port=${chromePort} profile=${userDataDir}`);
    }
  }
}

await main();
