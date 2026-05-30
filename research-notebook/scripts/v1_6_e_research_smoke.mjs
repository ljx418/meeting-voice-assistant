/* global fetch */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const techShareRoot = process.env.RN_V16_RESEARCH_ROOT ?? join(process.env.HOME ?? '', 'Desktop', '技术分享');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_6', 'research-workflow');
const sourceFile = process.env.RN_V16_RESEARCH_SOURCE ?? join(techShareRoot, '11-数字人', 'AI数字人资料包', '01_industry_overview.md');
const question = process.env.RN_V16_RESEARCH_QUESTION ?? '数字人行业的市场趋势和商业应用有哪些？';

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
    return value.replaceAll('/Users', '[home]').replaceAll('/private/tmp', '[tmp]').replaceAll('/tmp', '[tmp]').replaceAll('file://', 'file-redacted://');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  for (const [name, payload] of Object.entries(fixtures)) {
    const target = join(fixtureDir, name);
    await mkdir(dirname(target), { recursive: true });
    await writeFile(target, JSON.stringify(sanitize(payload), null, 2) + '\n');
  }
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

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: `rn-v16-research-${Date.now()}`, owner: 'v1.6-research-smoke', tags: ['v1.6', 'research'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  fixtures['workspace-create.json'] = payload;
  mark('workspace create', 'pass', workspaceId);
}

async function importMarkdown() {
  const content = await readFile(sourceFile, 'utf8');
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: basename(sourceFile),
          content,
          metadata: { v1_6_research_smoke: true, source_type: 'markdown', file_name: basename(sourceFile) }
        }
      ],
      metadata: { v1_6_research_smoke: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error('source_id missing');
  fixtures['source-import.json'] = payload;
  mark('source import', 'pass', sourceId);
}

async function createResearch(label, inputQuestion) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/research`, {
    method: 'POST',
    body: { question: inputQuestion, top_k: 8 }
  });
  fixtures[`${label}.json`] = payload;
  if (hasRawPath(payload)) throw new Error(`${label} contains raw path`);
  return dataOf(payload)?.research;
}

async function resolveEvidence(evidence) {
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) {
    throw new Error('research evidence missing source_id/unit_id/evidence_id');
  }
  const unit = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}`
  );
  const span = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
  );
  if (hasRawPath(unit) || hasRawPath(span)) throw new Error('evidence resolution contains raw path');
  fixtures['research-evidence-unit.json'] = unit;
  fixtures['research-evidence-span.json'] = span;
  mark('evidence resolution', 'pass', evidence.evidence_id);
}

async function archiveWorkspace() {
  if (!workspaceId) return;
  const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.6 research smoke cleanup' }
  });
  fixtures['workspace-archive.json'] = payload.payload;
  mark('workspace archive', payload.ok ? 'pass' : 'degraded', `${payload.status}`);
}

try {
  await mustRequest('/api/workspaces');
  mark('target route probe', 'pass', baseUrl);
  await createWorkspace();
  const emptyReport = await createResearch('research-no-sources', question);
  if (emptyReport?.research_available !== false || emptyReport?.coverage_status !== 'no_sources') throw new Error('no-source research did not refuse');
  mark('no-source refusal', 'pass', emptyReport.coverage_status);
  await importMarkdown();
  const report = await createResearch('research-supported', question);
  if (report?.research_available !== true) throw new Error('research report not available after source import');
  if (!Array.isArray(report.supported_conclusions) || report.supported_conclusions.length < 1) throw new Error('research report missing supported conclusions');
  const evidence = report.supported_conclusions[0]?.evidence_refs?.[0];
  await resolveEvidence(evidence);
  if (!Array.isArray(report.conflicts) || !Array.isArray(report.missing_evidence)) throw new Error('research report missing conflicts/missing_evidence fields');
  mark('research report', 'pass', `${report.supported_conclusions.length} conclusions`);
  finalDecision = 'PASS_LIMITED_CONTRACT_SMOKE';
} catch (error) {
  mark('v1.6-e research smoke', 'fail', error instanceof Error ? error.message : String(error));
  finalDecision = 'FAIL';
  process.exitCode = 1;
} finally {
  await archiveWorkspace();
  fixtures['v1_6_e_research_smoke_result.json'] = { finalDecision, results, baseUrl, sourceFile, question };
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
