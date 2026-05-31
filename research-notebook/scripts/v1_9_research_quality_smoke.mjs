/* global fetch */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V19_RESEARCH_PREFIX ?? `rn-v19-research-${Date.now()}`;
const materialDir =
  process.env.RN_V19_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_9', 'research-quality');

const results = [];
const fixtures = {};
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
      if (
        lowered.includes('api_key') ||
        lowered.includes('authorization') ||
        lowered === 'path' ||
        lowered.endsWith('_path') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack')
      ) continue;
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
  fixtures[name] = sanitize(payload);
  await writeFile(join(fixtureDir, name), `${JSON.stringify(fixtures[name], null, 2)}\n`);
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
    body: { name: prefix, owner: 'v1.9-research-quality', tags: ['v1.9', 'research-quality'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  await saveFixture('workspace-create.json', payload);
  mark('workspace create', 'pass', workspaceId);
}

async function importMarkdown(fileName, title) {
  const content = await readFile(join(materialDir, fileName), 'utf8');
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [{ title, content, metadata: { source_format: 'markdown', v1_9_research_quality: true } }],
      metadata: { v1_9_research_quality: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${fileName} source_id missing`);
  await saveFixture(`${fileName.replaceAll('.', '-')}-import.json`, payload);
  mark('source import', 'pass', `${title}: ${sourceId}`);
}

async function createResearch(label, question) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/research`, {
    method: 'POST',
    body: { question, top_k: 8 }
  });
  if (hasRawPath(payload)) throw new Error(`${label} contains raw path`);
  await saveFixture(`${label}.json`, payload);
  return dataOf(payload)?.research;
}

async function resolveEvidence(evidence, label) {
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) throw new Error(`${label} evidence ids missing`);
  const unit = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}`
  );
  const span = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
  );
  if (hasRawPath(unit) || hasRawPath(span)) throw new Error(`${label} evidence resolution contains raw path`);
  await saveFixture(`${label}-unit.json`, unit);
  await saveFixture(`${label}-span.json`, span);
  mark('evidence resolution', 'pass', label);
}

function validateSupportedReport(report) {
  if (report?.research_available !== true) throw new Error('supported research not available');
  if (!Array.isArray(report.supported_conclusions) || report.supported_conclusions.length < 1) throw new Error('missing supported_conclusions');
  for (const [index, conclusion] of report.supported_conclusions.entries()) {
    if (!String(conclusion.claim ?? '').trim()) throw new Error(`conclusion ${index} claim missing`);
    if (!Array.isArray(conclusion.evidence_refs) || conclusion.evidence_refs.length < 1) throw new Error(`conclusion ${index} evidence missing`);
  }
  if (!Array.isArray(report.inferences) || !Array.isArray(report.conflicts) || !Array.isArray(report.missing_evidence)) {
    throw new Error('research report missing structured fields');
  }
  for (const [index, inference] of report.inferences.entries()) {
    if (!Array.isArray(inference.evidence_refs) || inference.evidence_refs.length < 1) throw new Error(`inference ${index} evidence missing`);
  }
}

function validateRefusal(report, expectedStatus) {
  const refused =
    report?.research_available === false ||
    report?.coverage_status === expectedStatus ||
    report?.answer_basis === 'source_grounded_refusal' ||
    String(report?.answer ?? '').includes('未覆盖') ||
    String(report?.answer ?? '').includes('未找到依据');
  if (!refused) throw new Error(`research did not refuse: ${expectedStatus}`);
}

async function cleanup() {
  if (!workspaceId) return;
  const payload = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.9 research quality cleanup' }
  });
  await saveFixture('workspace-archive.json', payload.payload);
  mark('cleanup', payload.ok ? 'pass' : 'degraded', String(payload.status));
}

try {
  await mustRequest('/api/workspaces');
  mark('target route probe', 'pass', baseUrl);
  await createWorkspace();

  const noSource = await createResearch('research-no-sources', '数字人行业的商业化结论是什么？');
  validateRefusal(noSource, 'no_sources');
  mark('no-source refusal', 'pass', noSource.coverage_status);

  await importMarkdown('01_industry_overview.md', 'AI 数字人行业概览');
  await importMarkdown('02_technology_trends.md', 'AI 数字人技术趋势');

  const supported = await createResearch('research-supported', '数字人行业的市场趋势、技术进展和商业应用有哪些？');
  validateSupportedReport(supported);
  await resolveEvidence(supported.supported_conclusions[0].evidence_refs[0], 'supported-conclusion');
  mark('supported research report', 'pass', `${supported.supported_conclusions.length} conclusions`);

  const outside = await createResearch('research-outside-question', '火星采矿农业机械的投资结论是什么？');
  validateRefusal(outside, 'insufficient_evidence');
  mark('outside refusal', 'pass', outside.coverage_status);

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  mark('v1.9 research quality smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  await cleanup().catch((error) => mark('cleanup', 'degraded', error instanceof Error ? error.message : String(error)));
  await saveFixture('v1_9_a_research_quality_result.json', {
    generated_at: new Date().toISOString(),
    final_decision: finalDecision,
    results,
    accepted_debts: ['automatic research smoke is not human quality review']
  });
  console.log(`V1_9_A_RESEARCH_QUALITY_DECISION ${finalDecision}`);
}
