/* global fetch */

import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = `rn-v11-s2-discovery-${Date.now()}`;
const fixturesDir = join(process.cwd(), 'fixtures/real/v1_1/all-source-type-discovery');

const candidates = [
  { source_type: 'text', title: 'Text contract discovery', extension: '.txt' },
  { source_type: 'pdf', title: 'PDF contract discovery', extension: '.pdf' },
  { source_type: 'pptx', title: 'PPTX contract discovery', extension: '.pptx' },
  { source_type: 'json', title: 'JSON contract discovery', extension: '.json' },
  { source_type: 'markdown', title: 'Markdown contract discovery', extension: '.md' },
  { source_type: 'html', title: 'HTML contract discovery', extension: '.html' },
  { source_type: 'video', title: 'Video contract discovery', extension: '.mp4' },
  { source_type: 'audio', title: 'Audio contract discovery', extension: '.mp3' }
];

const results = [];
let workspaceId = '';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  console.log(`${status === 'pass' ? 'PASS' : status === 'warn' ? 'WARN' : 'FAIL'} ${name}${detail ? ` - ${detail}` : ''}`);
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const out = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (lowered === 'raw_path_leak') {
        out[key] = item;
      } else if (
        lowered.includes('path') ||
        lowered.includes('filename') ||
        lowered.includes('stored') ||
        lowered.includes('physical') ||
        lowered.includes('cache')
      ) {
        out[key] = '<redacted>';
      } else {
        out[key] = sanitize(item);
      }
    }
    return out;
  }
  if (typeof value === 'string') {
    return value
      .replaceAll(process.cwd(), '<research-notebook>')
      .replaceAll('/Users/Zhuanz/Desktop/workspace/research-notebook', '<research-notebook>')
      .replaceAll('/Users/Zhuanz/Desktop/workspace/data_service', '<data-service>')
      .replace(/\/private\/tmp\/[^\s",]*/g, '<tmp-redacted>')
      .replace(/\/tmp\/[^\s",]*/g, '<tmp-redacted>');
  }
  return value;
}

function hasRawPath(value) {
  const text = JSON.stringify(value);
  return /(?:^|[^A-Za-z])[A-Za-z]:\\|\/Users(?:\/|")|file:\/\/|cache_path|artifact_path|physical_path|\/private(?:\/|")|\/tmp(?:\/|")/.test(text);
}

async function saveFixture(name, payload) {
  await mkdir(fixturesDir, { recursive: true });
  await writeFile(join(fixturesDir, name), `${JSON.stringify(sanitize(payload), null, 2)}\n`);
}

async function request(path, init = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: init.method ?? 'GET',
    headers: { 'content-type': 'application/json', ...(init.headers ?? {}) },
    body: init.body ? JSON.stringify(init.body) : undefined
  });
  let payload = null;
  try {
    payload = await response.json();
  } catch {
    payload = { status: 'error', raw: await response.text().catch(() => '') };
  }
  return { ok: response.ok, status: response.status, payload };
}

async function mustRequest(path, init = {}) {
  const response = await request(path, init);
  if (!response.ok) {
    throw new Error(`${init.method ?? 'GET'} ${path} failed: HTTP ${response.status} ${JSON.stringify(response.payload).slice(0, 300)}`);
  }
  return response.payload;
}

function dataOf(payload) {
  return payload?.data ?? payload;
}

function readWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace_id ?? data?.workspace?.workspace_id ?? payload?.workspace_id;
}

function readSourceId(payload) {
  const data = dataOf(payload);
  return data?.source?.source_id ?? data?.sources?.[0]?.source_id ?? payload?.source_id;
}

function readSource(payload) {
  const data = dataOf(payload);
  return data?.source ?? payload?.source ?? data;
}

function readPreview(payload) {
  return dataOf(payload)?.preview ?? payload?.preview ?? dataOf(payload);
}

function readUnits(payload) {
  return dataOf(payload)?.units ?? payload?.units ?? dataOf(payload);
}

function readTrace(payload) {
  return dataOf(payload)?.trace ?? payload?.trace ?? dataOf(payload);
}

function classifyCapability(manifest, sourceType) {
  const entry = manifest?.supported_source_types?.find((item) => item?.source_type === sourceType);
  if (!entry) return { status: 'NOT_READY', preview: 'none', locators: [] };
  return { status: entry.preview === 'none' ? 'UNSUPPORTED' : 'PASS', preview: entry.preview, locators: entry.locators ?? [] };
}

function classifyPreview(preview) {
  if (preview?.preview_available === true) return 'PASS';
  if (preview?.unsupported_reason === 'source_type_not_supported') return 'UNSUPPORTED';
  if (preview?.unsupported_reason) return 'NOT_READY';
  return 'BLOCKED_BY_BACKEND_CONTRACT';
}

function classifyUnits(units) {
  if (Array.isArray(units?.items) && units.items.length > 0) return 'PASS';
  if (units?.unsupported_reason === 'source_type_not_supported') return 'UNSUPPORTED';
  if (Array.isArray(units?.items) && units.items.length === 0) return 'LIMITED_PASS';
  return 'BLOCKED_BY_BACKEND_CONTRACT';
}

function classifyTrace(traceResponse, trace) {
  if (traceResponse.ok && trace?.trace_available === true) return 'LIMITED_PASS';
  if (traceResponse.ok && trace?.trace_available === false) return 'UNSUPPORTED';
  if (traceResponse.status === 404) return 'NOT_READY';
  return 'BLOCKED_BY_BACKEND_CONTRACT';
}

try {
  const probe = await request('/api/workspaces');
  if (!probe.ok) throw new Error(`target route probe failed: HTTP ${probe.status}`);
  mark('target route probe', 'pass', baseUrl);

  const created = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: `${prefix}-workspace` }
  });
  workspaceId = readWorkspaceId(created);
  if (!workspaceId) throw new Error('workspace_id missing after workspace create');
  mark('workspace create', 'pass', workspaceId);

  const capabilityPayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/capabilities`);
  const manifest = dataOf(capabilityPayload)?.manifest ?? capabilityPayload?.manifest;
  if (!manifest?.capabilities || !Array.isArray(manifest.supported_source_types)) {
    throw new Error('capability manifest missing supported_source_types');
  }
  mark('capability manifest', 'pass', manifest.supported_source_types.map((item) => `${item.source_type}:${item.preview}`).join(', '));
  await saveFixture('capability-manifest.json', capabilityPayload);

  const candidateResults = [];
  for (const candidate of candidates) {
    const sourcePayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
      method: 'POST',
      body: {
        texts: [
          {
            title: candidate.title,
            content: `${candidate.title} for V1.1-S2 all-source-type contract discovery. This payload is synthetic and contains no private content.`,
            metadata: {
              stage: 'v1.1-s2-all-source-type-contract-discovery',
              source_type: candidate.source_type,
              extension: candidate.extension
            }
          }
        ],
        metadata: {
          stage: 'v1.1-s2-all-source-type-contract-discovery',
          source_type: candidate.source_type,
          extension: candidate.extension
        }
      }
    });
    const sourceId = readSourceId(sourcePayload);
    if (!sourceId || !/^src_[A-Za-z0-9]{8,64}$/.test(sourceId)) throw new Error(`${candidate.source_type} source_id is not registry-shaped`);

    const sourceDetailPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}`
    );
    const source = readSource(sourceDetailPayload);

    const previewPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/preview`
    );
    const preview = readPreview(previewPayload);

    const unitsPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units?limit=20`
    );
    const units = readUnits(unitsPayload);

    const traceResponse = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/trace`);
    const trace = traceResponse.ok ? readTrace(traceResponse.payload) : null;

    const rawPathLeak =
      hasRawPath(sourceDetailPayload) || hasRawPath(previewPayload) || hasRawPath(unitsPayload) || (traceResponse.payload && hasRawPath(traceResponse.payload));
    if (rawPathLeak) throw new Error(`${candidate.source_type} response leaked raw path`);

    const capability = classifyCapability(manifest, candidate.source_type);
    const result = {
      source_type: candidate.source_type,
      source_id: sourceId,
      observed_source_type: source?.source_type,
      capability_manifest: capability,
      source_create: 'PASS_REGISTRY_SOURCE_ID',
      native_ingestion: candidate.source_type === 'text' ? 'PASS_TEXT_SOURCE' : 'NOT_VERIFIED_METADATA_ONLY',
      source_preview: classifyPreview(preview),
      document_units: classifyUnits(units),
      evidence_spans: candidate.source_type === 'text' && classifyUnits(units) === 'PASS' ? 'PASS_TEXT_ROUTE_AVAILABLE' : 'NOT_READY_NOT_SMOKED',
      source_trace: classifyTrace(traceResponse, trace),
      unsupported_reason: preview?.unsupported_reason ?? units?.unsupported_reason,
      trace_http_status: traceResponse.status,
      raw_path_leak: false
    };

    candidateResults.push(result);
    await saveFixture(`${candidate.source_type}-source-detail.json`, sourceDetailPayload);
    await saveFixture(`${candidate.source_type}-preview.json`, previewPayload);
    await saveFixture(`${candidate.source_type}-units.json`, unitsPayload);
    await saveFixture(`${candidate.source_type}-trace.json`, traceResponse.payload);
    mark(`discover ${candidate.source_type}`, 'pass', `${result.source_preview}/${result.document_units}/${result.source_trace}`);
  }

  const summary = {
    declaration: 'CONTRACT_DISCOVERY_COMPLETE',
    workspace_id: workspaceId,
    candidates: candidateResults,
    results
  };
  await saveFixture('s2-all-source-type-discovery-result.json', summary);
  console.log('S2_ALL_SOURCE_TYPE_DISCOVERY_DECISION CONTRACT_DISCOVERY_COMPLETE');
} catch (error) {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    const close = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
    if (close.ok) mark('workspace archive cleanup', 'pass', workspaceId);
    else mark('workspace archive cleanup', 'fail', `HTTP ${close.status}`);
  }
}
