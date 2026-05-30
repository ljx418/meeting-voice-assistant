/* global fetch, setTimeout */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V16_URL_PREFIX ?? `rn-v16-url-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_6', 'url-extraction');
const successUrls = (process.env.RN_V16_URL_SUCCESS_URLS ?? 'http://example.com/,http://example.org/')
  .split(',')
  .map((item) => item.trim())
  .filter(Boolean);
const blockedUrl = process.env.RN_V16_URL_BLOCKED_URL ?? 'http://127.0.0.1:8003/';
const maxPollMs = Number(process.env.RN_V16_URL_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V16_URL_POLL_INTERVAL_MS ?? 1_000);

const results = [];
const fixtures = {};
const sourceIds = [];
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
    return value.replaceAll('/Users', '[home]').replaceAll('/private/tmp', '[tmp]').replaceAll('/tmp', '[tmp]').replaceAll('file://', 'file-redacted://');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  await Promise.all(
    Object.entries(fixtures).map(([name, payload]) => writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n'))
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
    body: { name: prefix, owner: 'v1.6-url-smoke', tags: ['v1.6', 'url-extraction'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  fixtures['workspace-create.json'] = payload;
  mark('workspace create', 'pass', workspaceId);
}

async function importUrlSource(url, index) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      urls: [{ title: `V1.6 URL Source ${index + 1}`, url, metadata: { v1_6_url_smoke: true } }],
      metadata: { v1_6_url_smoke: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`URL source_id missing for ${url}`);
  sourceIds.push(sourceId);
  fixtures[`url-import-${index + 1}.json`] = payload;
  mark(`url import ${index + 1}`, 'pass', sourceId);
}

async function assertBlockedUrl() {
  const result = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: { urls: [{ title: 'Blocked URL', url: blockedUrl }] }
  });
  fixtures['url-security-blocked.json'] = result.payload;
  if (result.status !== 422 || !JSON.stringify(result.payload).includes('url_security_blocked')) {
    throw new Error(`blocked URL did not return url_security_blocked: HTTP ${result.status}`);
  }
  mark('unsafe URL blocked', 'pass', 'url_security_blocked');
}

async function buildWorkspace() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(payload);
  if (!operationId) {
    mark('workspace build', 'degraded', 'operation_id missing; continuing');
    return;
  }
  const result = await pollOperation(operationId);
  fixtures['workspace-build.json'] = result.payload;
  if (result.status !== 'completed') throw new Error(`build did not complete: ${result.status}`);
  mark('workspace build', 'pass', operationId);
}

async function validateSourceChain(sourceId) {
  const preview = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/preview`);
  fixtures[`source-${sourceId}-preview.json`] = preview;
  const previewData = dataOf(preview)?.preview;
  if (previewData?.source_type !== 'url' || !previewData?.preview_available) throw new Error('URL preview unavailable');
  if (hasRawPath(preview)) throw new Error('preview contains raw path');

  const unitsPayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units`);
  fixtures[`source-${sourceId}-units.json`] = unitsPayload;
  const unitsRaw = dataOf(unitsPayload)?.units;
  const unit = Array.isArray(unitsRaw) ? unitsRaw[0] : unitsRaw?.items?.[0];
  if (!unit?.unit_id) throw new Error('URL unit missing');
  mark(`source chain ${sourceId}`, 'pass', unit.unit_id);
}

function firstEvidence(payload) {
  const data = dataOf(payload);
  return data?.answer?.evidence?.[0] ?? data?.evidence?.[0] ?? null;
}

async function validateQueryAndEvidence() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
    method: 'POST',
    body: { query: 'What is Example Domain used for?', top_k: 6 }
  });
  fixtures['url-query.json'] = payload;
  const evidence = firstEvidence(payload);
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) throw new Error('query evidence missing source_id/unit_id/evidence_id');
  const span = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
  );
  fixtures['url-query-evidence-span.json'] = span;
  const spanData = dataOf(span)?.evidence_span;
  if (spanData?.source_id !== evidence.source_id || spanData?.unit_id !== evidence.unit_id) throw new Error('EvidenceSpan mismatch');
  mark('query evidence span', 'pass', evidence.evidence_id);
}

async function validateGuideAndStudio() {
  const guide = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/guide`);
  fixtures['url-guide.json'] = guide;
  if (!Array.isArray(dataOf(guide)?.guide?.evidence_refs) || dataOf(guide).guide.evidence_refs.length < 1) throw new Error('guide URL evidence missing');
  mark('guide URL evidence', 'pass', `${dataOf(guide).guide.evidence_refs.length} refs`);

  const studio = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/studio/artifacts`, {
    method: 'POST',
    body: { artifact_type: 'faq' }
  });
  fixtures['url-studio-faq.json'] = studio;
  const artifact = dataOf(studio)?.artifact;
  if (!artifact?.artifact_available || !Array.isArray(artifact.evidence_refs) || artifact.evidence_refs.length < 1) {
    throw new Error('studio URL evidence missing');
  }
  mark('studio URL evidence', 'pass', `${artifact.evidence_refs.length} refs`);
}

async function cleanup() {
  if (!workspaceId) return;
  const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.6 url smoke cleanup' }
  });
  fixtures['workspace-cleanup.json'] = payload.payload;
  mark('workspace cleanup', payload.ok ? 'pass' : 'degraded', workspaceId);
}

async function main() {
  try {
    if (successUrls.length < 2) throw new Error('At least two success URLs are required');
    await createWorkspace();
    await assertBlockedUrl();
    for (const [index, url] of successUrls.entries()) {
      await importUrlSource(url, index);
    }
    await buildWorkspace();
    for (const sourceId of sourceIds) {
      await validateSourceChain(sourceId);
    }
    await validateQueryAndEvidence();
    await validateGuideAndStudio();
    finalDecision = 'PASS_LIMITED';
  } catch (error) {
    finalDecision = String(error?.message ?? '').includes('fetch') ? 'BLOCKED_BY_NETWORK_OR_SITE' : 'FAIL';
    mark('v1.6-a-url smoke', 'fail', error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  } finally {
    await cleanup().catch((error) => mark('workspace cleanup', 'degraded', error instanceof Error ? error.message : String(error)));
    fixtures['v1_6_a_url_extraction_smoke_result.json'] = {
      final_decision: finalDecision,
      base_url: baseUrl,
      success_urls: successUrls,
      blocked_url: blockedUrl,
      workspace_id: workspaceId,
      source_ids: sourceIds,
      results,
      still_not_ready: ['all websites URL extraction', 'login/private/paywalled pages', 'javascript rendered pages', 'batch web crawl']
    };
    await saveFixtures();
    console.log(`FINAL ${finalDecision}`);
  }
}

await main();
