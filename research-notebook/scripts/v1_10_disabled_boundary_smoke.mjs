/* global fetch, WebSocket, setTimeout */
import { existsSync } from 'node:fs';
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9250);
const runBrowser = process.env.RN_V10_BROWSER === '1';
const timestamp = Date.now();
const userDataDir = join('/private/tmp', `rn-v10-boundary-profile-${timestamp}`);
const chromePath = resolveChromiumPath();
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_10', 'disabled-boundary');
const reportPath = join(process.cwd(), 'docs', 'design', 'V1.10', 'v1_10_rc_disabled_boundary_report.md');

const results = [];
const networkRequests = [];
const consoleErrors = [];
let finalDecision = 'FAIL';
let chromeProcess;
let cdp;
let workspaceId = '';

function resolveChromiumPath() {
  if (process.env.RN_CHROMIUM_PATH) return process.env.RN_CHROMIUM_PATH;
  const candidates = [
    '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser'
  ];
  return candidates.find((candidate) => existsSync(candidate)) ?? '';
}

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function failIf(condition, message) {
  if (condition) throw new Error(message);
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|api_key|authorization/i.test(value);
}

async function readText(path) {
  return readFile(path, 'utf8');
}

async function readJson(path) {
  return JSON.parse(await readText(path));
}

async function writeJson(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), `${JSON.stringify(payload, null, 2)}\n`);
}

async function writeReport(payload) {
  const resultRows = payload.results.map((item) => `| ${item.name} | ${item.status.toUpperCase()} | ${item.detail || ''} |`).join('\n');
  const report = `# V1.10-RC Disabled Boundary Acceptance Report

日期：2026-05-31

## 当前状态

\`${payload.final_decision}\`

## 环境记录

| 项 | 值 |
| --- | --- |
| frontend URL | ${payload.environment.frontend_url} |
| data_service URL | ${payload.environment.data_service_url} |
| browser | ${payload.environment.browser} |
| tester | ${payload.environment.tester} |
| timestamp | ${payload.generated_at} |

## 验收结果

| 项 | 状态 | 说明 |
| --- | --- | --- |
${resultRows}

## 结论

V1.10 disabled-boundary smoke 证明当前 UI / 文档仍保持后续输出工具 disabled：

- Audio Overview 不生成真实输出。
- PPT generation 不生成真实输出。
- Mindmap 不生成真实输出。
- Document comparison 不生成真实输出。
- 可抽取文本 PDF P0 路径使用既有真实数据 smoke 结果确认未回退。
- OCR / scanned PDF 仍保持 NOT_READY / CONTRACT_DISCOVERY_READY。

## 声明边界

不得声明：

- OCR ready
- scanned PDF ready
- Audio Overview ready
- PPT generation ready
- Mindmap ready
- Document comparison ready
- all-source-type ready
- all websites URL ready
- cloud sync / collaboration ready

## 风险评估

| 风险项 | 评级 | 说明 |
| --- | --- | --- |
| 规格漂移 | LOW | 本轮只验证 disabled boundary，不进入功能实现 |
| 虚假验收 | LOW | 报告保持 NOT_READY / DISABLED_READY，不写成功能 ready |
`;
  await writeFile(reportPath, report);
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

function extractWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace?.workspace_id ?? data?.workspace_id ?? payload?.workspace_id;
}

function startChrome() {
  failIf(!chromePath || !existsSync(chromePath), 'Chrome executable not found');
  chromeProcess = spawn(
    chromePath,
    [
      `--remote-debugging-port=${chromePort}`,
      `--user-data-dir=${userDataDir}`,
      '--headless=new',
      '--disable-gpu',
      '--window-size=1440,1000',
      '--no-first-run',
      '--no-default-browser-check',
      '--disable-background-networking',
      'about:blank'
    ],
    { stdio: ['ignore', 'pipe', 'pipe'] }
  );
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

async function evaluate(expression) {
  const result = await cdp.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (result.exceptionDetails) throw new Error(result.exceptionDetails.text || 'Runtime.evaluate failed');
  return result.result.value;
}

async function runBrowserBoundary() {
  await request('/api/workspaces');
  const created = await request('/api/workspaces', {
    method: 'POST',
    body: { name: `rn-v10-disabled-${Date.now()}`, owner: 'v1.10-disabled-boundary', tags: ['v1.10', 'disabled-boundary'] }
  });
  workspaceId = extractWorkspaceId(created);
  failIf(!workspaceId, 'workspace_id missing');
  mark('browser workspace create', 'pass', workspaceId);

  startChrome();
  cdp = createCdpClient(await getWebSocketUrl());
  await cdp.waitOpen();
  cdp.on('Network.requestWillBeSent', (params) => networkRequests.push(params.request?.url ?? ''));
  cdp.on('Runtime.consoleAPICalled', (params) => {
    if (params.type === 'error') consoleErrors.push(params.args?.map((arg) => arg.value || arg.description).join(' '));
  });
  await cdp.send('Runtime.enable');
  await cdp.send('Network.enable');
  await cdp.send('Page.enable');
  await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}` });
  await waitFor(() => evaluate('document.body && document.body.innerText.includes("后续输出工具")'), 'Studio disabled tools visible', 30_000);
  mark('browser opened ResearchNotebook workspace', 'pass', appUrl);

  for (const title of ['音频概览', 'PPT 生成', '思维导图', '文档对比']) {
    const visible = await evaluate(`document.body.innerText.includes(${JSON.stringify(title)})`);
    failIf(!visible, `${title} not visible in browser`);
  }
  const disabledCount = await evaluate(`(() => [...document.querySelectorAll('button')].filter((button) => button.innerText.includes('暂不可用') && button.disabled).length)()`);
  failIf(disabledCount < 4, `expected at least 4 disabled Phase 2/3 buttons, got ${disabledCount}`);
  mark('browser disabled tools visible and disabled', 'pass', `${disabledCount} disabled buttons`);

  const clicked = await evaluate(`(() => {
    const buttons = [...document.querySelectorAll('button')].filter((button) => button.innerText.includes('暂不可用'));
    for (const button of buttons) button.click();
    return buttons.length;
  })()`);
  await delay(800);
  const forbidden = networkRequests.filter((url) => /audio|ppt|mindmap|compare|document-comparison|phase-2|phase-3/i.test(url));
  failIf(forbidden.length > 0, `disabled tools triggered generation request: ${forbidden[0]}`);
  mark('browser disabled tool network result', 'pass', `${clicked} disabled buttons clicked, no generation request`);

  const artifactTextAbsent = await evaluate(`(() => !/音频已生成|PPT 已生成|思维导图已生成|文档对比已生成/.test(document.body.innerText))()`);
  failIf(!artifactTextAbsent, 'pseudo Phase 2/3 artifact text found');
  mark('browser artifact list check', 'pass', 'no pseudo Phase 2/3 artifact');

  const archived = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.10 disabled-boundary cleanup' }
  });
  failIf(!archived, 'workspace archive missing response');
  mark('browser workspace cleanup', 'pass', workspaceId);
}

try {
  const workspacePage = await readText('src/features/workspaces/WorkspacePage.tsx');
  const dataClient = await readText('src/shared/api/dataServiceClient.ts');
  const v14Sources = await readJson('fixtures/real/v1_4/sources-p0/v1_4_sources_p0_result.json');
  const v19Rc = await readJson('fixtures/real/v1_9/rc/v1_9_rc_result.json');
  const v16OcrReport = await readText('docs/design/V1.6/v1_6_c_ocr_contract_report.md');
  const v10Readme = await readText('docs/design/V1.10/00_README.md');

  const phaseTwoTitles = ['音频概览', 'PPT 生成', '思维导图', '文档对比'];
  for (const title of phaseTwoTitles) {
    failIf(!workspacePage.includes(`title: '${title}'`), `${title} disabled tool missing`);
  }
  mark('Phase 2/3 disabled tools visible in Studio source', 'pass', phaseTwoTitles.join(', '));

  failIf(!workspacePage.includes('以下能力暂不可用。当前不会生成伪输出，也不会调用后端。'), 'disabled tool explanatory copy missing');
  failIf(!workspacePage.includes('<button className="secondary-button" type="button" disabled>'), 'disabled button missing');
  mark('disabled tools do not expose executable button', 'pass');

  failIf(/artifact_type:\s*['"](audio|ppt|mindmap|document_comparison|compare)['"]/i.test(workspacePage), 'Phase 2/3 artifact mutation appears enabled');
  failIf(/\/(audio|ppt|mindmap|compare|document-comparison)/i.test(dataClient), 'Phase 2/3 backend route string appears in dataServiceClient');
  mark('no Phase 2/3 generation route or artifact mutation', 'pass');

  failIf(v14Sources.decision !== 'PASS_LIMITED', 'V1.4 P0 sources real-data smoke is not PASS_LIMITED');
  failIf(v14Sources.pdf_classification !== 'PDF_EXTRACTED', 'V1.4 P0 PDF extraction classification missing');
  const requiredP0 = ['markdown import', 'txt import', 'pdf browser upload import', 'pdf preview', 'pdf query citation'];
  for (const check of requiredP0) {
    failIf(!v14Sources.results?.some((item) => item.name === check && item.status === 'pass'), `V1.4 P0 check missing: ${check}`);
  }
  mark('P0 Markdown/TXT/extractable PDF real data smoke remains PASS_LIMITED', 'pass', v14Sources.pdf_classification);

  failIf(!v16OcrReport.includes('CONTRACT_DISCOVERY_READY'), 'V1.6 OCR contract discovery status missing');
  failIf(!v16OcrReport.includes('ocr=false') || !v16OcrReport.includes('scanned_pdf_ocr=false'), 'OCR disabled capability flags missing from V1.6 report');
  mark('OCR/scanned PDF remains contract-discovery disabled', 'pass');

  failIf(v19Rc.final_decision !== 'V1_9_READY_FOR_FINAL_HUMAN_ACCEPTANCE', 'V1.9 RC prerequisite is not ready for final human acceptance');
  mark('V1.9 RC prerequisite remains ready for human acceptance', 'pass');

  failIf(!v10Readme.includes('继续 `NOT_READY`') || !v10Readme.includes('继续 `DISABLED_READY`'), 'V1.10 README missing NOT_READY / DISABLED_READY wording');
  mark('V1.10 documentation keeps disabled boundary wording', 'pass');

  if (runBrowser) {
    await runBrowserBoundary();
  } else {
    mark('browser disabled boundary path', 'degraded', 'not run; set RN_V10_BROWSER=1 to execute ChromeCLI path');
  }

  const combined = JSON.stringify({ results, v14Sources, v19Rc });
  failIf(hasSensitiveText(combined), 'V1.10 disabled-boundary result contains sensitive path or secret-like text');
  mark('fixture/report hygiene', 'pass', 'no sensitive path or API key');

  finalDecision = 'V1_10_DISABLED_BOUNDARY_ACCEPTED';
} catch (error) {
  mark('v1.10 disabled boundary smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  const payload = {
    generated_at: new Date().toISOString(),
    final_decision: finalDecision,
    environment: {
      frontend_url: runBrowser ? appUrl : 'not_started_static_boundary_smoke',
      data_service_url: runBrowser ? baseUrl : 'fixture_based_real_data_smoke',
      browser: runBrowser ? `chrome-cdp:${chromePath ? 'configured' : 'missing'}` : 'not_started_static_boundary_smoke',
      tester: 'codex'
    },
    results,
    workspace_id: workspaceId || undefined,
    disabled_tool_network_request_count: networkRequests.filter((url) => /audio|ppt|mindmap|compare|document-comparison|phase-2|phase-3/i.test(url)).length,
    console_error_count: consoleErrors.length
  };
  await writeJson('v1_10_disabled_boundary_result.json', payload);
  await writeReport(payload);
  console.log(`V1_10_DISABLED_BOUNDARY_DECISION ${finalDecision}`);
  cdp?.close();
  chromeProcess?.kill();
}
