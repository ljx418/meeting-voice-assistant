/* global fetch, setTimeout */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V11_S1_WORKSPACE_PREFIX ?? `rn-v11-s1-session-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_1', 'session-precise-navigation');
const maxPollMs = Number(process.env.RN_V11_S1_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V11_S1_POLL_INTERVAL_MS ?? 1_000);

const results = [];
const fixtures = {};
let workspaceId = '';
let sourceId = '';
let sessionId = '';
let sessionBuildRequired = 'unknown';
let sessionBuildOperationId = '';
let sessionBuildFinalStatus = '';
let sessionEvidenceShape = 'UNSTABLE_OR_BLOCKED';
let unitResolution = 'NOT_RUN';
let evidenceSpanResolution = 'NOT_RUN';
let uiCitationResult = 'NOT_RUN';
let declaration = 'NOT_READY';

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
      .replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]')
      .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]')
      .replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]')
      .replace(/[A-Za-z]:\\[^\s"',}]*/g, '[windows-path]')
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

function arrayFrom(...candidates) {
  for (const candidate of candidates) {
    if (Array.isArray(candidate)) return candidate;
  }
  return [];
}

function readWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace?.workspace_id ?? data?.workspace_id ?? payload?.workspace_id;
}

function readSourceId(payload) {
  const data = dataOf(payload);
  return data?.source?.source_id ?? data?.sources?.[0]?.source_id ?? payload?.source_id;
}

function readSessionId(payload) {
  const data = dataOf(payload);
  return data?.session?.session_id ?? data?.session_id ?? payload?.session_id;
}

function readOperationId(payload) {
  const data = dataOf(payload);
  return data?.operation?.operation_id ?? data?.operation_id ?? payload?.operation_id;
}

function readOperationStatus(payload) {
  const data = dataOf(payload);
  return data?.operation?.status ?? data?.status ?? payload?.status;
}

function readManifest(payload) {
  const data = dataOf(payload);
  return data?.manifest ?? data;
}

function readSources(payload) {
  const data = dataOf(payload);
  return arrayFrom(data?.sources, data?.items, data);
}

function readEvidence(payload) {
  const data = dataOf(payload);
  return arrayFrom(data?.evidence, data?.evidence_refs, data?.items, data?.results, data?.sources, data?.hits, payload?.hits);
}

function readUnit(payload) {
  const data = dataOf(payload);
  return data?.unit ?? data;
}

function readEvidenceSpan(payload) {
  const data = dataOf(payload);
  return data?.evidence_span ?? data;
}

function hasRawPath(value) {
  const text = JSON.stringify(value);
  return /(?:^|[^A-Za-z])[A-Za-z]:\\|\/Users(?:\/|")|file:\/\/|cache_path|artifact_path|physical_path|\/private(?:\/|")|\/tmp(?:\/|")/.test(text);
}

function isRegistrySourceId(id) {
  return typeof id === 'string' && /^src_[A-Za-z0-9]{8,64}$/.test(id) && !id.includes('://') && !id.includes('/');
}

function findJumpableEvidence(payload) {
  return readEvidence(payload).find((item) => item?.source_id && item?.unit_id && item?.evidence_id);
}

function hasGraphOnlyPayload(payload) {
  const data = dataOf(payload);
  return [data?.nodes, data?.edges, data?.communities].some((value) => Array.isArray(value) && value.length > 0);
}

function classifySessionQuery(payload) {
  if (hasRawPath(payload)) return 'UNSTABLE_OR_BLOCKED';
  const evidence = readEvidence(payload);
  if (evidence.some((item) => item?.source_id && item?.unit_id && item?.evidence_id)) return 'HAS_EVIDENCE_SPAN_IDS';
  if (hasGraphOnlyPayload(payload)) return 'GRAPH_ONLY_NO_EVIDENCE';
  if (evidence.length === 0) return 'NO_EVIDENCE_ACCEPTED';
  if (evidence.some((item) => item?.node_id || item?.edge_id || item?.community_id || item?.graph_id)) return 'GRAPH_ONLY_NO_EVIDENCE';
  return 'NO_EVIDENCE_ACCEPTED';
}

function assertCapabilities(manifest) {
  for (const key of ['document_units', 'unit_level_navigation', 'evidence_spans', 'precise_span_highlight', 'citation_backjump']) {
    if (manifest?.capabilities?.[key] !== true) throw new Error(`capability ${key} is not true`);
  }
}

function assertEvidenceSpan(span, evidence, unit) {
  if (span.evidence_id !== evidence.evidence_id) throw new Error('EvidenceSpan evidence_id mismatch');
  if (span.source_id !== evidence.source_id) throw new Error('EvidenceSpan source_id mismatch');
  if (span.unit_id !== evidence.unit_id) throw new Error('EvidenceSpan unit_id mismatch');
  if (span.offset_basis !== 'normalized_text') throw new Error(`unsupported offset_basis ${span.offset_basis}`);
  if (span.offset_range !== 'half_open') throw new Error(`unsupported offset_range ${span.offset_range}`);
  if (span.text_basis !== 'document_unit_text') throw new Error(`unsupported text_basis ${span.text_basis}`);
  if (!Number.isFinite(span.start_offset) || !Number.isFinite(span.end_offset)) throw new Error('EvidenceSpan offsets missing');
  if (span.start_offset < 0 || span.end_offset <= span.start_offset) throw new Error('EvidenceSpan offsets invalid');
  const text = String(unit?.text_preview ?? '');
  if (span.end_offset > text.length) throw new Error('EvidenceSpan end_offset outside unit text');
  if (!span.snippet) throw new Error('EvidenceSpan snippet missing');
}

async function pollOperation(path) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(path);
    const status = readOperationStatus(latest);
    if (['completed', 'succeeded', 'failed', 'blocked', 'cancelled'].includes(status)) {
      return { status, payload: latest };
    }
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return { status: 'poll_timeout', payload: latest };
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

  const sourceCreated = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: 'V1.1 S1 Session Evidence Source',
          content:
            'Session precise navigation should preserve source id, unit id, and evidence id so the notebook can open the same highlighted source span from a session answer.',
          metadata: { stage: 'v1.1-s1-session-precise-navigation' }
        }
      ],
      metadata: { stage: 'v1.1-s1-session-precise-navigation' }
    }
  });
  sourceId = readSourceId(sourceCreated);
  if (!isRegistrySourceId(sourceId)) throw new Error(`source_id is not a registry source id: ${sourceId}`);
  mark('source create', 'pass', sourceId);

  fixtures['source-list.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
  const listedSource = readSources(fixtures['source-list.json']).find((source) => source?.source_id === sourceId);
  if (!listedSource) throw new Error('created source_id missing from source list');
  fixtures['source-detail.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}`);
  mark('source list/get registry id', 'pass', sourceId);

  fixtures['capability-manifest.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/capabilities`);
  assertCapabilities(readManifest(fixtures['capability-manifest.json']));
  mark('capability manifest evidence flags', 'pass');

  fixtures['session-create.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions`, {
    method: 'POST',
    body: { title: `${prefix} session precise navigation` }
  });
  sessionId = readSessionId(fixtures['session-create.json']);
  if (!sessionId) throw new Error('session_id missing after session create');
  mark('session create', 'pass', sessionId);

  fixtures['session-ingest.json'] = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/ingest`,
    {
      method: 'POST',
      body: {
        title: 'V1.1 S1 session snippet',
        content_format: 'text',
        source_type: 'text',
        content:
          'Session precise navigation should preserve source id, unit id, and evidence id so the notebook can open the same highlighted source span from a session answer.',
        related_source_ids: [sourceId],
        source_refs: [sourceId],
        metadata: { stage: 'v1.1-s1-session-precise-navigation' }
      }
    }
  );
  mark('session ingest', 'pass');

  const sessionBuild = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  fixtures['session-build-operation.json'] = sessionBuild.payload;
  if (sessionBuild.ok) {
    sessionBuildRequired = 'yes';
    sessionBuildOperationId = readOperationId(sessionBuild.payload) ?? '';
    if (sessionBuildOperationId) {
      const buildResult = await pollOperation(
        `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/operations/${encodeURIComponent(
          sessionBuildOperationId
        )}`
      );
      fixtures['session-build-operation.json'] = buildResult.payload;
      sessionBuildFinalStatus = buildResult.status ?? 'unknown';
      mark('session build polling', ['completed', 'succeeded'].includes(sessionBuildFinalStatus) ? 'pass' : 'degraded', sessionBuildFinalStatus);
    } else {
      sessionBuildFinalStatus = 'operation_id_missing';
      mark('session build polling', 'degraded', sessionBuildFinalStatus);
    }
  } else {
    sessionBuildRequired = 'no_or_unavailable';
    sessionBuildFinalStatus = `HTTP ${sessionBuild.status}`;
    mark('session build polling', 'degraded', sessionBuildFinalStatus);
  }

  const sessionQuery = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/query`, {
    method: 'POST',
    body: {
      query: 'What identifiers should session precise navigation preserve?',
      top_k: 5
    }
  });
  if (!sessionQuery.ok) {
    fixtures['session-query-no-evidence.json'] = { status: sessionQuery.status, payload: sessionQuery.payload };
    sessionEvidenceShape = 'UNSTABLE_OR_BLOCKED';
    declaration = 'BLOCKED_BY_BACKEND_CONTRACT';
    mark('session query', 'fail', `HTTP ${sessionQuery.status}`);
  } else {
    sessionEvidenceShape = classifySessionQuery(sessionQuery.payload);
    fixtures[
      sessionEvidenceShape === 'HAS_EVIDENCE_SPAN_IDS' ? 'session-query-with-evidence-span.json' : 'session-query-no-evidence.json'
    ] = sessionQuery.payload;
    mark('session query', sessionEvidenceShape === 'HAS_EVIDENCE_SPAN_IDS' ? 'pass' : 'degraded', sessionEvidenceShape);
  }

  const jumpable = sessionQuery.ok ? findJumpableEvidence(sessionQuery.payload) : null;
  if (jumpable) {
    if (!isRegistrySourceId(jumpable.source_id)) throw new Error(`session evidence source_id is not registry id: ${jumpable.source_id}`);
    fixtures['session-evidence-unit-detail.json'] = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(jumpable.source_id)}/units/${encodeURIComponent(
        jumpable.unit_id
      )}`
    );
    const unit = readUnit(fixtures['session-evidence-unit-detail.json']);
    unitResolution = 'PASS';
    mark('unit detail resolution', 'pass', jumpable.unit_id);

    fixtures['session-evidence-span-detail.json'] = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(jumpable.source_id)}/units/${encodeURIComponent(
        jumpable.unit_id
      )}/evidence/${encodeURIComponent(jumpable.evidence_id)}`
    );
    const span = readEvidenceSpan(fixtures['session-evidence-span-detail.json']);
    assertEvidenceSpan(span, jumpable, unit);
    evidenceSpanResolution = 'PASS';
    declaration = 'API_SMOKE_READY';
    mark('evidence span resolution', 'pass', `${span.offset_basis}/${span.offset_range}/${span.text_basis}`);
  } else if (sessionEvidenceShape === 'UNSTABLE_OR_BLOCKED') {
    declaration = 'BLOCKED_BY_BACKEND_CONTRACT';
    mark('evidence id decision', 'fail', sessionEvidenceShape);
  } else {
    declaration = 'NOT_READY';
    mark('evidence id decision', 'degraded', sessionEvidenceShape);
  }

  fixtures['s1-session-precise-navigation-result.json'] = {
    declaration,
    session_query_evidence_shape: sessionEvidenceShape,
    unit_detail_resolution: unitResolution,
    evidence_span_resolution: evidenceSpanResolution,
    ui_citation_result: uiCitationResult,
    workspace_id: workspaceId,
    source_id: sourceId,
    session_id: sessionId,
    session_build_required: sessionBuildRequired,
    session_build_operation_id: sessionBuildOperationId,
    session_build_final_status: sessionBuildFinalStatus,
    results
  };

  await saveFixtures();
  mark('fixtures saved', 'pass', fixtureDir);
  console.log(`S1_SESSION_PRECISE_NAVIGATION_DECISION ${declaration}`);
} catch (error) {
  declaration = declaration === 'API_SMOKE_READY' ? 'BLOCKED_BY_BACKEND_CONTRACT' : declaration;
  fixtures['s1-session-precise-navigation-result.json'] = {
    declaration,
    session_query_evidence_shape: sessionEvidenceShape,
    unit_detail_resolution: unitResolution,
    evidence_span_resolution: evidenceSpanResolution,
    ui_citation_result: uiCitationResult,
    workspace_id: workspaceId,
    source_id: sourceId,
    session_id: sessionId,
    session_build_required: sessionBuildRequired,
    session_build_operation_id: sessionBuildOperationId,
    session_build_final_status: sessionBuildFinalStatus,
    error: error instanceof Error ? error.message : String(error),
    results
  };
  await saveFixtures().catch(() => undefined);
  mark('v1.1-s1 session precise navigation smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (sessionId && workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/close`, {
        method: 'POST',
        body: {}
      });
      mark('session close cleanup', 'pass', sessionId);
    } catch (error) {
      mark('session close cleanup', 'degraded', error instanceof Error ? error.message : String(error));
    }
  }
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: {} });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'degraded', error instanceof Error ? error.message : String(error));
    }
  }
}
