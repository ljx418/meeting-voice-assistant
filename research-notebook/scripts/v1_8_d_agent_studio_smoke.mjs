/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V18_D_PREFIX ?? `rn-v18-agent-studio-${Date.now()}`;
const materialDir =
  process.env.RN_V18_D_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V18_D_DIGITAL_HUMAN_PDF ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_8', 'agent-studio');
const maxPollMs = Number(process.env.RN_V18_D_MAX_POLL_MS ?? 60_000);
const pollIntervalMs = Number(process.env.RN_V18_D_POLL_INTERVAL_MS ?? 1_000);
const providerRetryDelayMs = Number(process.env.RN_V18_D_PROVIDER_RETRY_DELAY_MS ?? 5_000);
const providerMaxAttempts = Number(process.env.RN_V18_D_PROVIDER_MAX_ATTEMPTS ?? 5);
const artifactTypes = ['notes', 'study_guide', 'briefing_doc', 'faq'];

const results = [];
const assertions = [];
const fixtures = {};
let workspaceId = '';
let finalDecision = 'FAIL';

function mark(name, status, detail = '') {
  results.push({ name, status, detail });
  const label = status === 'pass' ? 'PASS' : status === 'degraded' ? 'DEGRADED' : 'FAIL';
  console.log(`${label} ${name}${detail ? ` - ${detail}` : ''}`);
}

function assertRecord(name, expected, actual, status, evidenceRef = '') {
  assertions.push({
    assertion_id: `assert_${String(assertions.length + 1).padStart(3, '0')}`,
    name,
    expected,
    actual,
    status,
    evidence_ref: evidenceRef || undefined
  });
  if (status === 'FAIL') throw new Error(`${name}: expected ${JSON.stringify(expected)}, actual ${JSON.stringify(actual)}`);
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
        lowered === 'paths' ||
        lowered.endsWith('_path') ||
        lowered.endsWith('_paths') ||
        lowered.includes('cache') ||
        lowered.includes('physical') ||
        lowered.includes('stack') ||
        lowered.includes('content_base64')
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
      .replace(/\/Users(?:\/[^\s"',}]*)?/g, '[home]')
      .replace(/\/private(?:\/[^\s"',}]*)?/g, '[private]')
      .replace(/\/tmp(?:\/[^\s"',}]*)?/g, '[tmp]')
      .replaceAll('file://', 'file-redacted://')
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]');
  }
  return value;
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

async function saveFixture(name, payload) {
  await mkdir(fixtureDir, { recursive: true });
  fixtures[name] = sanitize(payload);
  const content = typeof fixtures[name] === 'string' ? `${fixtures[name]}\n` : `${JSON.stringify(fixtures[name], null, 2)}\n`;
  await writeFile(join(fixtureDir, name), content);
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

function createDraft() {
  const task = {
    task_id: `task_${Date.now()}`,
    user_intent: '验证数字人 Studio 四类轻量输出、引用和导出合同',
    target_path_labels: ['Desktop/技术分享/11-数字人'],
    target_path_refs: [`perm_${Date.now()}`],
    expected_outputs: ['notes', 'study_guide', 'briefing_doc', 'faq', 'markdown_export', 'json_export', 'validation_report'],
    status: 'approved'
  };
  mark('agent studio draft', 'pass', task.task_id);
  assertRecord('draft contains no raw local path', false, JSON.stringify(task).includes('/Users'), 'PASS', task.task_id);
  return task;
}

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.8-agent-studio', tags: ['v1.8', 'agent-studio'] }
  });
  workspaceId = extractWorkspaceId(payload);
  if (!workspaceId) throw new Error('workspace_id missing');
  await saveFixture('workspace-create.json', payload);
  mark('workspace create', 'pass', workspaceId);
}

async function importTextSource(title, content, sourceFormat, fixtureName) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [{ title, content, metadata: { source_format: sourceFormat, v1_8_agent_studio: true } }],
      metadata: { source_format: sourceFormat, v1_8_agent_studio: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${sourceFormat} source_id missing`);
  await saveFixture(fixtureName, payload);
  mark(`${sourceFormat} import`, 'pass', sourceId);
}

async function importPdfSource() {
  const pdf = await readFile(realPdfPath);
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      metadata: {
        title: 'AI 数字人产业发展报告 PDF',
        source_type: 'pdf',
        file_name: basename(realPdfPath),
        v1_8_agent_studio: true
      },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: pdf.toString('base64'),
          metadata: { file_name: basename(realPdfPath), v1_8_agent_studio: true }
        }
      ]
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error('pdf source_id missing');
  await saveFixture('pdf-import.json', payload);
  mark('pdf import', 'pass', sourceId);
}

async function buildWorkspace() {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(payload);
  if (!operationId) {
    mark('workspace build', 'degraded', 'operation_id missing');
    return;
  }
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const data = dataOf(latest);
    const status = data?.operation?.status ?? data?.status;
    if (status === 'completed') {
      await saveFixture('workspace-build.json', latest);
      mark('workspace build', 'pass', operationId);
      return;
    }
    if (['failed', 'blocked', 'cancelled'].includes(status)) throw new Error(`build ${status}`);
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  throw new Error('build timeout');
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
    if (attempt < providerMaxAttempts) await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
  }
  return latest;
}

function artifactFrom(payload) {
  return dataOf(payload)?.artifact;
}

function validateArtifact(payload, artifactType) {
  const artifact = artifactFrom(payload);
  if (!artifact?.artifact_available) throw new Error(`${artifactType} artifact_available is false`);
  if (artifact.generation_metadata?.fallback_mode !== false) throw new Error(`${artifactType} used fallback mode`);
  if (!String(artifact.title ?? '').trim()) throw new Error(`${artifactType} title missing`);
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
  assertRecord(`${artifactType} top-level evidence refs`, '>=1', artifact.evidence_refs.length, 'PASS', `studio-${artifactType}-success.json`);
  assertRecord(`${artifactType} section evidence refs`, 'all sections', artifact.sections.length, 'PASS', `studio-${artifactType}-success.json`);
  return artifact;
}

async function assertEvidenceResolves(evidence, fixturePrefix) {
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) {
    throw new Error(`${fixturePrefix} evidence missing source_id/unit_id/evidence_id`);
  }
  const unitPayload = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}`
  );
  const spanPayload = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
  );
  const span = dataOf(spanPayload)?.evidence_span;
  if (span?.source_id !== evidence.source_id || span?.unit_id !== evidence.unit_id || span?.evidence_id !== evidence.evidence_id) {
    throw new Error(`${fixturePrefix} EvidenceSpan ids do not match`);
  }
  if (span.offset_basis !== 'normalized_text' || span.offset_range !== 'half_open' || span.text_basis !== 'document_unit_text') {
    throw new Error(`${fixturePrefix} EvidenceSpan offset contract mismatch`);
  }
  if (hasRawPath(unitPayload) || hasRawPath(spanPayload)) throw new Error(`${fixturePrefix} unit/span payload contains raw path`);
  await saveFixture(`${fixturePrefix}-unit-detail.json`, unitPayload);
  await saveFixture(`${fixturePrefix}-evidence-span.json`, spanPayload);
  assertRecord(`${fixturePrefix} citation resolves`, true, Boolean(span?.evidence_id), span?.evidence_id ? 'PASS' : 'FAIL', `${fixturePrefix}-evidence-span.json`);
}

function artifactToMarkdown(artifact) {
  const lines = [`# ${artifact.title}`, '', artifact.summary, '', '## Sections'];
  for (const section of artifact.sections) {
    lines.push('', `### ${section.title}`, '', section.content, '', 'Citations:');
    for (const ref of section.evidence_refs ?? []) {
      lines.push(`- source_id=${ref.source_id}; unit_id=${ref.unit_id}; evidence_id=${ref.evidence_id}`);
    }
  }
  lines.push('', '## Evidence Refs');
  for (const ref of artifact.evidence_refs ?? []) {
    lines.push(`- source_id=${ref.source_id}; unit_id=${ref.unit_id}; evidence_id=${ref.evidence_id}; title=${ref.source_title ?? ''}`);
  }
  return lines.join('\n');
}

function artifactToJsonExport(artifact) {
  return {
    schema_version: 'v1_8_d_agent_studio_export',
    exported_at: new Date().toISOString(),
    artifact_id: artifact.artifact_id,
    artifact_type: artifact.artifact_type,
    title: artifact.title,
    summary: artifact.summary,
    sections: artifact.sections,
    evidence_refs: artifact.evidence_refs,
    generation_metadata: artifact.generation_metadata
  };
}

function validateExports(artifact, artifactType) {
  const markdown = artifactToMarkdown(artifact);
  const jsonExport = artifactToJsonExport(artifact);
  if (!markdown.includes(artifact.title) || !markdown.includes('Citations:') || !markdown.includes('source_id=')) {
    throw new Error(`${artifactType} markdown export missing citation metadata`);
  }
  for (const key of ['schema_version', 'exported_at', 'artifact_id', 'artifact_type', 'sections', 'evidence_refs']) {
    if (!(key in jsonExport)) throw new Error(`${artifactType} json export missing ${key}`);
  }
  if (hasRawPath(markdown) || hasRawPath(jsonExport)) throw new Error(`${artifactType} export contains raw path`);
  return { markdown, jsonExport };
}

async function cleanup() {
  if (!workspaceId) return;
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.8 agent studio cleanup' }
  });
  await saveFixture('workspace-archive.json', payload);
  mark('cleanup', 'pass', workspaceId);
}

async function main() {
  const startedAt = new Date().toISOString();
  const task = createDraft();
  try {
    const md = await readFile(join(materialDir, '01_industry_overview.md'), 'utf8');
    const tech = await readFile(join(materialDir, '02_technology_trends.md'), 'utf8');
    await readFile(realPdfPath);
    mark('material check', 'pass', 'AI digital human Markdown/PDF available');

    await mustRequest('/api/workspaces');
    mark('target route probe', 'pass', baseUrl);
    await createWorkspace();
    await importTextSource('AI 数字人行业概览 Markdown', md, 'markdown', 'markdown-import.json');
    await importTextSource('AI 数字人技术趋势 Markdown', tech, 'markdown', 'technology-markdown-import.json');
    await importPdfSource();
    await buildWorkspace();

    for (const artifactType of artifactTypes) {
      const payload = await requestStudioArtifact(artifactType);
      await saveFixture(`studio-${artifactType}-success.json`, payload);
      const artifact = validateArtifact(payload, artifactType);
      await assertEvidenceResolves(artifact.evidence_refs[0], `studio-${artifactType}`);
      const { markdown, jsonExport } = validateExports(artifact, artifactType);
      await saveFixture(`export-${artifactType}.md`, markdown);
      await saveFixture(`export-${artifactType}.json`, jsonExport);
      mark(`studio ${artifactType}`, 'pass', 'artifact/citation/export');
      await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
    }

    finalDecision = 'PASS_LIMITED';
  } catch (error) {
    finalDecision = 'FAIL';
    const cause = error && typeof error === 'object' && 'cause' in error ? error.cause : null;
    const detail = `${error instanceof Error ? error.message : String(error)}${cause ? `; cause=${JSON.stringify(cause)}` : ''}`;
    mark('v1.8-d agent studio smoke', 'fail', detail);
    process.exitCode = 1;
  } finally {
    await cleanup().catch((error) => mark('cleanup', 'degraded', error instanceof Error ? error.message : String(error)));
    const stepResults = results.map((result, index) => ({
      step_id: `step_${String(index + 1).padStart(3, '0')}`,
      name: result.name,
      status: result.status === 'pass' || result.status === 'degraded' ? 'completed' : 'failed',
      output_summary: { detail: result.detail, smoke_status: result.status },
      retry_count: 0,
      artifact_refs: []
    }));
    const workflowRun = {
      run_id: `run_${Date.now()}`,
      task_id: task.task_id,
      workspace_id: workspaceId,
      status: finalDecision === 'PASS_LIMITED' ? 'completed' : 'failed',
      started_at: startedAt,
      finished_at: new Date().toISOString(),
      steps: stepResults,
      artifact_refs: Object.keys(fixtures),
      validation_report_id: '',
      final_decision: finalDecision
    };
    const report = {
      report_id: `report_${Date.now()}`,
      task_id: task.task_id,
      workspace_id: workspaceId,
      run_id: workflowRun.run_id,
      workflow_run: workflowRun,
      studio_result: { artifact_types: artifactTypes },
      export_result: { markdown: true, json: true },
      step_results: stepResults,
      assertions,
      raw_fixture_refs: Object.keys(fixtures),
      accepted_debts: ['Agent validation is not a substitute for human Studio content quality review', 'ordinary user UX remains accepted debt'],
      still_not_ready: ['Studio human quality ready', 'ordinary user UX ready', 'Audio/PPT/Mindmap/Compare ready'],
      final_decision: finalDecision,
      generated_at: startedAt
    };
    workflowRun.validation_report_id = report.report_id;
    assertRecord('report contains no raw path', false, hasRawPath(report), hasRawPath(report) ? 'FAIL' : 'PASS');
    report.assertions = assertions;
    await saveFixture('v1_8_d_agent_studio_result.json', report);
    if (hasRawPath(fixtures)) {
      mark('fixture hygiene', 'fail', 'raw path detected');
      process.exitCode = 1;
    } else {
      mark('fixture hygiene', 'pass', 'sanitized');
    }
    console.log(`V1_8_D_AGENT_STUDIO_DECISION ${finalDecision}`);
  }
}

await main();
