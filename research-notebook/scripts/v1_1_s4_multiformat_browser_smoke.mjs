/* global fetch, WebSocket, setTimeout */

import { Buffer } from 'node:buffer';
import { mkdir, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const timestamp = Date.now();
const prefix = `rn-v11-s4-multiformat-${timestamp}`;
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_1_s4_multiformat', String(timestamp));
const fixturesDir = join(process.cwd(), 'fixtures/real/v1_1/multi-format-frontend');
const chromePath = resolveChromiumPath();
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9226);
const userDataDir = join('/private/tmp', `rn-v11-s4-browser-profile-${timestamp}`);

const candidates = [
  {
    sourceType: 'markdown',
    title: 'V1.1 S4 Markdown Browser Source',
    anchor: 's4markdownanchor',
    content: '# Markdown Browser Evidence\n\ns4markdownanchor evidence should be highlighted from markdown source.',
    question: 'What should s4markdownanchor evidence do?'
  },
  {
    sourceType: 'json',
    title: 'V1.1 S4 JSON Browser Source',
    anchor: 's4jsonanchor',
    content: JSON.stringify({ summary: 's4jsonanchor evidence should be highlighted from json source', status: 'supported' }),
    question: 'What should s4jsonanchor evidence do?'
  }
];

const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const candidateResults = [];
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];
let workspaceId = '';
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
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error('Chromium executable not found. Set RN_CHROMIUM_PATH or install Chrome/Chromium.');
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
  const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text ?? 'Runtime evaluation failed');
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

async function clickPreviewForSource(cdp, title) {
  return evalJs(
    cdp,
    `(() => {
      const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(title)}));
      const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Preview'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function closeDrawer(cdp) {
  await evalJs(
    cdp,
    `(() => {
      const drawer = document.querySelector('[data-testid="source-preview-drawer"]');
      const button = drawer && [...drawer.querySelectorAll('button')].find((el) => (el.textContent || '').includes('Close'));
      if (button) button.click();
      return true;
    })()`
  ).catch(() => false);
}

async function askWorkspace(cdp, question) {
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
  return evalJs(
    cdp,
    `(() => {
      const button = [...document.querySelectorAll('.ask-form button')].find((el) => (el.textContent || '').includes('Ask workspace'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function getSmokeState(cdp) {
  return evalJs(
    cdp,
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
        bodyText: document.body.innerText,
        drawerOpen: Boolean(drawer),
        selectedUnitVisible: Boolean(selectedUnit),
        highlightText: highlight?.textContent || '',
        highlightInsideSelectedUnit: Boolean(highlight && selectedUnit && selectedUnit.contains(highlight)),
        sourceIdText: sourceIdTexts[sourceIdTexts.length - 1] || '',
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

async function saveFixture(name, payload) {
  await mkdir(fixturesDir, { recursive: true });
  await writeFile(join(fixturesDir, name), `${JSON.stringify(payload, null, 2)}\n`);
}

async function main() {
  let cdp;
  try {
    await mkdir(artifactsDir, { recursive: true });
    await mkdir(fixturesDir, { recursive: true });
    assertChromiumAvailable();

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

    for (const candidate of candidates) {
      if (!(await setFieldInForm(cdp, 'Import source', 0, candidate.title))) throw new Error(`could not set ${candidate.sourceType} source title`);
      if (!(await setFieldInForm(cdp, 'Import source', 1, candidate.sourceType))) throw new Error(`could not set ${candidate.sourceType} source type`);
      if (!(await setFieldInForm(cdp, 'Import source', 2, candidate.content))) throw new Error(`could not set ${candidate.sourceType} source content`);
      if (!(await submitForm(cdp, 'Import source'))) throw new Error(`could not submit ${candidate.sourceType} source`);
      await waitFor(() => textExists(cdp, candidate.title), `${candidate.sourceType} source appears`);
      mark(`${candidate.sourceType} source import visible`, 'pass');

      await waitFor(() => clickPreviewForSource(cdp, candidate.title), `${candidate.sourceType} preview button clickable`);
      await waitFor(() => textExists(cdp, 'Source Preview'), `${candidate.sourceType} drawer opens`);
      await waitFor(() => textExists(cdp, 'Document Units'), `${candidate.sourceType} units visible`);
      await waitFor(
        () => evalJs(cdp, `Boolean(document.querySelector('[data-testid="document-units-outline"] button'))`),
        `${candidate.sourceType} unit outline loaded`
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
      if (!firstUnitClicked) throw new Error(`could not click ${candidate.sourceType} first unit`);
      await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="selected-document-unit"]'))`), `${candidate.sourceType} selected unit visible`);
      mark(`${candidate.sourceType} preview and unit visible`, 'pass');

      await closeDrawer(cdp);
      const citationCountBeforeAsk = await evalJs(cdp, `document.querySelectorAll('[data-testid="jumpable-evidence-citation"]').length`);
      if (!(await askWorkspace(cdp, candidate.question))) throw new Error(`could not ask ${candidate.sourceType} question`);
      await waitFor(
        () =>
          evalJs(
            cdp,
            `document.querySelectorAll('[data-testid="jumpable-evidence-citation"]').length > ${Number(citationCountBeforeAsk)}`
          ),
        `${candidate.sourceType} new citation rendered`
      );
      await waitFor(() => textExists(cdp, candidate.anchor), `${candidate.sourceType} answer/evidence rendered`);
      await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="jumpable-evidence-citation"]'))`), `${candidate.sourceType} citation visible`);
      const citationClicked = await evalJs(
        cdp,
        `(() => {
          const citations = [...document.querySelectorAll('[data-testid="jumpable-evidence-citation"]')];
          const citation = citations.find((el) => (el.textContent || '').includes(${JSON.stringify(candidate.anchor)}));
          if (!citation) return false;
          citation.click();
          return true;
        })()`
      );
      if (!citationClicked) throw new Error(`could not click ${candidate.sourceType} citation`);
      await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), `${candidate.sourceType} highlight visible`);
      const smokeState = await getSmokeState(cdp);
      if (!smokeState.highlightText.trim()) throw new Error(`${candidate.sourceType} highlight text is empty`);
      if (!smokeState.highlightInsideSelectedUnit) throw new Error(`${candidate.sourceType} highlight is not inside selected unit detail`);
      const sourceId = smokeState.sourceIdText.match(/src_[a-z0-9]+/i)?.[0] ?? '';
      const unitId = smokeState.unitText.match(/unit_[0-9a-f]{8,}/i)?.[0] ?? '';
      const evidenceId = smokeState.evidenceText.match(/ev_[a-z0-9]+/i)?.[0] ?? '';
      const screenshotPath = await saveScreenshot(cdp, `${candidate.sourceType}-highlight.png`);
      candidateResults.push({
        sourceType: candidate.sourceType,
        sourceId,
        unitId,
        evidenceId,
        highlightText: smokeState.highlightText.trim(),
        screenshotArtifact: screenshotPath.replace(process.cwd(), '<research-notebook>')
      });
      mark(`${candidate.sourceType} evidence highlight visible`, 'pass', smokeState.highlightText.trim());
      await closeDrawer(cdp);
    }

    const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
    if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
    if (pageErrors.length || consoleErrors.length) {
      throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
    }
    mark('browser console/network guard', 'pass');

    const summary = {
      appUrl,
      dataServiceBaseUrl,
      workspaceId,
      candidates: candidateResults,
      forbiddenKnowledgeRequests: forbiddenRequests,
      consoleErrors,
      pageErrors,
      declaration: 'S4_MARKDOWN_JSON_FRONTEND_BROWSER_SMOKE_READY',
      results
    };
    await saveFixture('s4-multiformat-browser-result.json', summary);
    await writeFile(join(artifactsDir, 'browser-smoke-result.json'), JSON.stringify(summary, null, 2) + '\n');
    console.log('S4_MULTI_FORMAT_FRONTEND_DECISION BROWSER_SMOKE_READY_MARKDOWN_JSON');
    cdp.close();
  } catch (error) {
    mark('v1.1-s4 multiformat browser smoke', 'fail', error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  } finally {
    await cleanupWorkspace();
    if (chromeProcess && !chromeProcess.killed) chromeProcess.kill('SIGTERM');
    if (cdp) cdp.close();
  }
}

await main();
