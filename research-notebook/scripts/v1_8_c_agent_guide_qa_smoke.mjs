/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V18_C_PREFIX ?? `rn-v18-agent-guide-qa-${Date.now()}`;
const materialDir =
  process.env.RN_V18_C_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V18_C_DIGITAL_HUMAN_PDF ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_8', 'agent-guide-qa');
const maxPollMs = Number(process.env.RN_V18_C_MAX_POLL_MS ?? 60_000);
const pollIntervalMs = Number(process.env.RN_V18_C_POLL_INTERVAL_MS ?? 1_000);
const providerRetryDelayMs = Number(process.env.RN_V18_C_PROVIDER_RETRY_DELAY_MS ?? 5_000);
const providerMaxAttempts = Number(process.env.RN_V18_C_PROVIDER_MAX_ATTEMPTS ?? 5);

const results = [];
const assertions = [];
const fixtures = {};
let workspaceId = '';
let finalDecision = 'FAIL';
let selectedSuggestedQuestion = '';

const fixedQuestions = [
  { key: 'covered-technology', kind: 'covered', text: '数字人 技术 趋势是什么？' },
  { key: 'outside', kind: 'outside', text: '火星采矿 农业机械 海洋运输的结论是什么？' }
];

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
  await writeFile(join(fixtureDir, name), `${JSON.stringify(fixtures[name], null, 2)}\n`);
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
    user_intent: '验证数字人 Notebook Guide、引用问答和 citation 可解析性',
    target_path_labels: ['Desktop/技术分享/11-数字人'],
    target_path_refs: [`perm_${Date.now()}`],
    expected_outputs: ['notebook_guide', 'source_grounded_qa', 'validation_report'],
    status: 'approved'
  };
  mark('agent guide qa draft', 'pass', task.task_id);
  assertRecord('draft contains no raw local path', false, JSON.stringify(task).includes('/Users'), 'PASS', task.task_id);
  return task;
}

async function createWorkspace() {
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: prefix, owner: 'v1.8-agent-guide-qa', tags: ['v1.8', 'agent-guide-qa'] }
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
      texts: [{ title, content, metadata: { source_format: sourceFormat, v1_8_agent_guide_qa: true } }],
      metadata: { source_format: sourceFormat, v1_8_agent_guide_qa: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${sourceFormat} source_id missing`);
  await saveFixture(fixtureName, payload);
  mark(`${sourceFormat} import`, 'pass', sourceId);
  return sourceId;
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
        v1_8_agent_guide_qa: true
      },
      files: [
        {
          title: 'AI 数字人产业发展报告 PDF',
          file_name: basename(realPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: pdf.toString('base64'),
          metadata: { file_name: basename(realPdfPath), v1_8_agent_guide_qa: true }
        }
      ]
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error('pdf source_id missing');
  await saveFixture('pdf-import.json', payload);
  mark('pdf import', 'pass', sourceId);
  return sourceId;
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

function questionText(value) {
  if (typeof value === 'string') return value;
  return value?.question ?? value?.text ?? value?.title ?? '';
}

function validateGuide(payload) {
  const guide = dataOf(payload)?.guide;
  if (!guide?.guide_available) throw new Error('guide_available is false');
  if (guide.generation_metadata?.fallback_mode !== false) throw new Error('AI Guide used fallback mode');
  if (!String(guide.overview ?? '').includes('数字人')) throw new Error('overview does not mention 数字人');
  if (!Array.isArray(guide.key_topics) || guide.key_topics.length < 3) throw new Error('key_topics length < 3');
  if (!Array.isArray(guide.suggested_questions) || guide.suggested_questions.length < 3) {
    throw new Error('suggested_questions length < 3');
  }
  if (!Array.isArray(guide.evidence_refs) || guide.evidence_refs.length < 1) throw new Error('guide evidence_refs missing');
  if (!guide.key_topics.some((topic) => Array.isArray(topic.evidence_refs) && topic.evidence_refs.length > 0)) {
    throw new Error('no key topic has evidence_refs');
  }
  if (hasRawPath(payload)) throw new Error('guide payload contains raw path');
  selectedSuggestedQuestion = questionText(guide.suggested_questions[0]);
  if (!selectedSuggestedQuestion) throw new Error('suggested question text missing');
  assertRecord('guide key topics count', '>=3', guide.key_topics.length, guide.key_topics.length >= 3 ? 'PASS' : 'FAIL', 'ai-guide-success.json');
  assertRecord(
    'guide suggested questions count',
    '>=3',
    guide.suggested_questions.length,
    guide.suggested_questions.length >= 3 ? 'PASS' : 'FAIL',
    'ai-guide-success.json'
  );
  assertRecord('guide evidence refs count', '>=1', guide.evidence_refs.length, guide.evidence_refs.length >= 1 ? 'PASS' : 'FAIL', 'ai-guide-success.json');
}

function isRetryableProviderFallback(payload) {
  const errorCode = dataOf(payload)?.generation_metadata?.error_code;
  return ['provider_timeout', 'provider_unavailable', 'rate_limited'].includes(errorCode);
}

async function queryWorkspace(question) {
  let latest = null;
  for (let attempt = 1; attempt <= providerMaxAttempts; attempt += 1) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
      method: 'POST',
      body: { query: question, top_k: 6 }
    });
    const data = dataOf(latest);
    if (data.no_evidence || data.generation_metadata?.fallback_mode !== true || !isRetryableProviderFallback(latest)) {
      return latest;
    }
    mark('qa retryable fallback', 'degraded', `${data.generation_metadata.error_code}; retry ${attempt}/${providerMaxAttempts}`);
    if (attempt < providerMaxAttempts) await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
  }
  return latest;
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
    throw new Error(`${fixturePrefix} EvidenceSpan ids do not match query evidence`);
  }
  if (span.offset_basis !== 'normalized_text' || span.offset_range !== 'half_open' || span.text_basis !== 'document_unit_text') {
    throw new Error(`${fixturePrefix} EvidenceSpan offset contract mismatch`);
  }
  if (hasRawPath(unitPayload) || hasRawPath(spanPayload)) throw new Error(`${fixturePrefix} unit/span payload contains raw path`);
  await saveFixture(`${fixturePrefix}-unit-detail.json`, unitPayload);
  await saveFixture(`${fixturePrefix}-evidence-span.json`, spanPayload);
  return span;
}

async function validateQuery(key, question, kind) {
  const payload = await queryWorkspace(question);
  await saveFixture(`query-${key}.json`, payload);
  const data = dataOf(payload);
  if (hasRawPath(payload)) throw new Error(`${key} payload contains raw path`);
  if (kind === 'outside') {
    const refused =
      data.no_evidence === true ||
      data.answer_basis === 'source_grounded_refusal' ||
      String(data.answer ?? '').includes('当前资料未覆盖') ||
      String(data.answer ?? '').includes('未找到依据');
    assertRecord(`${key} source-grounded refusal`, true, refused, refused ? 'PASS' : 'FAIL', `query-${key}.json`);
    mark(`query ${key}`, 'pass', 'outside refusal');
    return null;
  }
  if (data.no_evidence) throw new Error(`${key} unexpectedly has no evidence`);
  if (data.generation_metadata?.fallback_mode !== false) throw new Error(`${key} used fallback mode`);
  if (!Array.isArray(data.evidence_refs) || data.evidence_refs.length < 1) throw new Error(`${key} evidence_refs missing`);
  const span = await assertEvidenceResolves(data.evidence_refs[0], `query-${key}`);
  assertRecord(`${key} citation resolves`, true, Boolean(span?.evidence_id), span?.evidence_id ? 'PASS' : 'FAIL', `query-${key}-evidence-span.json`);
  mark(`query ${key}`, 'pass', kind);
  return span;
}

async function cleanup() {
  if (!workspaceId) return;
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
    method: 'POST',
    body: { reason: 'v1.8 agent guide qa cleanup' }
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

    const guidePayload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/guide`);
    await saveFixture('ai-guide-success.json', guidePayload);
    validateGuide(guidePayload);
    mark('guide validation', 'pass', 'overview/topics/questions/evidence');

    await validateQuery('suggested-question', selectedSuggestedQuestion, 'suggested');
    await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
    await validateQuery(fixedQuestions[0].key, fixedQuestions[0].text, fixedQuestions[0].kind);
    await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
    await validateQuery(fixedQuestions[1].key, fixedQuestions[1].text, fixedQuestions[1].kind);

    finalDecision = 'PASS_LIMITED';
  } catch (error) {
    finalDecision = 'FAIL';
    const cause = error && typeof error === 'object' && 'cause' in error ? error.cause : null;
    const detail = `${error instanceof Error ? error.message : String(error)}${cause ? `; cause=${JSON.stringify(cause)}` : ''}`;
    mark('v1.8-c agent guide qa smoke', 'fail', detail);
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
      guide_result: { selected_suggested_question: selectedSuggestedQuestion },
      qa_result: { checked_questions: ['suggested-question', ...fixedQuestions.map((item) => item.key)] },
      citation_result: { evidence_span_resolution_required: true },
      step_results: stepResults,
      assertions,
      raw_fixture_refs: Object.keys(fixtures),
      accepted_debts: ['Agent validation is not a substitute for full human content quality review', 'ordinary user UX remains accepted debt'],
      still_not_ready: ['Studio quality ready', 'all-domain QA quality ready', 'ordinary user UX ready'],
      final_decision: finalDecision,
      generated_at: startedAt
    };
    workflowRun.validation_report_id = report.report_id;
    assertRecord('report contains no raw path', false, hasRawPath(report), hasRawPath(report) ? 'FAIL' : 'PASS');
    report.assertions = assertions;
    await saveFixture('v1_8_c_agent_guide_qa_result.json', report);
    if (hasRawPath(fixtures)) {
      mark('fixture hygiene', 'fail', 'raw path detected');
      process.exitCode = 1;
    } else {
      mark('fixture hygiene', 'pass', 'sanitized');
    }
    console.log(`V1_8_C_AGENT_GUIDE_QA_DECISION ${finalDecision}`);
  }
}

await main();
