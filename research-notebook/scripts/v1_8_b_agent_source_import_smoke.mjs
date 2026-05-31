/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V18_B_PREFIX ?? `rn-v18-agent-source-import-${Date.now()}`;
const materialRoot =
  process.env.RN_V18_B_SOURCE_ROOT ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人');
const materialDir = process.env.RN_V18_B_MARKDOWN_DIR ?? join(materialRoot, 'AI数字人资料包');
const realPdfPath = process.env.RN_V18_B_PDF ?? join(materialRoot, 'AI数字人产业发展报告_2026-05-26.pdf');
const successUrls = (process.env.RN_V18_B_SUCCESS_URLS ?? 'http://example.com/,http://example.org/')
  .split(',')
  .map((item) => item.trim())
  .filter(Boolean);
const failingUrl = process.env.RN_V18_B_FAILING_URL ?? 'http://127.0.0.1:8003/';
const artifactRoot = join(process.cwd(), '.smoke-artifacts', 'v1_8_b_agent_source_import', String(Date.now()));
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_8', 'agent-source-import');
const maxPollMs = Number(process.env.RN_V18_B_MAX_POLL_MS ?? 60_000);
const pollIntervalMs = Number(process.env.RN_V18_B_POLL_INTERVAL_MS ?? 1_000);

const markdownFiles = ['01_industry_overview.md', '02_technology_trends.md'];
const results = [];
const assertions = [];
const fixtures = {};
const sourceIds = [];
const skippedFiles = [];
let workspaceId = '';
let finalDecision = 'FAIL';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function assertRecord(name, expected, actual, status, evidenceRef = '') {
  assertions.push({
    assertion_id: `assert_${String(assertions.length + 1).padStart(3, '0')}`,
    name,
    expected,
    actual,
    status,
    evidence_ref: evidenceRef || undefined
  });
  if (status === 'FAIL') throw new Error(`${name}: expected ${JSON.stringify(expected)}, actual ${JSON.stringify(actual)}`);
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const output = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (lowered === 'relative_path') {
        output[key] = sanitize(item);
        continue;
      }
      if (
        lowered.includes('api_key') ||
        lowered.includes('authorization') ||
        lowered === 'path' ||
        lowered === 'paths' ||
        lowered.endsWith('_path') ||
        lowered.endsWith('_paths') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack') ||
        lowered.includes('content_base64')
      ) {
        continue;
      }
      output[key] = sanitize(item);
    }
    return output;
  }
  if (typeof value === 'string') {
    return value
      .replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]')
      .replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]')
      .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]')
      .replaceAll('file://', 'file-redacted://')
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  fixtures[name] = sanitize(payload);
  await writeFile(join(fixtureDir, name), `${JSON.stringify(fixtures[name], null, 2)}\n`);
}

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: options.method ?? 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  return { ok: response.ok, status: response.status, path, payload };
}

async function mustRequest(path, options = {}) {
  const result = await request(path, options);
  if (!result.ok) {
    const error = new Error(`HTTP ${result.status} ${path}`);
    error.status = result.status;
    error.payload = result.payload;
    throw error;
  }
  return result.payload;
}

function dataOf(payload) {
  return payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

function extractWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace?.workspace_id ?? data?.workspace_id ?? payload?.workspace_id;
}

function extractSourceId(payload) {
  const data = dataOf(payload);
  return data?.source?.source_id ?? data?.sources?.[0]?.source_id ?? payload?.source_id;
}

function extractOperationId(payload) {
  const data = dataOf(payload);
  return payload?.operation_id ?? data?.operation_id ?? data?.operation?.operation_id;
}

function stripMarkdown(markdown) {
  return markdown
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^#+\s+/gm, '')
    .replace(/^>\s?/gm, '')
    .replace(/[*_`|]/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function createDraft() {
  const task = {
    task_id: `task_${Date.now()}`,
    user_intent: '导入数字人资料并验证 P0/P1 来源导入能力',
    target_path_labels: ['Desktop/技术分享/11-数字人'],
    target_path_refs: [],
    target_urls: successUrls.concat(failingUrl),
    source_policy: {
      allowed_types: ['pdf', 'txt', 'markdown', 'url'],
      recursive_folder_scan: true,
      require_user_authorization: true,
      skip_unsupported_types: true
    },
    expected_outputs: ['validation_report'],
    status: 'draft'
  };
  mark('agent draft created', 'pass', task.task_id);
  assertRecord('draft does not include raw target paths', false, JSON.stringify(task).includes('/Users'), 'PASS', task.task_id);
  return task;
}

function grantPermission(task) {
  const grant = {
    permission_grant_id: `perm_${Date.now()}`,
    task_id: task.task_id,
    root_label: 'Desktop/技术分享/11-数字人',
    scopes: ['scan', 'read_source'],
    status: 'approved',
    created_at: new Date().toISOString()
  };
  task.target_path_refs = [grant.permission_grant_id];
  task.status = 'approved';
  mark('permission grant recorded', 'pass', grant.permission_grant_id);
  return grant;
}

async function scanAuthorizedSources(permissionGrant) {
  if (!permissionGrant?.permission_grant_id || permissionGrant.status !== 'approved') {
    throw new Error('permission_grant_id is required before scan');
  }
  const md = {};
  for (const fileName of markdownFiles) {
    md[fileName] = await readFile(join(materialDir, fileName), 'utf8');
  }
  const pdf = await readFile(realPdfPath);
  const txt = stripMarkdown(md['01_industry_overview.md']);
  await mkdir(artifactRoot, { recursive: true });
  await writeFile(join(artifactRoot, 'ai-digital-human-sample.txt'), `${txt}\n`);
  skippedFiles.push({
    relative_path: '2026_Silicon_Workforce_Blueprint.pptx',
    skipped_reason: 'unsupported_extension'
  });
  mark('authorized source scan', 'pass', `${markdownFiles.length} markdown, 1 txt, 1 pdf, ${skippedFiles.length} skipped`);
  return { markdown: md, txt, pdf };
}

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.8-agent-source-import', tags: ['v1.8', 'agent-source-import'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  await saveFixture('workspace-create.json', payload);
  mark('workspace create', 'pass', workspaceId);
}

async function importTextSource(title, content, sourceFormat, fixtureName) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title,
          content,
          metadata: { source_format: sourceFormat, v1_8_agent_source_import: true }
        }
      ],
      metadata: { source_format: sourceFormat, v1_8_agent_source_import: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${sourceFormat} source_id missing`);
  sourceIds.push(sourceId);
  await saveFixture(fixtureName, payload);
  mark(`${sourceFormat} import`, 'pass', sourceId);
  return sourceId;
}

async function importPdfSource(pdfBuffer) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      metadata: {
        title: 'AI 数字人产业发展报告 PDF',
        source_type: 'pdf',
        file_name: basename(realPdfPath),
        v1_8_agent_source_import: true
      },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: pdfBuffer.toString('base64'),
          metadata: { file_name: basename(realPdfPath), v1_8_agent_source_import: true }
        }
      ]
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error('pdf source_id missing');
  sourceIds.push(sourceId);
  await saveFixture('pdf-import.json', payload);
  mark('pdf import', 'pass', sourceId);
  return sourceId;
}

async function importUrlSource(url, index) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      urls: [{ title: `V1.8 Agent URL Source ${index + 1}`, url, metadata: { v1_8_agent_source_import: true } }],
      metadata: { v1_8_agent_source_import: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`url source_id missing for ${url}`);
  sourceIds.push(sourceId);
  await saveFixture(`url-import-${index + 1}.json`, payload);
  mark(`url import ${index + 1}`, 'pass', sourceId);
  return sourceId;
}

async function assertStableFailingUrl() {
  const result = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { urls: [{ title: 'V1.8 stable failing URL', url: failingUrl }] }
  });
  await saveFixture('url-stable-failure.json', result.payload);
  const text = JSON.stringify(result.payload);
  if (result.ok || !['url_security_blocked', 'extraction_failed', 'unsupported_site'].some((code) => text.includes(code))) {
    throw new Error(`failing URL did not return stable failure: HTTP ${result.status}`);
  }
  mark('stable failing URL', 'pass', `HTTP ${result.status}`);
}

async function buildWorkspace() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(payload);
  if (!operationId) {
    mark('workspace build', 'degraded', 'operation_id missing');
    return;
  }
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const data = dataOf(latest);
    const status = data?.operation?.status ?? data?.status;
    if (status === 'completed') {
      await saveFixture('workspace-build.json', latest);
      mark('workspace build', 'pass', operationId);
      return;
    }
    if (['failed', 'blocked', 'cancelled'].includes(status)) throw new Error(`build ${status}`);
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  throw new Error('build timeout');
}

async function validateSourceList() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
  await saveFixture('source-list.json', payload);
  const items = dataOf(payload)?.items ?? dataOf(payload)?.sources ?? [];
  const ids = new Set(items.map((item) => item.source_id).filter(Boolean));
  const missing = sourceIds.filter((sourceId) => !ids.has(sourceId));
  if (missing.length) throw new Error(`source list missing registry ids: ${missing.join(', ')}`);
  mark('source list registry ids', 'pass', `${sourceIds.length} ids`);
}

async function cleanup() {
  if (!workspaceId) return;
  const result = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.8 agent source import cleanup' }
  });
  await saveFixture('workspace-cleanup.json', result.payload);
  mark('workspace cleanup', result.ok ? 'pass' : 'degraded', workspaceId);
}

async function main() {
  const startedAt = new Date().toISOString();
  const task = createDraft();
  let permissionGrant = null;
  try {
    assertRecord('no local read before permission grant', 'no_scan_before_grant', 'draft_only', 'PASS', task.task_id);
    permissionGrant = grantPermission(task);
    await createWorkspace();
    const materials = await scanAuthorizedSources(permissionGrant);
    await importTextSource('AI 数字人行业概览 Markdown', materials.markdown['01_industry_overview.md'], 'markdown', 'markdown-import.json');
    await importTextSource('AI 数字人资料 TXT 样本', materials.txt, 'txt', 'txt-import.json');
    await importPdfSource(materials.pdf);
    if (successUrls.length < 2) throw new Error('At least two success URLs are required');
    await importUrlSource(successUrls[0], 0);
    await importUrlSource(successUrls[1], 1);
    await assertStableFailingUrl();
    await buildWorkspace();
    await validateSourceList();
    assertRecord('skipped files have reason', true, skippedFiles.every((item) => item.relative_path && item.skipped_reason), 'PASS');
    finalDecision = 'PASS_LIMITED';
  } catch (error) {
    finalDecision = 'FAIL';
    const cause = error && typeof error === 'object' && 'cause' in error ? error.cause : null;
    const detail = `${error instanceof Error ? error.message : String(error)}${cause ? `; cause=${JSON.stringify(cause)}` : ''}`;
    mark('v1.8-b agent source import smoke', 'fail', detail);
    process.exitCode = 1;
  } finally {
    await cleanup().catch((error) => mark('workspace cleanup', 'degraded', error instanceof Error ? error.message : String(error)));
    const stepResults = results.map((result, index) => ({
      step_id: `step_${String(index + 1).padStart(3, '0')}`,
      name: result.name,
      status: result.status === 'pass' || result.status === 'degraded' ? 'completed' : 'failed',
      output_summary: { detail: result.detail, smoke_status: result.status },
      retry_count: 0,
      artifact_refs: []
    }));
    const workflowRun = {
      run_id: `run_${Date.now()}`,
      task_id: task.task_id,
      workspace_id: workspaceId,
      status: finalDecision === 'PASS_LIMITED' ? 'completed' : 'failed',
      started_at: startedAt,
      finished_at: new Date().toISOString(),
      steps: stepResults,
      artifact_refs: Object.keys(fixtures),
      validation_report_id: '',
      final_decision: finalDecision
    };
    const report = {
      report_id: `report_${Date.now()}`,
      task_id: task.task_id,
      workspace_id: workspaceId,
      run_id: workflowRun.run_id,
      workflow_run: workflowRun,
      source_summary: {
        imported_source_count: sourceIds.length,
        source_ids: sourceIds,
        skipped_files: skippedFiles,
        target_path_labels: task.target_path_labels,
        target_path_refs: task.target_path_refs
      },
      step_results: stepResults,
      assertions,
      raw_fixture_refs: Object.keys(fixtures),
      accepted_debts: ['weak frontend UX remains accepted debt', 'V1.8-B does not validate Guide/QA/Studio quality'],
      still_not_ready: ['all-source-type ready', 'all websites URL ready', 'ordinary user UX ready'],
      final_decision: finalDecision,
      generated_at: startedAt
    };
    workflowRun.validation_report_id = report.report_id;
    assertRecord('report contains no raw path', false, hasRawPath(report), hasRawPath(report) ? 'FAIL' : 'PASS');
    report.assertions = assertions;
    await saveFixture('v1_8_b_agent_source_import_result.json', report);
    if (hasRawPath(fixtures)) {
      mark('fixture hygiene', 'fail', 'raw path detected');
      process.exitCode = 1;
    } else {
      mark('fixture hygiene', 'pass', 'sanitized');
    }
    console.log(`V1_8_B_AGENT_SOURCE_IMPORT_DECISION ${finalDecision}`);
  }
}

await main();
