/* global fetch, WebSocket, setTimeout */
import { Buffer } from 'node:buffer';
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const folderRoot = process.env.RN_V13_FOLDER_ROOT ?? 'Desktop/技术分享';
const timestamp = Date.now();
const prefix = process.env.RN_V13_RC_WORKSPACE_PREFIX ?? `rn-v13-rc-agent-${timestamp}`;
const chromePath = resolveChromiumPath();
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9236);
const userDataDir = join('/private/tmp', `rn-v13-rc-agent-profile-${timestamp}`);
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_3_rc_agent_entry', String(timestamp));
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'agent-entry-acceptance');

const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];
let workspaceId = '';
let chromeProcess;
let finalDecision = 'BLOCKED';

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
  if (!response.ok) throw new Error(`HTTP ${response.status} ${path}`);
  return payload;
}

function dataOf(payload) {
  return payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

async function cleanupWorkspace() {
  if (!workspaceId) return;
  try {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
      method: 'POST',
      body: { reason: 'v1.3 rc agent entry browser cleanup' }
    });
    mark('cleanup archive workspace', 'pass', workspaceId);
  } catch (error) {
    mark('cleanup archive workspace', 'fail', error instanceof Error ? error.message : String(error));
  }
}

function assertChromiumAvailable() {
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error('Chrome/Chromium executable not found. Set RN_CHROMIUM_PATH to a local executable.');
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
  }, 'Chrome DevTools endpoint');
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

async function textExists(cdp, text) {
  return evalJs(cdp, `document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function setField(cdp, selector, value) {
  return evalJs(
    cdp,
    `(() => {
      const field = document.querySelector(${JSON.stringify(selector)});
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

async function clickButton(cdp, text) {
  return evalJs(
    cdp,
    `(() => {
      const button = [...document.querySelectorAll('button')].find((el) => (el.textContent || '').includes(${JSON.stringify(text)}));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), JSON.stringify(payload, null, 2) + '\n');
}

async function saveScreenshot(cdp, name) {
  await mkdir(artifactsDir, { recursive: true });
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const file = join(artifactsDir, name);
  await writeFile(file, Buffer.from(result.data, 'base64'));
  return file;
}

async function main() {
  let cdp;
  try {
    await request('/api/workspaces');
    mark('data_service probe', 'pass', dataServiceBaseUrl);
    const created = await request('/api/workspaces', { method: 'POST', body: { name: `${prefix}-workspace` } });
    workspaceId = dataOf(created)?.workspace?.workspace_id ?? created?.workspace_id;
    if (!workspaceId) throw new Error('workspace_id missing');
    mark('workspace create', 'pass', workspaceId);

    assertChromiumAvailable();
    startChrome();
    const wsUrl = await getWebSocketUrl();
    cdp = createCdpClient(wsUrl);
    await cdp.waitOpen();
    await cdp.send('Page.enable');
    await cdp.send('Runtime.enable');
    await cdp.send('Log.enable');
    await cdp.send('Network.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
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

    await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}` });
    await waitFor(() => textExists(cdp, '文件夹总结工作流'), 'folder summary workflow panel visible');
    mark('browser opened workspace Agent entry', 'pass', `${appUrl}/workspaces/${workspaceId}`);

    if (!(await setField(cdp, 'textarea[aria-label="任务指令"]', '递归总结 Desktop/技术分享，每个子文件夹生成一份总结。'))) {
      throw new Error('could not set agent goal');
    }
    if (!(await setField(cdp, 'input[aria-label="授权目录"]', folderRoot))) throw new Error('could not set authorized folder');
    if (!(await clickButton(cdp, '生成工作流草案'))) throw new Error('could not create workflow draft');
    await waitFor(() => textExists(cdp, '等待用户确认'), 'workflow draft awaiting confirmation');
    mark('workflow draft visible', 'pass');

    if (!(await clickButton(cdp, '确认并生成总结'))) throw new Error('could not run confirmed workflow');
    await waitFor(() => textExists(cdp, '总结产物'), 'summary artifacts panel visible', 90_000);
    await waitFor(() => textExists(cdp, '根目录总览'), 'root summary visible');
    mark('summary artifacts visible', 'pass');

    const openedDetails = await evalJs(
      cdp,
      `(() => {
        const details = [...document.querySelectorAll('details')].find((el) => (el.textContent || '').includes('根目录总览')) || document.querySelector('details');
        if (!details) return false;
        details.open = true;
        details.dispatchEvent(new ToggleEvent('toggle'));
        return true;
      })()`
    );
    if (!openedDetails) throw new Error('could not open summary details');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="summary-artifact-evidence-citation"]'))`), 'summary evidence citation visible');
    mark('summary evidence citation visible', 'pass');

    const citationClicked = await evalJs(
      cdp,
      `(() => {
        const button = document.querySelector('[data-testid="summary-artifact-evidence-citation"]');
        if (!button || button.disabled) return false;
        button.click();
        return true;
      })()`
    );
    if (!citationClicked) throw new Error('could not click summary evidence citation');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="source-preview-drawer"]'))`), 'source preview drawer visible');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="selected-document-unit"]'))`), 'selected unit visible');
    await waitFor(() => evalJs(cdp, `Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'evidence highlight visible');
    const state = await evalJs(
      cdp,
      `(() => ({
        highlightText: document.querySelector('[data-testid="evidence-highlight"]')?.textContent || '',
        citationCount: document.querySelectorAll('[data-testid="summary-artifact-evidence-citation"]').length,
        drawerVisible: Boolean(document.querySelector('[data-testid="source-preview-drawer"]')),
        selectedUnitVisible: Boolean(document.querySelector('[data-testid="selected-document-unit"]'))
      }))()`
    );
    if (!state.highlightText.trim()) throw new Error('highlight text is empty');
    mark('summary EvidenceSpan highlight visible', 'pass', state.highlightText.trim());

    const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
    if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
    if (pageErrors.length || consoleErrors.length) throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
    mark('browser console/network guard', 'pass');

    const screenshotPath = await saveScreenshot(cdp, 'agent-entry-summary-highlight.png');
    const screenshotArtifact = screenshotPath.split('/').slice(-3).join('/');
    mark('screenshot saved', 'pass', screenshotArtifact);
    finalDecision = 'PASS_LIMITED';
    await saveFixture('agent-entry-browser-result.json', {
      app_url: appUrl,
      data_service_base_url: dataServiceBaseUrl,
      workspace_id: workspaceId,
      folder_root_label: folderRoot,
      highlight_visible: true,
      highlight_text: state.highlightText.trim(),
      summary_citation_count: state.citationCount,
      screenshot_artifact: screenshotArtifact,
      final_decision: finalDecision,
      results
    });
  } catch (error) {
    finalDecision = 'BLOCKED';
    mark('v1.3 rc agent entry browser smoke', 'fail', error instanceof Error ? error.message : String(error));
    await saveFixture('agent-entry-browser-result.json', {
      workspace_id: workspaceId,
      final_decision: finalDecision,
      error: error instanceof Error ? error.message : String(error),
      results
    }).catch(() => undefined);
    process.exitCode = 1;
  } finally {
    if (cdp) cdp.close();
    await cleanupWorkspace();
    if (chromeProcess && !chromeProcess.killed) chromeProcess.kill('SIGTERM');
    console.log(`FINAL ${finalDecision}`);
  }
}

await main();
