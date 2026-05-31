/* global fetch, WebSocket, setTimeout */
import { Buffer } from 'node:buffer';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join, relative } from 'node:path';

const root = process.cwd();
const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9260);
const timestamp = Date.now();
const artifactsDir = join(root, '.smoke-artifacts', 'v1_x_interactive_acceptance', String(timestamp));
const screenshotsDir = join(artifactsDir, 'screenshots');
const userDataDir = join('/private/tmp', `rn-v1x-interactive-profile-${timestamp}`);
const materialDir =
  process.env.RN_V1X_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V1X_DIGITAL_HUMAN_PDF ??
  join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const headless = process.env.RN_V1X_INTERACTIVE_HEADLESS !== '0';
const chromePath = resolveChromiumPath();
const workspaceName = process.env.RN_V1X_INTERACTIVE_WORKSPACE ?? `rn-v1x-interactive-${timestamp}`;

const results = [];
const screenshots = [];
const keyTexts = {};
const networkRequests = [];
const consoleErrors = [];
const pageErrors = [];
let chromeProcess;
let cdp;
let workspaceId = '';
let finalDecision = 'FAIL';

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

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitFor(fn, label, timeoutMs = 90_000) {
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

function sanitizeText(value) {
  return String(value ?? '')
    .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]')
    .replace(/\/Users\/[^\s"',<>)]+/g, '[home-path]')
    .replace(/\/private\/tmp\/[^\s"',<>)]+/g, '[private-tmp]')
    .replace(/\/tmp\/[^\s"',<>)]+/g, '[tmp]')
    .replace(/file:\/\//g, 'file-redacted://')
    .slice(0, 8000);
}

function hasSensitiveText(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\/|DATA_SERVICE_AI_API_KEY|api_key|authorization|bearer\s+/i.test(
    String(value)
  );
}

function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

async function seedWorkspace() {
  const overview = await readFile(join(materialDir, '01_industry_overview.md'), 'utf8');
  const technology = await readFile(join(materialDir, '02_technology_trends.md'), 'utf8');
  const pdfBase64 = (await readFile(realPdfPath)).toString('base64');

  const created = await request('/api/workspaces', {
    method: 'POST',
    body: { name: workspaceName, owner: 'v1.x-interactive', tags: ['v1.x', 'interactive-acceptance'] }
  });
  workspaceId = dataOf(created)?.workspace?.workspace_id ?? created.workspace_id;
  failIf(!workspaceId, 'workspace_id missing after workspace creation');

  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { texts: [{ title: 'AI 数字人行业概览 Markdown', content: overview, metadata: { source_format: 'markdown' } }] }
  });
  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { texts: [{ title: 'AI 数字人技术趋势 Markdown', content: technology, metadata: { source_format: 'markdown' } }] }
  });
  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
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

  const build = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, { method: 'POST', body: {} });
  const operationId = dataOf(build)?.operation_id ?? build.operation_id;
  if (operationId) {
    await waitFor(async () => {
      const latest = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
      const status = dataOf(latest)?.operation?.status ?? dataOf(latest)?.status;
      if (status === 'completed') return latest;
      if (['failed', 'blocked', 'cancelled'].includes(status)) throw new Error(`workspace build ${status}`);
      return null;
    }, 'workspace build completed', 180_000);
  }

  mark('workspace and real sources seeded', 'pass', workspaceId);
}

function startChrome() {
  failIf(!chromePath || !existsSync(chromePath), 'Chrome/Chromium executable not found. Set RN_CHROMIUM_PATH.');
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

async function textIncludes(text) {
  return evaluate(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function capture(name, title, selector = 'body') {
  await mkdir(screenshotsDir, { recursive: true });
  await evaluate(`(() => {
    document.querySelectorAll('[data-v1x-capture]').forEach((el) => el.removeAttribute('data-v1x-capture'));
    const target = document.querySelector(${JSON.stringify(selector)});
    if (target) target.setAttribute('data-v1x-capture', 'true');
    target?.scrollIntoView?.({ block: 'center', inline: 'center' });
    return Boolean(target);
  })()`);
  await delay(300);
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const fileName = `${String(screenshots.length + 1).padStart(2, '0')}-${name}.png`;
  const absolutePath = join(screenshotsDir, fileName);
  await writeFile(absolutePath, Buffer.from(result.data, 'base64'));
  const rel = relative(artifactsDir, absolutePath);
  screenshots.push({ name, title, file: rel });
  keyTexts[name] = sanitizeText(
    await evaluate(`(() => {
      const target = document.querySelector(${JSON.stringify(selector)}) || document.body;
      return target.innerText || '';
    })()`)
  );
  mark(`capture ${title}`, 'pass', rel);
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
  failIf(!didSet, 'question textarea not found');
  await waitFor(
    () =>
      evaluate(`(() => {
        const form = document.querySelector('.ask-form');
        const button = form && [...form.querySelectorAll('button')].find((el) => el.innerText.includes('发送问题'));
        const textarea = form && form.querySelector('textarea');
        return Boolean(textarea && textarea.value.trim() && button && !button.disabled);
      })()`),
    'query submit button enabled'
  );
  await evaluate(`(() => {
    const form = document.querySelector('.ask-form');
    const button = form && [...form.querySelectorAll('button')].find((el) => el.innerText.includes('发送问题'));
    button?.click();
    return Boolean(button);
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

async function clickResearchButton() {
  return evaluate(`(() => {
    const buttons = [...document.querySelectorAll('button')];
    const button = buttons.find((item) => item.innerText.includes('生成 Research 综合') && !item.disabled);
    button?.click();
    return Boolean(button);
  })()`);
}

async function generateStudioOutputs() {
  const tools = ['笔记', '学习导读', '资料简报', '常见问题'];
  for (let index = 0; index < tools.length; index += 1) {
    await waitFor(
      () =>
        evaluate(`(() => {
          const cards = [...document.querySelectorAll('.studio-tool-list article')];
          const card = cards[${index}];
          const button = card && [...card.querySelectorAll('button')].find((item) => item.innerText.includes('生成'));
          return Boolean(button && !button.disabled);
        })()`),
      `Studio ${tools[index]} button enabled`
    );
    await evaluate(`(() => {
      const cards = [...document.querySelectorAll('.studio-tool-list article')];
      const card = cards[${index}];
      const button = card && [...card.querySelectorAll('button')].find((item) => item.innerText.includes('生成') && !item.disabled);
      button?.click();
      return Boolean(button);
    })()`);
    await waitFor(
      () =>
        evaluate(`(() => {
          const cards = [...document.querySelectorAll('.studio-tool-list article')];
          const card = cards[${index}];
          return Boolean(card && card.innerText.includes(${JSON.stringify(tools[index])}) && card.innerText.includes('已生成'));
        })()`),
      `Studio ${tools[index]} generated state visible`,
      120_000
    );
    await waitFor(
      () =>
        evaluate(`(() => {
          const panel = document.querySelector('.studio-panel');
          return Boolean(
            panel &&
              panel.innerText.includes(${JSON.stringify(tools[index])}) &&
              panel.innerText.includes('复制 Markdown') &&
              panel.innerText.includes('下载 JSON') &&
              panel.innerText.includes('可定位到原文片段')
          );
        })()`),
      `Studio ${tools[index]} artifact and citation visible`,
      120_000
    );
    await capture(`studio-${index + 1}`, `Studio ${tools[index]}`, '.studio-panel');
    await delay(1200);
  }
}

async function assertDisabledTools() {
  for (const title of ['音频概览', 'PPT 生成', '思维导图', '文档对比']) {
    failIf(!(await textIncludes(title)), `${title} disabled tool not visible`);
  }
  const disabledCount = await evaluate(`(() => [...document.querySelectorAll('button')].filter((button) => button.innerText.includes('暂不可用') && button.disabled).length)()`);
  failIf(disabledCount < 4, `expected at least 4 disabled tool buttons, got ${disabledCount}`);
  const before = networkRequests.length;
  await evaluate(`(() => {
    const buttons = [...document.querySelectorAll('button')].filter((button) => button.innerText.includes('暂不可用'));
    for (const button of buttons) button.click();
    return buttons.length;
  })()`);
  await delay(800);
  const afterRequests = networkRequests.slice(before);
  const forbidden = afterRequests.filter((url) => /audio|ppt|mindmap|compare|document-comparison|phase-2|phase-3/i.test(url));
  failIf(forbidden.length > 0, `disabled tool triggered request: ${forbidden[0]}`);
  mark('Phase 2/3 disabled tools checked', 'pass', `${disabledCount} disabled buttons`);
}

async function runBrowserPath() {
  startChrome();
  cdp = createCdpClient(await getWebSocketUrl());
  await cdp.waitOpen();
  cdp.on('Network.requestWillBeSent', (event) => networkRequests.push(event.request?.url ?? ''));
  cdp.on('Runtime.consoleAPICalled', (event) => {
    const text = (event.args ?? []).map((arg) => arg.value ?? arg.description ?? '').join(' ');
    if (event.type === 'error' && !/React Router Future Flag Warning/i.test(text)) consoleErrors.push(sanitizeText(text));
  });
  cdp.on('Runtime.exceptionThrown', (event) => pageErrors.push(sanitizeText(event.exceptionDetails?.text ?? 'page exception')));
  await cdp.send('Runtime.enable');
  await cdp.send('Page.enable');
  await cdp.send('Network.enable');

  await cdp.send('Page.navigate', { url: `${appUrl}/workspaces/${encodeURIComponent(workspaceId)}` });
  await waitFor(() => textIncludes('资料导读'), 'workspace page loaded');
  await waitFor(() => evaluate(`document.body.innerText.includes('概览') && !document.body.innerText.includes('正在生成资料导读')`), 'guide visible', 180_000);
  await capture('guide', 'Notebook Guide', '.notebook-column-chat');

  await setQuestionAndSubmit('数字人技术趋势和产业应用有哪些重点？');
  await waitFor(() => textIncludes('回答'), 'QA answer visible', 120_000);
  await waitFor(() => textIncludes('可定位到原文片段'), 'QA citation visible', 120_000);
  await capture('qa-answer', '引用问答', '.notebook-column-chat');

  failIf(!(await clickFirstJumpableCitation()), 'jumpable citation button not found');
  await waitFor(() => evaluate(`Boolean(document.querySelector('[data-testid="evidence-highlight"]'))`), 'EvidenceSpan highlight visible', 120_000);
  await capture('citation-highlight', 'Citation 来源定位', '.source-preview-drawer');

  if (await clickResearchButton()) {
    await waitFor(() => textIncludes('Research 综合输出'), 'Research report visible', 120_000);
    await capture('research-report', 'Research 综合输出', '.notebook-column-chat');
  } else {
    mark('Research button', 'degraded', 'not available after QA answer');
  }

  await generateStudioOutputs();
  await capture('studio-export', 'Studio 导出入口', '.studio-panel');

  await setQuestionAndSubmit('火星采矿、农业机械和海洋运输的数字人结论是什么？');
  await waitFor(() => textIncludes('当前资料未覆盖'), 'source-grounded refusal visible', 120_000);
  await capture('refusal', '资料不足拒答', '.notebook-column-chat');

  await assertDisabledTools();
  await capture('disabled-tools', '后续输出工具 disabled', '.studio-panel');

  failIf(networkRequests.some((url) => url.includes('/api/v1/knowledge')), 'browser requested /api/v1/knowledge');
}

async function cleanup() {
  if (workspaceId) {
    try {
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.x interactive acceptance cleanup' }
      });
      mark('cleanup workspace', 'pass', workspaceId);
    } catch (error) {
      mark('cleanup workspace', 'degraded', error instanceof Error ? error.message : String(error));
    }
  }
  cdp?.close();
  chromeProcess?.kill('SIGTERM');
}

function buildHtmlReport(payload) {
  const resultRows = payload.results
    .map((item) => `<tr><td>${escapeHtml(item.name)}</td><td><span class="${item.status}">${escapeHtml(item.status.toUpperCase())}</span></td><td>${escapeHtml(item.detail)}</td></tr>`)
    .join('\n');
  const screenshotCards = payload.screenshots
    .map(
      (item) => `<article class="shot">
        <button class="shot-button" type="button" data-image="${escapeHtml(item.file)}">
          <img src="${escapeHtml(item.file)}" alt="${escapeHtml(item.title)}" />
        </button>
        <h3>${escapeHtml(item.title)}</h3>
        <pre>${escapeHtml(payload.key_texts[item.name] ?? '')}</pre>
      </article>`
    )
    .join('\n');
  return `<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>ResearchNotebook V1.x 交互式验收证据包</title>
  <style>
    :root { color-scheme: light; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f6f4ef; color: #172026; }
    body { margin: 0; padding: 32px; }
    main { max-width: 1180px; margin: 0 auto; }
    h1, h2, h3 { margin: 0 0 12px; }
    .summary, .panel, .shot { background: #fffdf8; border: 1px solid #ddd6c8; border-radius: 10px; padding: 18px; margin: 16px 0; box-shadow: 0 12px 30px rgba(23,32,38,.08); }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 16px; }
    table { border-collapse: collapse; width: 100%; background: #fff; }
    th, td { border-bottom: 1px solid #e5ded0; padding: 10px; text-align: left; vertical-align: top; }
    .pass { color: #116149; font-weight: 700; }
    .degraded { color: #946200; font-weight: 700; }
    .fail { color: #a42424; font-weight: 700; }
    .shot img { width: 100%; max-height: 360px; object-fit: contain; background: #eee7db; border: 1px solid #ddd6c8; border-radius: 8px; }
    .shot-button { appearance: none; border: 0; background: transparent; padding: 0; width: 100%; cursor: zoom-in; }
    pre { white-space: pre-wrap; max-height: 220px; overflow: auto; background: #f5efe4; border-radius: 8px; padding: 12px; line-height: 1.5; }
    .modal { position: fixed; inset: 0; display: none; align-items: center; justify-content: center; background: rgba(0,0,0,.86); z-index: 99; }
    .modal.open { display: flex; }
    .modal img { max-width: 96vw; max-height: 92vh; object-fit: contain; cursor: zoom-in; transition: transform .15s ease; }
    .modal img.zoomed { transform: scale(1.8); cursor: zoom-out; }
    .modal button { position: fixed; right: 24px; top: 18px; font-size: 18px; padding: 8px 12px; border-radius: 8px; border: 0; }
  </style>
</head>
<body>
<main>
  <section class="summary">
    <h1>ResearchNotebook V1.x 交互式验收证据包</h1>
    <p>最终状态：<strong>${escapeHtml(payload.final_decision)}</strong></p>
    <p>该报告由 Chrome/CDP 自动操作生成，用于辅助人工验收；它不能替代 Guide / QA / Studio / Research 的人工内容质量判断。</p>
    <p>工作区：${escapeHtml(payload.workspace_id)} · 前端：${escapeHtml(payload.app_url)} · 后端：${escapeHtml(payload.base_url)}</p>
  </section>
  <section class="panel">
    <h2>自动化断言结果</h2>
    <table><thead><tr><th>项目</th><th>状态</th><th>说明</th></tr></thead><tbody>${resultRows}</tbody></table>
  </section>
  <section class="panel">
    <h2>仍需人工判断</h2>
    <ul>
      <li>Guide 是否准确覆盖数字人资料，不泛泛而谈。</li>
      <li>QA 与 Studio 输出的 citation 是否语义正确。</li>
      <li>Research 是否严格基于来源，未用资料外常识硬答。</li>
      <li>Markdown / JSON 导出文件内容是否满足实际交付需要。</li>
      <li>后续输出工具 disabled 文案是否不会误导普通用户。</li>
    </ul>
  </section>
  <section class="grid">${screenshotCards}</section>
</main>
<div class="modal" id="modal"><button type="button" id="close">关闭</button><img alt="放大截图" id="modalImage" /></div>
<script>
  const modal = document.getElementById('modal');
  const image = document.getElementById('modalImage');
  document.querySelectorAll('[data-image]').forEach((button) => {
    button.addEventListener('click', () => {
      image.src = button.dataset.image;
      image.classList.remove('zoomed');
      modal.classList.add('open');
    });
  });
  image.addEventListener('click', () => image.classList.toggle('zoomed'));
  document.getElementById('close').addEventListener('click', () => modal.classList.remove('open'));
  modal.addEventListener('click', (event) => { if (event.target === modal) modal.classList.remove('open'); });
</script>
</body>
</html>`;
}

async function writeArtifacts() {
  await mkdir(artifactsDir, { recursive: true });
  const payload = {
    generated_at: new Date().toISOString(),
    final_decision: finalDecision,
    app_url: appUrl,
    base_url: baseUrl,
    workspace_id: workspaceId || null,
    screenshots,
    key_texts: keyTexts,
    results,
    console_error_count: consoleErrors.length,
    page_error_count: pageErrors.length,
    forbidden_network_request_count: networkRequests.filter((url) => url.includes('/api/v1/knowledge')).length,
    declaration:
      finalDecision === 'READY_FOR_HUMAN_REVIEW_WITH_BROWSER_EVIDENCE'
        ? 'Interactive browser evidence package is ready for human review. It does not replace human quality acceptance.'
        : 'Interactive browser evidence package failed or is incomplete.'
  };
  const serialized = JSON.stringify(payload, null, 2);
  failIf(hasSensitiveText(serialized), 'result payload contains sensitive path or secret-like text');
  await writeFile(join(artifactsDir, 'result.json'), `${serialized}\n`);
  await writeFile(join(artifactsDir, 'key-texts.json'), `${JSON.stringify(keyTexts, null, 2)}\n`);
  await writeFile(join(artifactsDir, 'index.html'), buildHtmlReport(payload));
  console.log(`V1_X_INTERACTIVE_REPORT ${join(artifactsDir, 'index.html')}`);
}

async function main() {
  try {
    await request('/api/workspaces');
    await fetch(appUrl);
    mark('startup', 'pass', `${appUrl} / ${baseUrl}`);
    await seedWorkspace();
    await runBrowserPath();
    failIf(consoleErrors.length > 0 || pageErrors.length > 0, `browser errors: console=${consoleErrors.length}, page=${pageErrors.length}`);
    finalDecision = 'READY_FOR_HUMAN_REVIEW_WITH_BROWSER_EVIDENCE';
  } catch (error) {
    mark('interactive acceptance exception', 'fail', error instanceof Error ? error.message : String(error));
    finalDecision = 'FAIL';
    process.exitCode = 1;
  } finally {
    await cleanup();
    await writeArtifacts();
  }
}

await main();
