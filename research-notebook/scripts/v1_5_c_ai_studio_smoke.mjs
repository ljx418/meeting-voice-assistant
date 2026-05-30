/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V15_STUDIO_PREFIX ?? `rn-v15-ai-studio-${Date.now()}`;
const materialDir =
  process.env.RN_V15_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V15_DIGITAL_HUMAN_PDF ??
  join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_5', 'ai-studio');
const maxPollMs = Number(process.env.RN_V15_STUDIO_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V15_STUDIO_POLL_INTERVAL_MS ?? 1_000);
const providerRetryDelayMs = Number(process.env.RN_V15_STUDIO_PROVIDER_RETRY_DELAY_MS ?? 2_500);
const providerMaxAttempts = Number(process.env.RN_V15_STUDIO_PROVIDER_MAX_ATTEMPTS ?? 3);
const artifactTypes = ['notes', 'study_guide', 'briefing_doc', 'faq'];

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
    body: { name: prefix, owner: 'v1.5-ai-studio-smoke', tags: ['v1.5', 'ai-studio'] }
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
      texts: [{ title, content, metadata: { ...metadata, v1_5_ai_studio: true } }],
      metadata: { ...metadata, v1_5_ai_studio: true }
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
        v1_5_ai_studio: true
      },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: contentBase64,
          metadata: { file_name: basename(realPdfPath), v1_5_ai_studio: true }
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
    mark('workspace build', 'degraded', 'operation_id missing; continuing with Studio request');
    return;
  }
  const result = await pollOperation(operationId);
  fixtures['workspace-build.json'] = result.payload;
  if (result.status !== 'completed') throw new Error(`build did not complete: ${result.status}`);
  mark('workspace build', 'pass', operationId);
}

function validateArtifact(payload, artifactType) {
  const artifact = dataOf(payload)?.artifact;
  if (!artifact?.artifact_available) throw new Error(`${artifactType} artifact_available is false`);
  if (artifact.generation_metadata?.fallback_mode !== false) throw new Error(`${artifactType} used fallback mode`);
  if (artifact.generation_metadata?.provider_name !== 'minimax') throw new Error(`${artifactType} provider is not minimax`);
  if (artifact.generation_metadata?.artifact_type !== artifactType) throw new Error(`${artifactType} metadata artifact_type mismatch`);
  if (!String(artifact.summary ?? '').trim()) throw new Error(`${artifactType} summary missing`);
  if (!Array.isArray(artifact.evidence_refs) || artifact.evidence_refs.length < 1) throw new Error(`${artifactType} evidence_refs missing`);
  const minSections = artifactType === 'study_guide' || artifactType === 'faq' ? 3 : 2;
  if (!Array.isArray(artifact.sections) || artifact.sections.length < minSections) {
    throw new Error(`${artifactType} sections length < ${minSections}`);
  }
  for (const section of artifact.sections) {
    if (!String(section.title ?? '').trim() || !String(section.content ?? '').trim()) {
      throw new Error(`${artifactType} section missing title/content`);
    }
    if (!Array.isArray(section.evidence_refs) || section.evidence_refs.length < 1) {
      throw new Error(`${artifactType} section missing evidence_refs: ${section.title ?? '<untitled>'}`);
    }
  }
  if (hasRawPath(payload)) throw new Error(`${artifactType} payload contains raw path`);
}

function isRetryableProviderFallback(payload) {
  const errorCode = dataOf(payload)?.artifact?.generation_metadata?.error_code;
  return ['provider_timeout', 'provider_unavailable', 'rate_limited'].includes(errorCode);
}

async function requestStudioArtifact(artifactType) {
  let latest = null;
  for (let attempt = 1; attempt <= providerMaxAttempts; attempt += 1) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/studio/artifacts`, {
      method: 'POST',
      body: { artifact_type: artifactType }
    });
    const artifact = dataOf(latest)?.artifact;
    if (artifact?.generation_metadata?.fallback_mode !== true || !isRetryableProviderFallback(latest)) {
      return latest;
    }
    mark(`studio ${artifactType} retryable fallback`, 'degraded', `${artifact.generation_metadata.error_code}; retry ${attempt}/${providerMaxAttempts}`);
    if (attempt < providerMaxAttempts) {
      await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
    }
  }
  return latest;
}

async function cleanup() {
  if (!workspaceId) return;
  try {
    const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
      method: 'POST',
      body: { reason: 'v1.5 ai studio smoke cleanup' }
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

    for (const artifactType of artifactTypes) {
      const payload = await requestStudioArtifact(artifactType);
      fixtures[`studio-${artifactType}-success.json`] = payload;
      validateArtifact(payload, artifactType);
      mark(`studio ${artifactType}`, 'pass', 'AI output/citations/metadata');
      await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
    }

    finalDecision = 'PASS';
  } catch (error) {
    finalDecision = 'FAIL';
    mark('smoke exception', 'fail', error instanceof Error ? error.message : String(error));
  } finally {
    await cleanup();
    fixtures['v1_5_c_ai_studio_smoke_result.json'] = {
      generated_at: new Date().toISOString(),
      base_url: baseUrl,
      workspace_id: workspaceId || null,
      artifact_types: artifactTypes,
      results,
      final_decision: finalDecision,
      declaration:
        finalDecision === 'PASS'
          ? 'V1.5-C AI Studio outputs are quality-smoke-ready for the AI digital human P0 dataset.'
          : 'V1.5-C AI Studio outputs remain NOT_READY.'
    };
    await saveFixtures();
  }
  if (finalDecision !== 'PASS') process.exitCode = 1;
}

await main();
