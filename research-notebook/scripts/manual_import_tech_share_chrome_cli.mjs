/* global fetch, WebSocket, setTimeout */

import { Buffer } from 'node:buffer';
import { execFileSync } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { extname, join, relative, sep } from 'node:path';
import { spawn } from 'node:child_process';

const appUrl = process.env.RN_BROWSER_APP_URL ?? 'http://127.0.0.1:5173';
const dataServiceBaseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const sourceRoot = process.env.RN_TECH_SHARE_DIR ?? '/Users/Zhuanz/Desktop/技术分享';
const timestamp = Date.now();
const workspaceName = process.env.RN_TECH_SHARE_WORKSPACE_NAME ?? `技术分享导入验收-${timestamp}`;
const chromePort = Number(process.env.RN_CHROME_REMOTE_DEBUGGING_PORT ?? 9234);
const stepDelayMs = Number(process.env.RN_TECH_SHARE_STEP_DELAY_MS ?? 120);
const keepBrowserOpen = process.env.RN_TECH_SHARE_KEEP_BROWSER_OPEN !== '0';
const maxCharsPerSource = Number(process.env.RN_TECH_SHARE_MAX_CHARS ?? 24_000);
const maxIndividualSources = Number(process.env.RN_TECH_SHARE_MAX_INDIVIDUAL_SOURCES ?? 90);
const chromePath = resolveChromiumPath();
const userDataDir = join('/private/tmp', `rn-tech-share-import-${timestamp}`);
const artifactsDir = join(process.cwd(), '.smoke-artifacts', 'tech-share-import', String(timestamp));
const fixtureDir = join(process.cwd(), 'fixtures', 'manual');
const reportPath = join(process.cwd(), 'docs/design/V1.2/tech_share_manual_import_report.md');

const ignoredDirNames = new Set(['node_modules', 'dist', 'build', '.git', '.next', '.vite', '.cache', 'coverage']);
const ignoredFileNames = new Set(['.DS_Store', 'package-lock.json', 'package.json', 'LICENSE', 'license']);
const textExtensions = new Set(['.md', '.markdown', '.txt', '.py', '.sh', '.html', '.htm', '.csv', '.json', '.jsonl', '.drawio', '.xml']);
const officeExtensions = new Set(['.pptx', '.docx']);
const metadataOnlyExtensions = new Set([
  '.pdf',
  '.mp4',
  '.mp3',
  '.png',
  '.jpg',
  '.jpeg',
  '.svg',
  '.webp',
  '.gif',
  '.theme',
  '.env',
  '.lock',
  '.tsbuildinfo',
  '.map'
]);
const knownWarningPatterns = [/React Router Future Flag Warning/i, /Failed to load resource: the server responded with a status of 404/i];

const results = [];
const imported = [];
const skipped = [];
const metadataOnlyFiles = [];
let discoveredSourceRecordCount = 0;
const consoleErrors = [];
const pageErrors = [];
const networkRequests = [];
const screenshots = [];
let chromeProcess;
let workspaceId = '';
let cdp;

function resolveChromiumPath() {
  if (process.env.RN_CHROMIUM_PATH) return process.env.RN_CHROMIUM_PATH;
  return [
    '/Applications/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium',
    '/usr/bin/chromium-browser',
    '/snap/bin/chromium'
  ].find((candidate) => existsSync(candidate)) ?? '';
}

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'not_ready' ? 'NOT_READY' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function pause() {
  if (stepDelayMs > 0) await delay(stepDelayMs);
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

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, sanitize(item)]));
  }
  if (typeof value !== 'string') return value;
  return value
    .replaceAll(sourceRoot, '<tech-share-root>')
    .replace(/\/Users\/[^/\s"',}]+/g, '<home>')
    .replace(/\/private(?:\/[^\s"',}]*)?/g, '<private>')
    .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '<tmp>')
    .replaceAll('file://', 'file-redacted://');
}

async function saveJson(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), `${JSON.stringify(sanitize(payload), null, 2)}\n`);
}

function assertChromeAvailable() {
  if (!chromePath || !existsSync(chromePath)) {
    throw new Error('Chrome executable not found. Set RN_CHROMIUM_PATH to a local Chrome executable.');
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
    { detached: keepBrowserOpen, stdio: 'ignore' }
  );
  if (keepBrowserOpen) chromeProcess.unref();
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

async function setFieldInForm(formLabel, fieldIndex, value, fieldSelector = 'input, select, textarea') {
  return evalJs(
    `(() => {
      const form = [...document.querySelectorAll('form')].find((el) => el.getAttribute('aria-label') === ${JSON.stringify(formLabel)});
      if (!form) return false;
      const field = [...form.querySelectorAll(${JSON.stringify(fieldSelector)})][${fieldIndex}];
      if (!field) return false;
      if (field.tagName === 'SELECT') {
        field.value = ${JSON.stringify(value)};
      } else {
        const proto = field.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
        const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
        setter.call(field, ${JSON.stringify(value)});
      }
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

async function textExists(text) {
  return evalJs(`document.body && document.body.innerText.includes(${JSON.stringify(text)})`);
}

async function saveScreenshot(name) {
  const result = await cdp.send('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  const file = join(artifactsDir, name);
  await writeFile(file, Buffer.from(result.data, 'base64'));
  screenshots.push(relative(process.cwd(), file));
}

function shouldIgnorePath(path) {
  const parts = path.split(sep);
  return parts.some((part) => ignoredDirNames.has(part));
}

async function collectFiles(dir) {
  const files = [];
  const stack = [dir];
  while (stack.length) {
    const current = stack.pop();
    let entries;
    try {
      entries = await import('node:fs/promises').then((fs) => fs.readdir(current, { withFileTypes: true }));
    } catch (error) {
      skipped.push({ relative_path: relative(sourceRoot, current), reason: `read_dir_failed: ${error.message}` });
      continue;
    }
    for (const entry of entries) {
      const full = join(current, entry.name);
      if (shouldIgnorePath(full)) continue;
      if (entry.isDirectory()) {
        stack.push(full);
      } else if (entry.isFile()) {
        if (ignoredFileNames.has(entry.name)) continue;
        files.push(full);
      }
    }
  }
  return files.sort((a, b) => relative(sourceRoot, a).localeCompare(relative(sourceRoot, b), 'zh-Hans-CN'));
}

function decodeXmlText(xml) {
  return xml
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .trim();
}

function extractZipText(path, ext) {
  const patterns = ext === '.pptx' ? ['ppt/slides/slide*.xml', 'ppt/notesSlides/notesSlide*.xml'] : ['word/document.xml'];
  const chunks = [];
  for (const pattern of patterns) {
    try {
      const stdout = execFileSync('unzip', ['-p', path, pattern], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
      const text = decodeXmlText(stdout);
      if (text) chunks.push(text);
    } catch {
      // Ignore missing optional zip entries.
    }
  }
  return chunks.join('\n\n').trim();
}

async function extractTextFile(path, ext) {
  const raw = await readFile(path, 'utf8');
  if (ext === '.json') return JSON.stringify(JSON.parse(raw), null, 2);
  if (ext === '.html' || ext === '.htm') return raw.replace(/<script[\s\S]*?<\/script>/gi, '').replace(/<style[\s\S]*?<\/style>/gi, '').replace(/<[^>]+>/g, ' ');
  return raw;
}

async function buildSourceRecords() {
  const files = await collectFiles(sourceRoot);
  const sourceRecords = [];
  for (const path of files) {
    const rel = relative(sourceRoot, path);
    const ext = extname(path).toLowerCase();
    const stats = statSync(path);
    try {
      if (textExtensions.has(ext)) {
        const text = await extractTextFile(path, ext);
        sourceRecords.push(makeRecord(rel, ext === '.json' || ext === '.jsonl' ? 'json' : ext === '.md' || ext === '.markdown' ? 'markdown' : 'text', text, 'direct_text'));
      } else if (officeExtensions.has(ext)) {
        const text = extractZipText(path, ext);
        if (text) sourceRecords.push(makeRecord(rel, 'text', text, `${ext.slice(1)}_zip_xml_text`));
        else metadataOnlyFiles.push({ relative_path: rel, extension: ext, size_bytes: stats.size, reason: 'office_text_extract_empty' });
      } else if (metadataOnlyExtensions.has(ext) || stats.size > 1_500_000) {
        metadataOnlyFiles.push({ relative_path: rel, extension: ext || '<none>', size_bytes: stats.size, reason: 'metadata_only' });
      } else {
        metadataOnlyFiles.push({ relative_path: rel, extension: ext || '<none>', size_bytes: stats.size, reason: 'unsupported_extension' });
      }
    } catch (error) {
      metadataOnlyFiles.push({ relative_path: rel, extension: ext || '<none>', size_bytes: stats.size, reason: `extract_failed: ${error.message}` });
    }
  }
  if (metadataOnlyFiles.length) {
    sourceRecords.push(
      makeRecord(
        '_媒体与未抽取文件清单',
        'text',
        metadataOnlyFiles.map((item) => `${item.relative_path}\t${item.extension}\t${item.size_bytes} bytes\t${item.reason}`).join('\n'),
        'metadata_manifest'
      )
    );
  }
  discoveredSourceRecordCount = sourceRecords.length;
  if (sourceRecords.length > maxIndividualSources) {
    const individual = sourceRecords.slice(0, Math.max(0, maxIndividualSources - 1));
    const aggregated = sourceRecords.slice(Math.max(0, maxIndividualSources - 1));
    const aggregateBody = aggregated
      .map((record) => `${record.relative_path}\t${record.source_type}\t${record.extraction_method}\t${record.content.length} chars`)
      .join('\n');
    individual.push(makeRecord('_剩余技术分享文件清单', 'text', aggregateBody, 'aggregated_remaining_manifest'));
    return individual;
  }
  return sourceRecords;
}

function makeRecord(relativePath, sourceType, body, method) {
  const truncated = body.length > maxCharsPerSource;
  const content = body.slice(0, maxCharsPerSource);
  return {
    relative_path: relativePath,
    title: `${relativePath}`.slice(0, 180),
    source_type: sourceType,
    extraction_method: method,
    truncated,
    content:
      `相对路径: ${relativePath}\n` +
      `抽取方式: ${method}\n` +
      `是否截断: ${truncated ? '是' : '否'}\n\n` +
      content
  };
}

async function importSource(record, index, total) {
  if (!(await setFieldInForm('导入来源', 0, record.title))) throw new Error(`could not set title for ${record.relative_path}`);
  if (!(await setFieldInForm('导入来源', 1, record.source_type))) throw new Error(`could not set source type for ${record.relative_path}`);
  if (!(await setFieldInForm('导入来源', 2, record.content))) throw new Error(`could not set content for ${record.relative_path}`);
  if (!(await submitForm('导入来源'))) throw new Error(`could not submit source form for ${record.relative_path}`);
  await waitFor(
    () =>
      evalJs(
        `(() => {
          const form = [...document.querySelectorAll('form')].find((el) => el.getAttribute('aria-label') === '导入来源');
          if (!form) return false;
          const button = form.querySelector('button[type="submit"]');
          const failed = document.body.innerText.includes('来源导入失败');
          const appears = document.body.innerText.includes(${JSON.stringify(record.title)});
          return !failed && ((button && !button.disabled) || appears);
        })()`
      ),
    `source import completed: ${record.relative_path}`,
    45_000
  );
  await pause();
  imported.push({
    relative_path: record.relative_path,
    source_type: record.source_type,
    extraction_method: record.extraction_method,
    truncated: record.truncated
  });
  mark(`import source ${index}/${total}`, 'pass', record.relative_path);
}

async function clickPreviewForTitle(title) {
  return evalJs(
    `(() => {
      const card = [...document.querySelectorAll('article.source-card')].find((el) => (el.textContent || '').includes(${JSON.stringify(title)}));
      const button = card && [...card.querySelectorAll('button')].find((el) => (el.textContent || '').includes('预览') || (el.textContent || '').includes('Preview'));
      if (!button || button.disabled) return false;
      button.click();
      return true;
    })()`
  );
}

async function previewSamples(records) {
  const samples = [
    records.find((record) => record.extraction_method.includes('pptx') || record.extraction_method.includes('docx')),
    records.find((record) => record.source_type === 'markdown'),
    records.find((record) => record.source_type === 'json')
  ].filter(Boolean);
  for (const sample of samples) {
    await waitFor(() => clickPreviewForTitle(sample.title), `preview button clickable: ${sample.relative_path}`);
    await waitFor(() => textExists('来源预览'), `preview drawer opens: ${sample.relative_path}`);
    await waitFor(() => textExists('文档单元') || textExists('来源正文'), `preview content visible: ${sample.relative_path}`);
    await saveScreenshot(`preview-${samples.indexOf(sample) + 1}.png`);
    mark('preview sample visible', 'pass', sample.relative_path);
    await evalJs(
      `(() => {
        const drawer = document.querySelector('[data-testid="source-preview-drawer"]');
        const button = drawer && [...drawer.querySelectorAll('button')].find((el) => (el.textContent || '').includes('关闭'));
        if (button) button.click();
        return true;
      })()`
    );
    await pause();
  }
}

async function writeReport(summary) {
  const lines = [
    '# 技术分享目录 Chrome CLI 导入验收报告',
    '',
    `执行时间：${new Date().toISOString()}`,
    '',
    '## 环境',
    '',
    `- 前端：${appUrl}`,
    `- 后端：${dataServiceBaseUrl}`,
    `- 工作区：${workspaceName}`,
    `- workspace_id：${workspaceId}`,
    '- 源目录：`<tech-share-root>`',
    '',
    '## 结果',
    '',
    `- 扫描后导入来源数：${summary.imported_count}`,
    `- metadata-only 文件数：${summary.metadata_only_count}`,
    `- 跳过文件/目录数：${summary.skipped_count}`,
    `- 预览抽样：${summary.preview_sample_count}`,
    `- Chrome 窗口保留：${keepBrowserOpen ? '是' : '否'}`,
    '',
    '## 说明',
    '',
    '- md/json/py/html/csv 等文本类文件直接抽取文本。',
    '- pptx/docx 通过 zip XML 尽力抽取文本。',
    '- pdf/mp4/mp3/png/jpg 等以 metadata-only 清单导入，不代表音视频/图像正文摄入 ready。',
    '- 报告与 fixture 不记录本地绝对路径。',
    '',
    '## 主要文件',
    '',
    ...summary.imported.slice(0, 80).map((item) => `- ${item.relative_path} (${item.source_type}, ${item.extraction_method})`),
    summary.imported.length > 80 ? `- 其余 ${summary.imported.length - 80} 条见 fixture。` : '',
    '',
    '## Artifact',
    '',
    `- Summary fixture：fixtures/manual/tech-share-import-summary.json`,
    `- 截图目录：${sanitize(artifactsDir)}`,
    ''
  ];
  await writeFile(reportPath, `${lines.filter((line) => line !== '').join('\n')}\n`);
}

async function main() {
  try {
    if (!existsSync(sourceRoot)) throw new Error(`source root does not exist: ${sourceRoot}`);
    await mkdir(artifactsDir, { recursive: true });
    assertChromeAvailable();
    await request('/api/workspaces');
    mark('data_service target route probe', 'pass', dataServiceBaseUrl);

    const sourceRecords = await buildSourceRecords();
    await saveJson('tech-share-import-manifest.json', {
      source_root: '<tech-share-root>',
      source_count: sourceRecords.length,
      metadata_only_count: metadataOnlyFiles.length,
      discovered_source_record_count: discoveredSourceRecordCount,
      max_individual_sources: maxIndividualSources,
      skipped,
      records: sourceRecords.map(({ content, ...record }) => ({ ...record, content_size: content.length }))
    });
    mark('tech share files prepared', 'pass', `${sourceRecords.length} import records, ${metadataOnlyFiles.length} metadata-only files`);

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
    await waitFor(() => textExists('个人知识工作区'), 'app home rendered');
    mark('visible Chrome opened app', 'pass', appUrl);

    if (!(await setFieldInForm('创建工作区', 0, workspaceName))) throw new Error('could not set workspace name');
    if (!(await submitForm('创建工作区'))) throw new Error('could not submit workspace form');
    await waitFor(() => evalJs(`location.pathname.startsWith('/workspaces/')`), 'workspace route after create');
    await waitFor(() => textExists('来源库'), 'workspace page rendered');
    workspaceId = await evalJs(`location.pathname.split('/').filter(Boolean)[1] || ''`);
    mark('workspace create and enter', 'pass', workspaceId);

    for (let index = 0; index < sourceRecords.length; index += 1) {
      try {
        await importSource(sourceRecords[index], index + 1, sourceRecords.length);
    } catch (error) {
      skipped.push({ relative_path: sourceRecords[index].relative_path, reason: `ui_import_failed: ${error.message}` });
      mark(`import source ${index + 1}/${sourceRecords.length}`, 'fail', `${sourceRecords[index].relative_path}: ${error.message}`);
    }
    }

    await previewSamples(sourceRecords);
    const forbiddenRequests = networkRequests.filter((url) => url.includes('/api/v1/knowledge'));
    if (forbiddenRequests.length) throw new Error(`/api/v1/knowledge request observed: ${forbiddenRequests[0]}`);
    if (pageErrors.length || consoleErrors.length) {
      throw new Error(`blocking browser errors: ${[...pageErrors, ...consoleErrors].join(' | ')}`);
    }
    mark('browser console/network guard', 'pass');

    const summary = {
      declaration: skipped.some((item) => item.reason.startsWith('ui_import_failed')) ? 'TECH_SHARE_IMPORT_PARTIAL_PASS' : 'TECH_SHARE_IMPORT_PASS',
      app_url: appUrl,
      data_service_base_url: dataServiceBaseUrl,
      workspace_name: workspaceName,
      workspace_id: workspaceId,
      source_root: '<tech-share-root>',
      discovered_source_record_count: discoveredSourceRecordCount,
      max_individual_sources: maxIndividualSources,
      imported_count: imported.length,
      metadata_only_count: metadataOnlyFiles.length,
      skipped_count: skipped.length,
      preview_sample_count: Math.min(3, imported.length),
      imported,
      metadata_only_files: metadataOnlyFiles,
      skipped,
      screenshots,
      results
    };
    await saveJson('tech-share-import-summary.json', summary);
    await writeFile(join(artifactsDir, 'tech-share-import-summary.json'), `${JSON.stringify(sanitize(summary), null, 2)}\n`);
    await writeReport(summary);
    console.log(`TECH_SHARE_IMPORT_DECISION ${summary.declaration}`);
  } catch (error) {
    mark('tech share visible import', 'fail', error instanceof Error ? error.message : String(error));
    await saveJson('tech-share-import-summary.json', {
      declaration: 'TECH_SHARE_IMPORT_FAIL',
      workspace_name: workspaceName,
      workspace_id: workspaceId,
      error: error instanceof Error ? error.message : String(error),
      imported,
      metadata_only_files: metadataOnlyFiles,
      skipped,
      results
    }).catch(() => undefined);
    process.exitCode = 1;
  } finally {
    if (cdp) cdp.close();
    if (chromeProcess && !chromeProcess.killed && !keepBrowserOpen) chromeProcess.kill('SIGTERM');
    if (keepBrowserOpen) {
      console.log(`VISIBLE_CHROME_LEFT_OPEN remote_debugging_port=${chromePort} profile=${userDataDir}`);
    }
  }
}

await main();
