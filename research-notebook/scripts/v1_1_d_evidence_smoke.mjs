/* global fetch, setTimeout */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V11D_WORKSPACE_PREFIX ?? `rn-v11d-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_1', 'evidence-spans');
const maxPollMs = Number(process.env.RN_V11D_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V11D_POLL_INTERVAL_MS ?? 1_000);

const results = [];
const fixtures = {};
let workspaceId = '';

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
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status} ${path}`);
    error.status = response.status;
    error.payload = payload;
    throw error;
  }
  return payload;
}

function dataOf(payload) {
  return payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

function arrayFrom(...candidates) {
  for (const candidate of candidates) {
    if (Array.isArray(candidate)) return candidate;
  }
  return [];
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
  return payload?.operation_id ?? payload?.data?.operation_id ?? payload?.data?.operation?.operation_id;
}

function extractManifest(payload) {
  const data = dataOf(payload);
  return data?.manifest ?? data;
}

function extractUnits(payload) {
  const data = dataOf(payload);
  const units = data?.units ?? data;
  return {
    items: Array.isArray(units?.items) ? units.items : [],
    hasMore: Boolean(units?.has_more),
    nextCursor: typeof units?.next_cursor === 'string' ? units.next_cursor : null
  };
}

function extractUnit(payload) {
  const data = dataOf(payload);
  return data?.unit ?? data;
}

function extractQueryEvidence(payload) {
  const data = dataOf(payload);
  return arrayFrom(data?.evidence, data?.evidence_refs, data?.sources, data?.hits, data?.items, data?.results);
}

function findJumpableEvidence(payload) {
  const evidence = extractQueryEvidence(payload);
  return evidence.find((item) => item?.source_id && item?.unit_id && item?.evidence_id);
}

function extractEvidenceSpan(payload) {
  const data = dataOf(payload);
  return data?.evidence_span ?? data;
}

async function pollOperation(workspaceId, operationId) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const status = latest?.status ?? latest?.data?.status ?? latest?.data?.operation?.status;
    if (status === 'completed' || status === 'failed' || status === 'cancelled' || status === 'blocked') return { status, payload: latest };
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return { status: 'poll_timeout', payload: latest };
}

function assertCapability(manifest, key) {
  if (manifest?.capabilities?.[key] !== true) {
    throw new Error(`capability ${key} is not true`);
  }
}

function assertSpan(span, evidence) {
  if (span.evidence_id !== evidence.evidence_id) throw new Error('EvidenceSpan evidence_id mismatch');
  if (span.source_id !== evidence.source_id) throw new Error('EvidenceSpan source_id mismatch');
  if (span.unit_id !== evidence.unit_id) throw new Error('EvidenceSpan unit_id mismatch');
  if (span.offset_basis !== 'normalized_text') throw new Error(`unsupported offset_basis ${span.offset_basis}`);
  if (span.offset_range !== 'half_open') throw new Error(`unsupported offset_range ${span.offset_range}`);
  if (span.text_basis !== 'document_unit_text') throw new Error(`unsupported text_basis ${span.text_basis}`);
  if (!Number.isFinite(span.start_offset) || !Number.isFinite(span.end_offset)) throw new Error('EvidenceSpan offsets missing');
  if (span.start_offset < 0 || span.end_offset <= span.start_offset) throw new Error('EvidenceSpan offsets invalid');
}

try {
  try {
    await request('/api/workspaces');
    mark('target route probe', 'pass', baseUrl);
  } catch (error) {
    mark('target route probe', 'fail', error.message);
    throw error;
  }

  const created = await request('/api/workspaces', {
    method: 'POST',
    body: { name: `${prefix}-workspace` }
  });
  workspaceId = extractWorkspaceId(created);
  if (!workspaceId) throw new Error('workspace_id missing after workspace create');
  mark('workspace create', 'pass', workspaceId);

  const sourceCreated = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: `${prefix} EvidenceSpan source`,
          content:
            'Queues absorb burst traffic during release validation. EvidenceSpan navigation should highlight this sentence after query evidence resolves to a source id, unit id, and evidence id.',
          metadata: { stage: 'v1.1-d-real-smoke' }
        }
      ],
      metadata: { stage: 'v1.1-d-real-smoke' }
    }
  });
  const sourceId = extractSourceId(sourceCreated);
  if (!sourceId) throw new Error('source_id missing after source create');
  mark('source create', 'pass', sourceId);

  fixtures['capability-manifest-evidence-spans.json'] = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/capabilities`);
  const manifest = extractManifest(fixtures['capability-manifest-evidence-spans.json']);
  for (const key of ['document_units', 'unit_level_navigation', 'evidence_spans', 'precise_span_highlight', 'citation_backjump']) {
    assertCapability(manifest, key);
  }
  mark('capability manifest evidence flags', 'pass');

  fixtures['document-units-list-success.json'] = await request(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units?limit=50`
  );
  const units = extractUnits(fixtures['document-units-list-success.json']);
  if (units.items.length === 0) throw new Error('unit list returned no items');
  const firstUnit = units.items[0];
  if (!firstUnit.unit_id) throw new Error('unit_id missing from first unit');
  mark('unit list', 'pass', firstUnit.unit_id);

  fixtures['document-unit-detail-success.json'] = await request(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units/${encodeURIComponent(firstUnit.unit_id)}`
  );
  const unit = extractUnit(fixtures['document-unit-detail-success.json']);
  if (!unit.text_preview || !unit.content_type) throw new Error('unit detail missing text_preview or content_type');
  mark('unit detail', 'pass', unit.content_type);

  const build = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(build);
  if (operationId) {
    const buildResult = await pollOperation(workspaceId, operationId);
    mark('workspace build polling', buildResult.status === 'completed' ? 'pass' : 'degraded', buildResult.status ?? 'unknown');
  } else {
    mark('workspace build polling', 'degraded', 'operation_id missing');
  }

  fixtures['query-evidence-with-evidence-span.json'] = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
    method: 'POST',
    body: {
      query: 'What should EvidenceSpan navigation highlight during release validation?',
      top_k: 5
    }
  });
  const jumpable = findJumpableEvidence(fixtures['query-evidence-with-evidence-span.json']);
  if (!jumpable) {
    throw new Error('workspace query evidence did not include source_id + unit_id + evidence_id');
  }
  mark('workspace query jumpable evidence', 'pass', `${jumpable.source_id}/${jumpable.unit_id}/${jumpable.evidence_id}`);

  fixtures['evidence-span-detail-success.json'] = await request(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(jumpable.source_id)}/units/${encodeURIComponent(
      jumpable.unit_id
    )}/evidence/${encodeURIComponent(jumpable.evidence_id)}`
  );
  const span = extractEvidenceSpan(fixtures['evidence-span-detail-success.json']);
  assertSpan(span, jumpable);
  mark('evidence span detail', 'pass', `${span.offset_basis}/${span.offset_range}/${span.text_basis}`);

  try {
    await request(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(jumpable.source_id)}/units/${encodeURIComponent(
        jumpable.unit_id
      )}/evidence/${encodeURIComponent('ev_0000000000000000')}`
    );
    mark('evidence not found semantics', 'fail', 'unknown evidence unexpectedly succeeded');
    throw new Error('unknown evidence unexpectedly succeeded');
  } catch (error) {
    fixtures['evidence-span-not-found.json'] = error.payload ?? { message: error.message };
    if (error.status === 404) {
      mark('evidence not found semantics', 'pass', '404');
    } else {
      mark('evidence not found semantics', 'degraded', error.message);
    }
  }

  try {
    await request(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(jumpable.source_id)}/units/${encodeURIComponent(
        jumpable.unit_id
      )}/evidence/${encodeURIComponent('artifact://ev')}`
    );
    mark('artifact_ref evidence id rejected', 'fail', 'artifact_ref unexpectedly succeeded');
    throw new Error('artifact_ref unexpectedly succeeded');
  } catch (error) {
    fixtures['evidence-span-artifact-ref-rejected.json'] = error.payload ?? { message: error.message };
    if (error.status === 422 || error.status === 400) {
      mark('artifact_ref evidence id rejected', 'pass', String(error.status));
    } else {
      mark('artifact_ref evidence id rejected', 'degraded', error.message);
    }
  }

  await saveFixtures();
  mark('fixtures saved', 'pass', fixtureDir);
} catch (error) {
  await saveFixtures().catch(() => undefined);
  mark('v1.1-d real smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'degraded', error instanceof Error ? error.message : String(error));
    }
  }
}
