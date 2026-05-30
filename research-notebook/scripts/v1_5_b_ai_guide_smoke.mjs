/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V15_GUIDE_PREFIX ?? `rn-v15-ai-guide-${Date.now()}`;
const materialDir =
  process.env.RN_V15_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V15_DIGITAL_HUMAN_PDF ??
  join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_5', 'ai-guide');
const maxPollMs = Number(process.env.RN_V15_GUIDE_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V15_GUIDE_POLL_INTERVAL_MS ?? 1_000);

const results = [];
const fixtures = {};
let workspaceId = '';
let finalDecision = 'FAIL';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
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
        lowered.endsWith('_path') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack')
      ) {
        if (lowered === 'api_key_configured') output[key] = Boolean(item);
        continue;
      }
      output[key] = sanitize(item);
    }
    return output;
  }
  if (typeof value === 'string') {
    return value
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]')
      .replaceAll('/Users', '[home]')
      .replaceAll('/private/tmp', '[tmp]')
      .replaceAll('/tmp', '[tmp]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  await Promise.all(
    Object.entries(fixtures).map(([name, payload]) =>
      writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n')
    )
  );
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

async function pollOperation(operationId) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const data = dataOf(latest);
    const status = data?.operation?.status ?? data?.status;
    if (['completed', 'failed', 'blocked', 'cancelled'].includes(status)) return { status, payload: latest };
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return { status: 'timeout', payload: latest };
}

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.5-ai-guide-smoke', tags: ['v1.5', 'ai-guide'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  fixtures['workspace-create.json'] = payload;
  mark('workspace create', 'pass', workspaceId);
}

async function importTextSource(title, content, metadata = {}) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [{ title, content, metadata: { ...metadata, v1_5_ai_guide: true } }],
      metadata: { ...metadata, v1_5_ai_guide: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${title} source_id missing`);
  return { sourceId, payload };
}

async function importPdfSource() {
  const contentBase64 = (await readFile(realPdfPath)).toString('base64');
  const result = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      metadata: {
        title: 'AI 数字人产业发展报告 PDF',
        source_type: 'pdf',
        file_name: basename(realPdfPath),
        v1_5_ai_guide: true
      },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: contentBase64,
          metadata: { file_name: basename(realPdfPath), v1_5_ai_guide: true }
        }
      ]
    }
  });
  const sourceId = extractSourceId(result);
  if (!sourceId) throw new Error('pdf source_id missing');
  return { sourceId, payload: result };
}

async function buildWorkspace() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(payload);
  if (!operationId) {
    mark('workspace build', 'degraded', 'operation_id missing; continuing with immediate guide request');
    return;
  }
  const result = await pollOperation(operationId);
  fixtures['workspace-build.json'] = result.payload;
  if (result.status !== 'completed') throw new Error(`build did not complete: ${result.status}`);
  mark('workspace build', 'pass', operationId);
}

function validateGuide(payload) {
  const guide = dataOf(payload)?.guide;
  if (!guide?.guide_available) throw new Error('guide_available is false');
  if (guide.generation_metadata?.fallback_mode !== false) throw new Error('AI Guide used fallback mode');
  if (guide.generation_metadata?.provider_name !== 'minimax') throw new Error('Guide provider is not minimax');
  if (!String(guide.overview ?? '').includes('数字人')) throw new Error('overview does not mention 数字人');
  if (!Array.isArray(guide.key_topics) || guide.key_topics.length < 3) throw new Error('key_topics length < 3');
  if (!Array.isArray(guide.suggested_questions) || guide.suggested_questions.length < 3) {
    throw new Error('suggested_questions length < 3');
  }
  if (!Array.isArray(guide.evidence_refs) || guide.evidence_refs.length < 1) throw new Error('guide evidence_refs missing');
  for (const topic of guide.key_topics) {
    if (!Array.isArray(topic.evidence_refs) || topic.evidence_refs.length < 1) {
      throw new Error(`topic missing evidence_refs: ${topic.title ?? '<untitled>'}`);
    }
  }
  if (hasRawPath(payload)) throw new Error('guide payload contains raw path');
}

async function cleanup() {
  if (!workspaceId) return;
  try {
    const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
      method: 'POST',
      body: { reason: 'v1.5 ai guide smoke cleanup' }
    });
    fixtures['workspace-archive.json'] = payload;
    mark('cleanup', 'pass', workspaceId);
  } catch (error) {
    mark('cleanup', 'fail', error instanceof Error ? error.message : String(error));
  }
}

async function main() {
  try {
    const md = await readFile(join(materialDir, '01_industry_overview.md'), 'utf8');
    const tech = await readFile(join(materialDir, '02_technology_trends.md'), 'utf8');
    await readFile(realPdfPath);
    mark('material check', 'pass', 'AI digital human Markdown/PDF available');

    await mustRequest('/api/workspaces');
    mark('target route probe', 'pass', baseUrl);
    await createWorkspace();

    const mdSource = await importTextSource('AI 数字人行业概览 Markdown', md, { source_format: 'markdown' });
    fixtures['markdown-import.json'] = mdSource.payload;
    mark('markdown import', 'pass', mdSource.sourceId);

    const techSource = await importTextSource('AI 数字人技术趋势 Markdown', tech, { source_format: 'markdown' });
    fixtures['technology-markdown-import.json'] = techSource.payload;
    mark('technology markdown import', 'pass', techSource.sourceId);

    const pdfSource = await importPdfSource();
    fixtures['pdf-import.json'] = pdfSource.payload;
    mark('pdf import', 'pass', pdfSource.sourceId);

    await buildWorkspace();

    const guidePayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/guide`);
    fixtures['ai-guide-success.json'] = guidePayload;
    validateGuide(guidePayload);
    mark('ai guide validation', 'pass', 'overview/key_topics/questions/evidence/metadata');

    finalDecision = 'PASS';
  } catch (error) {
    finalDecision = 'FAIL';
    mark('smoke exception', 'fail', error instanceof Error ? error.message : String(error));
  } finally {
    await cleanup();
    fixtures['v1_5_b_ai_guide_smoke_result.json'] = {
      generated_at: new Date().toISOString(),
      base_url: baseUrl,
      workspace_id: workspaceId || null,
      results,
      final_decision: finalDecision,
      declaration:
        finalDecision === 'PASS'
          ? 'V1.5-B AI Notebook Guide is quality-smoke-ready for the AI digital human P0 dataset.'
          : 'V1.5-B AI Notebook Guide remains NOT_READY.'
    };
    await saveFixtures();
  }
  if (finalDecision !== 'PASS') process.exitCode = 1;
}

await main();
