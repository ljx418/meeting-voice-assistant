/* global fetch, WebSocket, setTimeout */
import { Buffer } from 'node:buffer';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V15_E2E_PREFIX ?? `rn-v15-e2e-${Date.now()}`;
const materialDir =
  process.env.RN_V15_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V15_DIGITAL_HUMAN_PDF ??
  join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9245);
const timestamp = Date.now();
const userDataDir = join('/private/tmp', `rn-v15-e2e-profile-${timestamp}`);
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'v1_5_e_chromecli_manual_e2e', String(timestamp));
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_5', 'chromecli-manual-e2e');
const chromePath = resolveChromiumPath();
const headless = process.env.RN_V15_E2E_HEADLESS !== '0';
const providerRetryDelayMs = Number(process.env.RN_V15_E2E_PROVIDER_RETRY_DELAY_MS ?? 2_500);
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];

const results = [];
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const screenshots = [];
const fixtures = {};
let chromeProcess;
let cdp;
let workspaceId = '';
let finalDecision = 'FAIL';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
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

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitFor(fn, label, timeoutMs = 60_000) {
  const started = Date.now();
  let lastError;
  while (Date.now() - started < timeoutMs) {
    try {
      const value = await fn();
      if (value) return value;
    } catch (error) {
      lastError = error;
    }
    await delay(300);
  }
  throw new Error(`${label} timed out${lastError ? `: ${lastError.message}` : ''}`);
}

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
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

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const output = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (
        lowered.includes('api_key') ||
        lowered.includes('authorization') ||
        lowered === 'path' ||
        lowered.endsWith('_path') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack')
      ) {
        continue;
      }
      output[key] = sanitize(item);
    }
    return output;
  }
  if (typeof value === 'string') {
    return value
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]')
      .replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]')
      .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]')
      .replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), `${JSON.stringify(sanitize(payload), null, 2)}\n`);
}

async function screenshot(name) {
  await mkdir(artifactsDir, { recursive: true });
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const fileName = `${name}.png`;
  await writeFile(join(artifactsDir, fileName), Buffer.from(result.data, 'base64'));
  screenshots.push(join('.smoke-artifacts', 'v1_5_e_chromecli_manual_e2e', String(timestamp), fileName));
}

async function seedWorkspace() {
  const md = await readFile(join(materialDir, '01_industry_overview.md'), 'utf8');
  const tech = await readFile(join(materialDir, '02_technology_trends.md'), 'utf8');
  const pdfBase64 = (await readFile(realPdfPath)).toString('base64');
  const created = await request('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.5-e2e', tags: ['v1.5', 'chromecli-e2e'] }
  });
  workspaceId = dataOf(created)?.workspace?.workspace_id ?? created.workspace_id;
  if (!workspaceId) throw new Error('workspace_id missing');
  fixtures['workspace-create.json'] = created;

  const mdImport = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { texts: [{ title: 'AI 数字人行业概览 Markdown', content: md, metadata: { source_format: 'markdown' } }] }
  });
  const techImport = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { texts: [{ title: 'AI 数字人技术趋势 Markdown', content: tech, metadata: { source_format: 'markdown' } }] }
  });
  const pdfImport = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      metadata: { title: 'AI 数字人产业发展报告 PDF', source_type: 'pdf', file_name: basename(realPdfPath) },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: pdfBase64,
          metadata: { file_name: basename(realPdfPath) }
        }
      ]
    }
  });
  fixtures['markdown-import.json'] = mdImport;
  fixtures['technology-markdown-import.json'] = techImport;
  fixtures['pdf-import.json'] = pdfImport;

  const build = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, { method: 'POST', body: {} });
  const operationId = dataOf(build)?.operation_id ?? build.operation_id;
  if (operationId) {
    await waitFor(async () => {
      const latest = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
      const status = dataOf(latest)?.operation?.status ?? dataOf(latest)?.status;
      if (status === 'completed') return latest;
      if (['failed', 'blocked', 'cancelled'].includes(status)) throw new Error(`build ${status}`);
      return null;
    }, 'workspace build');
  }
  mark('seed workspace/source/build', 'pass', workspaceId);
}

function assertChromeAvailable() {
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error('Chrome/Chromium executable not found. Set RN_CHROMIUM_PATH to a local executable.');
  }
}

function startChrome() {
  const args = [
    `--remote-debugging-port=${chromePort}`,
    `--user-data-dir=${userDataDir}`,
    '--window-size=1440,1000',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-background-networking',
    'about:blank'
  ];
  if (headless) args.splice(2, 0, '--headless=new', '--disable-gpu');
  chromeProcess = spawn(chromePath, args, { stdio: ['ignore', 'pipe', 'pipe'] });
  chromeProcess.stdout.on('data', (chunk) => process.stdout.write(chunk));
  chromeProcess.stderr.on('data', (chunk) => process.stderr.write(chunk));
}

async function getWebSocketUrl() {
  return waitFor(async () => {
    const response = await fetch(`http://127.0.0.1:${chromePort}/json/list`);
    const payload = await response.json();
    return payload.find((item) => item.type === 'page' && item.webSocketDebuggerUrl)?.webSocketDebuggerUrl;
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

async function evaluate(expression, awaitPromise = true) {
  const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed');
  return result.result.value;
}

async function textIncludes(text) {
  return evaluate(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function setQuestionAndSubmit(question) {
  const didSet = await evaluate(`(() => {
    const textarea = document.querySelector('.ask-form textarea');
    if (!textarea) return false;
    const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    setter.call(textarea, ${JSON.stringify(question)});
    if (textarea._valueTracker) textarea._valueTracker.setValue('');
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
    textarea.focus();
    return true;
  })()`);
  if (!didSet) throw new Error('question textarea not found');
  await waitFor(
    () =>
      evaluate(`(() => {
        const form = document.querySelector('.ask-form');
        const button = form && [...form.querySelectorAll('button')].find((el) => el.innerText.includes('发送问题') || el.innerText.includes('询问工作区'));
        const textarea = form && form.querySelector('textarea');
        return Boolean(textarea && textarea.value.trim() && button && !button.disabled);
      })()`),
    'query submit button enabled',
    10_000
  );
  await evaluate(`(() => {
    const form = document.querySelector('.ask-form');
    const button = form && [...form.querySelectorAll('button')].find((el) => el.innerText.includes('发送问题') || el.innerText.includes('询问工作区'));
    if (!button || button.disabled) return false;
    button.click();
    return true;
  })()`);
}

async function clickFirstJumpableCitation() {
  return evaluate(`(() => {
    const target = document.querySelector('[data-testid="jumpable-evidence-citation"]');
    if (!target) return false;
    target.click();
    return true;
  })()`);
}

async function runBrowserPath() {
  assertChromeAvailable();
  startChrome();
  const wsUrl = await getWebSocketUrl();
  cdp = createCdpClient(wsUrl);
  await cdp.waitOpen();
  cdp.on('Runtime.consoleAPICalled', (event) => {
    const text = (event.args ?? []).map((arg) => arg.value ?? arg.description ?? '').join(' ');
    if (event.type === 'error' && !knownWarningPatterns.some((pattern) => pattern.test(text))) consoleErrors.push(text);
  });
  cdp.on('Runtime.exceptionThrown', (event) => pageErrors.push(event.exceptionDetails?.text ?? 'page exception'));
  cdp.on('Network.requestWillBeSent', (event) => networkRequests.push(event.request?.url ?? ''));
  await cdp.send('Runtime.enable');
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');

  await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}` });
  await waitFor(() => textIncludes('资料导读'), 'workspace page loaded');
  await waitFor(
    () =>
      evaluate(`document.body && document.body.innerText.includes('概览') && !document.body.innerText.includes('正在生成资料导读')`),
    'AI Guide visible',
    120_000
  );
  await screenshot('01-guide');
  mark('browser guide visible', 'pass');

  await setQuestionAndSubmit('数字人 技术 趋势是什么？');
  await waitFor(() => textIncludes('回答'), 'answer visible', 90_000);
  await waitFor(() => textIncludes('可定位到原文片段'), 'jumpable citation visible', 90_000);
  await screenshot('02-qa-answer');
  mark('browser qa citation visible', 'pass');

  if (!(await clickFirstJumpableCitation())) throw new Error('jumpable citation button not found');
  await waitFor(() => evaluate(`Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'evidence highlight visible', 90_000);
  await screenshot('03-citation-highlight');
  mark('browser citation highlight', 'pass');

  const studioTools = ['笔记', '学习导读', '资料简报', '常见问题'];
  for (let index = 0; index < studioTools.length; index += 1) {
    await waitFor(
      () =>
        evaluate(`(() => {
          const cards = [...document.querySelectorAll('.studio-tool-list article')];
          const card = cards[${index}];
          const button = card && [...card.querySelectorAll('button')].find((item) => item.innerText.includes('生成'));
          return Boolean(button && !button.disabled);
        })()`),
      `Studio ${studioTools[index]} button enabled`,
      90_000
    );
    await evaluate(`(() => {
      const cards = [...document.querySelectorAll('.studio-tool-list article')];
      const card = cards[${index}];
      const button = card && [...card.querySelectorAll('button')].find((item) => item.innerText.includes('生成') && !item.disabled);
      if (!button) return false;
      button.click();
      return true;
    })()`);
    await waitFor(() => textIncludes(studioTools[index]), `Studio ${studioTools[index]} visible`, 90_000);
    await waitFor(() => textIncludes('可定位到原文片段'), `Studio ${studioTools[index]} citation visible`, 90_000);
    await screenshot(`04-studio-${index + 1}`);
    mark(`browser studio ${studioTools[index]}`, 'pass');
    await delay(providerRetryDelayMs);
  }

  await setQuestionAndSubmit('火星采矿 农业机械 海洋运输的结论是什么？');
  await waitFor(() => textIncludes('当前资料未覆盖'), 'source-grounded refusal visible', 90_000);
  await screenshot('05-refusal');
  mark('browser refusal visible', 'pass');
}

async function cleanup() {
  if (workspaceId) {
    try {
      const archived = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.5 chromecli manual e2e cleanup' }
      });
      fixtures['workspace-archive.json'] = archived;
      mark('cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  if (cdp) cdp.close();
  if (chromeProcess && !chromeProcess.killed) chromeProcess.kill('SIGTERM');
}

async function main() {
  try {
    await request('/api/workspaces');
    await fetch(appUrl);
    mark('startup', 'pass', `${appUrl} / ${baseUrl}`);
    await seedWorkspace();
    await runBrowserPath();
    const blockingConsoleErrors = consoleErrors.filter((text) => !knownWarningPatterns.some((pattern) => pattern.test(text)));
    if (blockingConsoleErrors.length || pageErrors.length) {
      throw new Error(`blocking browser errors: console=${blockingConsoleErrors.length}, page=${pageErrors.length}`);
    }
    if (networkRequests.some((url) => url.includes('/api/v1/knowledge'))) {
      throw new Error('browser requested /api/v1/knowledge');
    }
    finalDecision = 'PASS';
  } catch (error) {
    finalDecision = 'FAIL';
    mark('e2e exception', 'fail', error instanceof Error ? error.message : String(error));
  } finally {
    await cleanup();
    fixtures['v1_5_e_chromecli_manual_e2e_result.json'] = {
      generated_at: new Date().toISOString(),
      app_url: appUrl,
      base_url: baseUrl,
      workspace_id: workspaceId || null,
      browser: { chrome_path: chromePath ? 'configured' : 'missing', headless },
      screenshots,
      results,
      console_error_count: consoleErrors.length,
      page_error_count: pageErrors.length,
      blocked_network_request_count: networkRequests.filter((url) => url.includes('/api/v1/knowledge')).length,
      final_decision: finalDecision,
      declaration:
        finalDecision === 'PASS'
          ? 'V1.5-E ChromeCLI / manual E2E is pass for the AI digital human P0 dataset.'
          : 'V1.5-E ChromeCLI / manual E2E remains NOT_READY.'
    };
    await saveFixture('v1_5_e_chromecli_manual_e2e_result.json', fixtures['v1_5_e_chromecli_manual_e2e_result.json']);
    await Promise.all(
      Object.entries(fixtures)
        .filter(([name]) => name !== 'v1_5_e_chromecli_manual_e2e_result.json')
        .map(([name, payload]) => saveFixture(name, payload))
    );
  }
  if (finalDecision !== 'PASS') process.exitCode = 1;
}

await main();
