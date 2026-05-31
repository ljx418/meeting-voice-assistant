/* global fetch */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V19_CONFLICT_PREFIX ?? `rn-v19-conflict-${Date.now()}`;
const datasetDir = join(process.cwd(), 'fixtures', 'manual', 'v1_9', 'conflict-dataset');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_9', 'conflict-labeling');

const results = [];
let workspaceId = '';
let finalDecision = 'FAIL';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  console.log(`${status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL'} ${name}${detail ? ` - ${detail}` : ''}`);
}

function sanitize(value) {
  if (Array.isArray(value)) return value.map(sanitize);
  if (value && typeof value === 'object') {
    const output = {};
    for (const [key, item] of Object.entries(value)) {
      const lowered = key.toLowerCase();
      if (lowered.includes('api_key') || lowered.includes('authorization') || lowered.endsWith('_path') || lowered.includes('cache') || lowered.includes('physical') || lowered.includes('stack')) continue;
      output[key] = sanitize(item);
    }
    return output;
  }
  if (typeof value === 'string') {
    return value.replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]').replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]').replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]').replaceAll('file://', 'file-redacted://');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  await writeFile(join(fixtureDir, name), `${JSON.stringify(sanitize(payload), null, 2)}\n`);
}

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: options.method ?? 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  const text = await response.text();
  return { ok: response.ok, status: response.status, payload: text ? JSON.parse(text) : null };
}

async function mustRequest(path, options = {}) {
  const result = await request(path, options);
  if (!result.ok) throw new Error(`HTTP ${result.status} ${path}`);
  return result.payload;
}

function dataOf(payload) {
  return payload?.data && typeof payload.data === 'object' ? payload.data : payload;
}

function extractWorkspaceId(payload) {
  const data = dataOf(payload);
  return data?.workspace?.workspace_id ?? data?.workspace_id ?? payload?.workspace_id;
}

function extractSourceId(payload) {
  const data = dataOf(payload);
  return data?.source?.source_id ?? data?.sources?.[0]?.source_id ?? payload?.source_id;
}

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.9-conflict-labeling', tags: ['v1.9', 'conflict'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  await saveFixture('workspace-create.json', payload);
  mark('workspace create', 'pass', workspaceId);
}

async function importConflictSource(fileName, title) {
  const content = await readFile(join(datasetDir, fileName), 'utf8');
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [{ title, content, metadata: { source_format: 'markdown', v1_9_conflict: true } }],
      metadata: { v1_9_conflict: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${fileName} source_id missing`);
  await saveFixture(`${fileName.replaceAll('.', '-')}-import.json`, payload);
  mark('conflict source import', 'pass', `${title}: ${sourceId}`);
}

async function resolveEvidence(evidence) {
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) throw new Error('conflict evidence ids missing');
  const unit = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}`);
  const span = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`);
  if (hasRawPath(unit) || hasRawPath(span)) throw new Error('conflict evidence resolution contains raw path');
  await saveFixture('conflict-evidence-unit.json', unit);
  await saveFixture('conflict-evidence-span.json', span);
  mark('conflict evidence resolution', 'pass', evidence.evidence_id);
}

async function cleanup() {
  if (!workspaceId) return;
  const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.9 conflict labeling cleanup' }
  });
  await saveFixture('workspace-archive.json', payload.payload);
  mark('cleanup', payload.ok ? 'pass' : 'degraded', String(payload.status));
}

try {
  await mustRequest('/api/workspaces');
  mark('target route probe', 'pass', baseUrl);
  await createWorkspace();
  await importConflictSource('digital-human-optimistic.md', '数字人商业化乐观口径');
  await importConflictSource('digital-human-conservative.md', '数字人商业化保守口径');
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/research`, {
    method: 'POST',
    body: { question: '数字人项目 Alpha 在 2026 年是否已经实现规模化商业化？请列出来源之间的分歧。', top_k: 8 }
  });
  if (hasRawPath(payload)) throw new Error('conflict research contains raw path');
  await saveFixture('research-conflict.json', payload);
  const report = dataOf(payload)?.research;
  const conflict = report?.conflicts?.[0];
  if (!conflict || !Array.isArray(conflict.positions) || conflict.positions.length < 2) {
    finalDecision = 'NOT_READY';
    mark('conflict labeling', 'fail', 'no real conflict detected');
    process.exitCode = 1;
  } else {
    const firstEvidence = conflict.positions.find((position) => Array.isArray(position.evidence_refs) && position.evidence_refs.length)?.evidence_refs?.[0];
    await resolveEvidence(firstEvidence);
    finalDecision = 'PASS_LIMITED';
    mark('conflict labeling', 'pass', `${conflict.positions.length} positions`);
  }
} catch (error) {
  mark('v1.9 conflict labeling smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  await cleanup().catch((error) => mark('cleanup', 'degraded', error instanceof Error ? error.message : String(error)));
  await saveFixture('v1_9_b_conflict_labeling_result.json', {
    generated_at: new Date().toISOString(),
    final_decision: finalDecision,
    results,
    accepted_debts: ['conflict labeling requires human semantic review']
  });
  console.log(`V1_9_B_CONFLICT_LABELING_DECISION ${finalDecision}`);
}
