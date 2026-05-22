/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V11_RC4_WORKSPACE_PREFIX ?? `rn-v11-rc4-trace-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_1', 'source-trace');

const results = [];
const fixtures = {};
let workspaceId = '';
let sourceId = '';
let traceDecision = 'NOT_READY';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const out = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (
        lowered === 'path' ||
        lowered === 'paths' ||
        lowered.endsWith('_path') ||
        lowered.endsWith('_paths') ||
        lowered.includes('physical') ||
        lowered.includes('cache') ||
        lowered.includes('stack')
      ) {
        continue;
      }
      out[key] = sanitize(item);
    }
    return out;
  }
  if (typeof value === 'string') {
    return value
      .replaceAll('/private/tmp', '[tmp]')
      .replaceAll('/tmp', '[tmp]')
      .replaceAll('/Users', '[home]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
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

function extractSourceList(payload) {
  const data = dataOf(payload);
  if (Array.isArray(data?.sources)) return data.sources;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data)) return data;
  return [];
}

function extractQueryEvidence(payload) {
  const data = dataOf(payload);
  if (Array.isArray(data?.evidence)) return data.evidence;
  if (Array.isArray(data?.evidence_refs)) return data.evidence_refs;
  if (Array.isArray(data?.sources)) return data.sources;
  if (Array.isArray(data?.hits)) return data.hits;
  if (Array.isArray(payload?.hits)) return payload.hits;
  return [];
}

function hasRawPath(value) {
  const text = JSON.stringify(value);
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(text);
}

function assertRegistrySourceId(id) {
  if (!id || typeof id !== 'string') throw new Error('registry source_id missing');
  if (id.includes('://') || id.includes('/') || id.startsWith('file:') || id.startsWith('artifact:')) {
    throw new Error(`source_id is not a registry source id: ${id}`);
  }
}

function classifyTrace(result) {
  if (hasRawPath(result.payload)) {
    return { decision: 'BLOCKED_BY_BACKEND_CONTRACT', status: 'fail', detail: 'trace response leaked raw path-like values' };
  }
  if (result.ok) {
    const data = dataOf(result.payload);
    const trace = data?.trace && typeof data.trace === 'object' ? data.trace : data;
    const provenance = Array.isArray(trace?.provenance) ? trace.provenance : [];
    const hasTrace = provenance.length > 0 || Boolean(trace?.summary) || Boolean(trace?.trace_summary);
    if (hasTrace) return { decision: 'PASS', status: 'pass', detail: `HTTP ${result.status}` };
    return { decision: 'BLOCKED_BY_BACKEND_CONTRACT', status: 'fail', detail: 'trace route returned 200 without trace/provenance payload' };
  }
  if (result.status === 404) {
    return { decision: 'NOT_READY', status: 'degraded', detail: 'HTTP 404 registry source trace remains unavailable' };
  }
  if (result.status === 400 || result.status === 422 || result.status === 503) {
    return { decision: 'DEGRADED_ACCEPTED', status: 'degraded', detail: `HTTP ${result.status} stable unavailable/error response` };
  }
  return { decision: 'BLOCKED_BY_BACKEND_CONTRACT', status: 'fail', detail: `HTTP ${result.status} unexpected trace response` };
}

try {
  const probe = await request('/api/workspaces');
  if (!probe.ok) throw new Error(`target route probe failed: HTTP ${probe.status}`);
  mark('target route probe', 'pass', baseUrl);

  const created = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: `${prefix}-workspace` }
  });
  workspaceId = extractWorkspaceId(created);
  if (!workspaceId) throw new Error('workspace_id missing after workspace create');
  mark('workspace create', 'pass', workspaceId);

  const sourceCreated = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: `${prefix} Source Trace Source`,
          content:
            'Source trace contract re-smoke should prove that a registry source id can open source-level provenance. The answer should preserve evidence if source trace is unavailable.',
          metadata: { stage: 'v1.1-rc4-source-trace' }
        }
      ],
      metadata: { stage: 'v1.1-rc4-source-trace' }
    }
  });
  sourceId = extractSourceId(sourceCreated);
  assertRegistrySourceId(sourceId);
  mark('source create', 'pass', sourceId);

  fixtures['source-list.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
  const listedSource = extractSourceList(fixtures['source-list.json']).find((source) => source?.source_id === sourceId);
  if (!listedSource) throw new Error('created registry source_id was not returned by source list');
  mark('source list registry id', 'pass', sourceId);

  fixtures['source-detail.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}`);
  const detailSourceId = extractSourceId(fixtures['source-detail.json']);
  if (detailSourceId !== sourceId) throw new Error(`source get returned unexpected source_id ${detailSourceId}`);
  mark('source get registry id', 'pass', sourceId);

  const traceResult = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/trace`);
  const traceClassification = classifyTrace(traceResult);
  traceDecision = traceClassification.decision;
  fixtures[traceResult.ok ? 'source-trace-success.json' : traceResult.status === 404 ? 'source-trace-404.json' : 'source-trace-unavailable.json'] = {
    status: traceResult.status,
    payload: traceResult.payload
  };
  mark('direct source trace', traceClassification.status, traceClassification.detail);
  if (traceClassification.status === 'fail') throw new Error(traceClassification.detail);

  const query = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
    method: 'POST',
    body: {
      query: 'What should the answer preserve if source trace is unavailable?',
      top_k: 5
    }
  });
  if (query.ok) {
    const evidence = extractQueryEvidence(query.payload);
    const traceable = evidence.find((item) => item?.source_id === sourceId || item?.sourceId === sourceId || item?.source === sourceId);
    fixtures[traceable ? 'query-evidence-traceable-source-id.json' : 'query-evidence-source-ref-only.json'] = query.payload;
    mark('workspace query evidence mapping', traceable ? 'pass' : 'degraded', traceable ? 'registry source id observed' : 'no traceable registry source id');
  } else {
    fixtures['query-evidence-source-ref-only.json'] = { status: query.status, payload: query.payload };
    mark('workspace query evidence mapping', 'degraded', `HTTP ${query.status}`);
  }

  fixtures['rc4-source-trace-result.json'] = {
    decision: traceDecision,
    workspace_id: workspaceId,
    source_id: sourceId,
    direct_trace_status: traceResult.status,
    results
  };

  await saveFixtures();
  mark('fixtures saved', 'pass', fixtureDir);
  console.log(`RC4_SOURCE_TRACE_DECISION ${traceDecision}`);
} catch (error) {
  fixtures['rc4-source-trace-result.json'] = {
    decision: traceDecision === 'PASS' ? 'BLOCKED_BY_BACKEND_CONTRACT' : traceDecision,
    workspace_id: workspaceId,
    source_id: sourceId,
    error: error instanceof Error ? error.message : String(error),
    results
  };
  await saveFixtures().catch(() => undefined);
  mark('v1.1-rc4 source trace smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'degraded', error instanceof Error ? error.message : String(error));
    }
  }
}
