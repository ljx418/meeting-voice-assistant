/* global fetch, setTimeout */
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const techShareRoot = process.env.RN_V16_QUALITY_ROOT ?? join(process.env.HOME ?? '', 'Desktop', '技术分享');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_6', 'quality-eval');
const maxPollMs = Number(process.env.RN_V16_QUALITY_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V16_QUALITY_POLL_INTERVAL_MS ?? 1_000);
const providerRetryDelayMs = Number(process.env.RN_V16_QUALITY_PROVIDER_RETRY_DELAY_MS ?? 2_500);
const providerMaxAttempts = Number(process.env.RN_V16_QUALITY_PROVIDER_MAX_ATTEMPTS ?? 3);

const datasets = [
  {
    key: 'digital-human',
    name: '数字人',
    files: [
      join(techShareRoot, '11-数字人', 'AI数字人资料包', '01_industry_overview.md'),
      join(techShareRoot, '11-数字人', 'AI数字人资料包', '02_technology_trends.md'),
      join(techShareRoot, '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf')
    ],
    coveredQuestions: ['数字人的主要应用场景是什么？', '数字人技术趋势有哪些？'],
    outsideQuestion: '火星采矿农业机械的投资结论是什么？',
    studioArtifact: 'faq'
  },
  {
    key: 'claude-code',
    name: 'Claude Code 技术分享',
    files: [join(techShareRoot, '02-claudecode技术分享', 'ClaudeCode高阶技巧.md')],
    coveredQuestions: ['Claude Code 的高阶技巧有哪些？', '如何更好地组织 Claude Code 工作流？'],
    outsideQuestion: '数字人监管政策有哪些？',
    studioArtifact: 'study_guide'
  },
  {
    key: 'ai-video-workflow',
    name: 'AI 视频工作流',
    files: [join(techShareRoot, '08-AITextToVideoWorkflow', 'README.md')],
    coveredQuestions: ['AI 文生视频工作流从想法、脚本、分镜、提示词、生成、剪辑到发布的完整链路是什么？', 'assets/images、assets/audio、assets/video 和 output 分别用于什么？'],
    outsideQuestion: 'Claude Code 的权限模型是什么？',
    studioArtifact: 'briefing_doc'
  }
];

const results = [];
const fixtures = {};
const datasetSummaries = [];
let currentWorkspaceId = '';
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
    return value
      .replaceAll(process.env.DATA_SERVICE_AI_API_KEY ?? '__NO_KEY__', '[redacted-api-key]')
      .replaceAll('/Users', '[home]')
      .replaceAll('/private/tmp', '[tmp]')
      .replaceAll('/tmp', '[tmp]')
      .replaceAll('file://', 'file-redacted://');
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

function extractOperationId(payload) {
  const data = dataOf(payload);
  return payload?.operation_id ?? data?.operation_id ?? data?.operation?.operation_id;
}

function evidenceRefsFrom(payload) {
  const data = dataOf(payload);
  return data?.evidence_refs ?? data?.answer?.evidence ?? data?.evidence ?? data?.guide?.evidence_refs ?? data?.artifact?.evidence_refs ?? [];
}

async function pollOperation(operationId) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const data = dataOf(latest);
    const status = data?.operation?.status ?? data?.status;
    if (['completed', 'failed', 'blocked', 'cancelled'].includes(status)) return { status, payload: latest };
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return { status: 'timeout', payload: latest };
}

async function createWorkspace(dataset) {
  const workspaceName = `rn-v16-quality-${dataset.key}-${Date.now()}`;
  const payload = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: workspaceName, owner: 'v1.6-quality-smoke', tags: ['v1.6', 'quality-eval', dataset.key] }
  });
  currentWorkspaceId = extractWorkspaceId(payload);
  if (!currentWorkspaceId) throw new Error('workspace_id missing');
  fixtures[`${dataset.key}/workspace-create.json`] = payload;
  mark(`${dataset.key} workspace create`, 'pass', currentWorkspaceId);
}

async function importFile(filePath, dataset) {
  const content = await readFile(filePath);
  const lower = filePath.toLowerCase();
  if (lower.endsWith('.pdf')) {
    const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/sources`, {
      method: 'POST',
      body: {
        files: [
          {
            title: basename(filePath),
            file_name: basename(filePath),
            content_base64: content.toString('base64'),
            content_type: 'application/pdf',
            source_type: 'pdf',
            metadata: { v1_6_quality_eval: true, dataset: dataset.key, file_name: basename(filePath) }
          }
        ],
        metadata: { v1_6_quality_eval: true, dataset: dataset.key }
      }
    });
    return extractSourceId(payload);
  }
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: basename(filePath),
          content: content.toString('utf8'),
          metadata: { v1_6_quality_eval: true, dataset: dataset.key, source_type: lower.endsWith('.txt') ? 'text' : 'markdown' }
        }
      ],
      metadata: { v1_6_quality_eval: true, dataset: dataset.key }
    }
  });
  return extractSourceId(payload);
}

async function buildWorkspace(dataset) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/build/start`, { method: 'POST', body: {} });
  const operationId = extractOperationId(payload);
  if (!operationId) {
    mark(`${dataset.key} build`, 'degraded', 'operation_id missing');
    return;
  }
  const result = await pollOperation(operationId);
  fixtures[`${dataset.key}/workspace-build.json`] = result.payload;
  if (result.status !== 'completed') throw new Error(`${dataset.key} build did not complete: ${result.status}`);
  mark(`${dataset.key} build`, 'pass', operationId);
}

async function resolveEvidence(dataset, label, evidence) {
  if (!evidence?.source_id || !evidence?.unit_id || !evidence?.evidence_id) {
    throw new Error(`${dataset.key} ${label} evidence is missing source_id/unit_id/evidence_id`);
  }
  const unitPayload = await mustRequest(
    `/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}`
  );
  const spanPayload = await mustRequest(
    `/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/sources/${encodeURIComponent(evidence.source_id)}/units/${encodeURIComponent(evidence.unit_id)}/evidence/${encodeURIComponent(evidence.evidence_id)}`
  );
  const span = dataOf(spanPayload)?.evidence_span;
  if (span?.source_id !== evidence.source_id || span?.unit_id !== evidence.unit_id || span?.evidence_id !== evidence.evidence_id) {
    throw new Error(`${dataset.key} ${label} EvidenceSpan mismatch`);
  }
  if (hasRawPath(unitPayload) || hasRawPath(spanPayload)) throw new Error(`${dataset.key} ${label} evidence payload contains raw path`);
  fixtures[`${dataset.key}/${label}-unit.json`] = unitPayload;
  fixtures[`${dataset.key}/${label}-span.json`] = spanPayload;
}

function isRetryableProviderFallback(payload) {
  const data = dataOf(payload);
  const errorCode = data?.generation_metadata?.error_code ?? data?.artifact?.generation_metadata?.error_code ?? data?.guide?.generation_metadata?.error_code;
  return ['provider_timeout', 'provider_unavailable', 'rate_limited'].includes(errorCode);
}

async function queryWorkspace(dataset, question) {
  let latest = null;
  for (let attempt = 1; attempt <= providerMaxAttempts; attempt += 1) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/query`, {
      method: 'POST',
      body: { query: question, top_k: 6 }
    });
    const data = dataOf(latest);
    if (data.no_evidence || data.generation_metadata?.fallback_mode !== true || !isRetryableProviderFallback(latest)) return latest;
    mark(`${dataset.key} query retry`, 'degraded', `${data.generation_metadata.error_code}; retry ${attempt}/${providerMaxAttempts}`);
    if (attempt < providerMaxAttempts) await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
  }
  return latest;
}

async function requestStudioArtifact(dataset) {
  let latest = null;
  for (let attempt = 1; attempt <= providerMaxAttempts; attempt += 1) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/studio/artifacts`, {
      method: 'POST',
      body: { artifact_type: dataset.studioArtifact }
    });
    const artifact = dataOf(latest)?.artifact;
    if (artifact?.generation_metadata?.fallback_mode !== true || !isRetryableProviderFallback(latest)) return latest;
    mark(`${dataset.key} studio retry`, 'degraded', `${artifact.generation_metadata.error_code}; retry ${attempt}/${providerMaxAttempts}`);
    if (attempt < providerMaxAttempts) await new Promise((resolve) => setTimeout(resolve, providerRetryDelayMs));
  }
  return latest;
}

async function validateDataset(dataset) {
  await createWorkspace(dataset);
  const sourceIds = [];
  for (const filePath of dataset.files) {
    const sourceId = await importFile(filePath, dataset);
    if (!sourceId) throw new Error(`${dataset.key} source_id missing for ${basename(filePath)}`);
    sourceIds.push(sourceId);
  }
  mark(`${dataset.key} source import`, 'pass', `${sourceIds.length} sources`);
  await buildWorkspace(dataset);

  const guide = await mustRequest(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/guide`);
  fixtures[`${dataset.key}/guide.json`] = guide;
  const guideData = dataOf(guide)?.guide;
  if (!guideData?.guide_available || !Array.isArray(guideData.evidence_refs) || guideData.evidence_refs.length < 1) {
    throw new Error(`${dataset.key} guide evidence missing`);
  }
  await resolveEvidence(dataset, 'guide-evidence', guideData.evidence_refs[0]);
  mark(`${dataset.key} guide`, 'pass', `${guideData.evidence_refs.length} refs`);

  const coveredResults = [];
  for (const [index, question] of dataset.coveredQuestions.entries()) {
    const payload = await queryWorkspace(dataset, question);
    fixtures[`${dataset.key}/query-covered-${index + 1}.json`] = payload;
    const refs = evidenceRefsFrom(payload);
    if (!Array.isArray(refs) || refs.length < 1) throw new Error(`${dataset.key} covered query evidence missing`);
    await resolveEvidence(dataset, `query-covered-${index + 1}-evidence`, refs[0]);
    coveredResults.push({ question, evidence_ref_count: refs.length });
    mark(`${dataset.key} covered query ${index + 1}`, 'pass', `${refs.length} refs`);
  }

  const outside = await queryWorkspace(dataset, dataset.outsideQuestion);
  fixtures[`${dataset.key}/query-outside.json`] = outside;
  const outsideData = dataOf(outside);
  const outsideRefused =
    outsideData?.no_evidence === true ||
    outsideData?.answer_basis === 'source_grounded_refusal' ||
    String(outsideData?.answer ?? '').includes('当前资料未覆盖');
  if (!outsideRefused) {
    mark(`${dataset.key} outside refusal`, 'degraded', 'needs manual review');
  } else {
    mark(`${dataset.key} outside refusal`, 'pass', 'source-grounded refusal observed');
  }

  const studio = await requestStudioArtifact(dataset);
  fixtures[`${dataset.key}/studio-${dataset.studioArtifact}.json`] = studio;
  const studioRefs = evidenceRefsFrom(studio);
  if (!Array.isArray(studioRefs) || studioRefs.length < 1) throw new Error(`${dataset.key} studio evidence missing`);
  await resolveEvidence(dataset, 'studio-evidence', studioRefs[0]);
  mark(`${dataset.key} studio`, 'pass', `${studioRefs.length} refs`);

  datasetSummaries.push({
    dataset_key: dataset.key,
    dataset_name: dataset.name,
    source_count: sourceIds.length,
    source_ids: sourceIds,
    guide_evidence_ref_count: guideData.evidence_refs.length,
    covered_queries: coveredResults,
    outside_refusal_auto_observed: outsideRefused,
    studio_artifact: dataset.studioArtifact,
    studio_evidence_ref_count: studioRefs.length,
    manual_review_required: true,
    auto_decision: 'CANDIDATE_READY_FOR_MANUAL_REVIEW'
  });
}

async function cleanup(dataset) {
  if (!currentWorkspaceId) return;
  const payload = await request(`/api/workspaces/${encodeURIComponent(currentWorkspaceId)}/archive`, {
    method: 'POST',
    body: { reason: `v1.6 quality eval cleanup: ${dataset.key}` }
  });
  fixtures[`${dataset.key}/workspace-cleanup.json`] = payload.payload;
  mark(`${dataset.key} cleanup`, payload.ok ? 'pass' : 'degraded', currentWorkspaceId);
}

async function main() {
  try {
    for (const dataset of datasets) {
      currentWorkspaceId = '';
      try {
        await validateDataset(dataset);
      } finally {
        await cleanup(dataset).catch((error) => mark(`${dataset.key} cleanup`, 'degraded', error instanceof Error ? error.message : String(error)));
      }
    }
    finalDecision = 'CANDIDATE_READY_FOR_MANUAL_REVIEW';
  } catch (error) {
    finalDecision = 'FAIL';
    mark('v1.6-b quality smoke', 'fail', error instanceof Error ? error.message : String(error));
    process.exitCode = 1;
  } finally {
    fixtures['v1_6_b_quality_eval_smoke_result.json'] = {
      final_decision: finalDecision,
      base_url: baseUrl,
      dataset_summaries: datasetSummaries,
      results,
      manual_review_required: true,
      not_claimed: ['V1.6-B PASS', 'multi-dataset quality ready', 'all-domain ready', 'all-source-type ready']
    };
    await saveFixtures();
    console.log(`FINAL ${finalDecision}`);
  }
}

await main();
