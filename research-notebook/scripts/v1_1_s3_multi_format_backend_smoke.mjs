/* global fetch */

import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = `rn-v11-s3-multiformat-${Date.now()}`;
const fixturesDir = join(process.cwd(), 'fixtures/real/v1_1/multi-format-backend');

const candidates = [
  {
    source_type: 'markdown',
    title: 'V1.1 S3 Markdown Source',
    query: 'markdownanchor queue',
    content: '# Markdown Evidence\n\nmarkdownanchor queue evidence proves markdown unit navigation.'
  },
  {
    source_type: 'json',
    title: 'V1.1 S3 JSON Source',
    query: 'jsonanchor queue',
    content: JSON.stringify({
      summary: 'jsonanchor queue evidence proves json node navigation',
      status: 'supported'
    })
  }
];

let workspaceId = '';
const results = [];

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
      if (
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
    throw new Error(`${init.method ?? 'GET'} ${path} failed: HTTP ${response.status} ${JSON.stringify(response.payload).slice(0, 400)}`);
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

function readPreview(payload) {
  return dataOf(payload)?.preview ?? payload?.preview ?? dataOf(payload);
}

function readUnits(payload) {
  return dataOf(payload)?.units ?? payload?.units ?? dataOf(payload);
}

function readEvidenceSpan(payload) {
  return dataOf(payload)?.evidence_span ?? payload?.evidence_span ?? dataOf(payload);
}

function assertNoRawPath(payload, label) {
  if (hasRawPath(payload)) throw new Error(`${label} leaked raw path/cache/artifact physical path`);
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
  await saveFixture('capability-manifest.json', capabilityPayload);
  const supported = new Map((manifest?.supported_source_types ?? []).map((item) => [item.source_type, item]));
  for (const sourceType of ['markdown', 'json']) {
    const entry = supported.get(sourceType);
    if (!entry || entry.preview !== 'unit') throw new Error(`manifest missing ${sourceType}:unit`);
  }
  mark('capability manifest markdown/json', 'pass', manifest.supported_source_types.map((item) => `${item.source_type}:${item.preview}`).join(', '));

  const candidateResults = [];
  for (const candidate of candidates) {
    const sourcePayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
      method: 'POST',
      body: {
        texts: [
          {
            title: candidate.title,
            content: candidate.content,
            metadata: {
              stage: 'v1.1-s3-multi-format-backend-contract',
              source_type: candidate.source_type
            }
          }
        ],
        metadata: {
          stage: 'v1.1-s3-multi-format-backend-contract',
          source_type: candidate.source_type
        }
      }
    });
    const sourceId = readSourceId(sourcePayload);
    if (!sourceId || !/^src_[A-Za-z0-9]{8,64}$/.test(sourceId)) throw new Error(`${candidate.source_type} source_id is not registry-shaped`);
    await saveFixture(`${candidate.source_type}-source-create.json`, sourcePayload);

    const previewPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/preview`
    );
    const preview = readPreview(previewPayload);
    if (preview.source_type !== candidate.source_type || preview.preview_available !== true) {
      throw new Error(`${candidate.source_type} preview not available`);
    }
    await saveFixture(`${candidate.source_type}-preview.json`, previewPayload);

    const unitsPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units?limit=20`
    );
    const units = readUnits(unitsPayload);
    if (!Array.isArray(units.items) || units.items.length < 1) throw new Error(`${candidate.source_type} units empty`);
    const firstUnit = units.items[0];
    if (firstUnit.source_id !== sourceId || !firstUnit.unit_id) throw new Error(`${candidate.source_type} unit missing stable ids`);
    if (candidate.source_type === 'json' && firstUnit.unit_type !== 'json_node') throw new Error('json did not produce json_node units');
    await saveFixture(`${candidate.source_type}-units.json`, unitsPayload);

    const queryPayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
      method: 'POST',
      body: { query: candidate.query, top_k: 6 }
    });
    const evidence = (queryPayload.evidence ?? []).find((item) => item.source_id === sourceId);
    if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) {
      throw new Error(`${candidate.source_type} query evidence missing source_id/unit_id/evidence_id`);
    }
    await saveFixture(`${candidate.source_type}-query-evidence.json`, queryPayload);

    const unitDetailPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units/${encodeURIComponent(evidence.unit_id)}`
    );
    await saveFixture(`${candidate.source_type}-unit-detail.json`, unitDetailPayload);

    const spanPayload = await mustRequest(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
    );
    const span = readEvidenceSpan(spanPayload);
    if (span.source_id !== sourceId || span.unit_id !== evidence.unit_id || span.evidence_id !== evidence.evidence_id) {
      throw new Error(`${candidate.source_type} EvidenceSpan id mismatch`);
    }
    if (span.offset_basis !== 'normalized_text' || span.offset_range !== 'half_open' || span.text_basis !== 'document_unit_text') {
      throw new Error(`${candidate.source_type} EvidenceSpan offset contract mismatch`);
    }
    await saveFixture(`${candidate.source_type}-evidence-span.json`, spanPayload);

    const queryEvidenceOnly = {
      evidence: queryPayload.evidence ?? [],
      evidence_refs: queryPayload.evidence_refs ?? []
    };
    for (const [label, payload] of [
      [`${candidate.source_type} source create`, sourcePayload],
      [`${candidate.source_type} preview`, previewPayload],
      [`${candidate.source_type} units`, unitsPayload],
      [`${candidate.source_type} query evidence`, queryEvidenceOnly],
      [`${candidate.source_type} unit detail`, unitDetailPayload],
      [`${candidate.source_type} evidence span`, spanPayload]
    ]) {
      assertNoRawPath(payload, label);
    }

    candidateResults.push({
      source_type: candidate.source_type,
      source_id: sourceId,
      preview: 'PASS',
      document_units: 'PASS',
      query_evidence: 'PASS',
      evidence_span: 'PASS',
      first_unit_id: evidence.unit_id,
      evidence_id: evidence.evidence_id
    });
    mark(`smoke ${candidate.source_type}`, 'pass', `${evidence.unit_id}/${evidence.evidence_id}`);
  }

  const summary = {
    declaration: 'S3_MULTI_FORMAT_BACKEND_READY_MARKDOWN_JSON',
    workspace_id: workspaceId,
    candidates: candidateResults,
    results
  };
  await saveFixture('s3-multi-format-backend-result.json', summary);
  console.log('S3_MULTI_FORMAT_BACKEND_DECISION READY_MARKDOWN_JSON');
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
