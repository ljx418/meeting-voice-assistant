/* global fetch, Buffer, setTimeout */
import { copyFile, mkdir, readFile, stat, writeFile } from 'node:fs/promises';
import { basename, join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V14_SOURCES_PREFIX ?? `rn-v14-sources-p0-${Date.now()}`;
const materialDir =
  process.env.RN_V14_DIGITAL_HUMAN_DIR ?? join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人资料包');
const realPdfPath =
  process.env.RN_V14_DIGITAL_HUMAN_PDF ??
  join(process.env.HOME ?? '', 'Desktop', '技术分享', '11-数字人', 'AI数字人产业发展报告_2026-05-26.pdf');
const manualDir = join(process.cwd(), 'fixtures', 'manual', 'v1_4', 'sources-p0');
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_4', 'sources-p0');
const maxPollMs = Number(process.env.RN_V14_SOURCES_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_V14_SOURCES_POLL_INTERVAL_MS ?? 1_000);

const markdownFiles = [
  '01_industry_overview.md',
  '02_technology_trends.md',
  '05_policy_and_risks.md'
];

const results = [];
const fixtures = {};
let workspaceId = '';
let finalDecision = 'NOT_READY';

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
      .replaceAll('/Users', '[home]')
      .replaceAll('/private/tmp', '[tmp]')
      .replaceAll('/tmp', '[tmp]')
      .replaceAll('file://', 'file-redacted://');
  }
  return value;
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  await Promise.all(
    Object.entries(fixtures).map(([name, payload]) =>
      writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n')
    )
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

function extractOperationId(payload) {
  const data = dataOf(payload);
  return payload?.operation_id ?? data?.operation_id ?? data?.operation?.operation_id;
}

function extractPreviewText(payload) {
  const data = dataOf(payload);
  const preview = data?.preview ?? data;
  return preview?.text_preview ?? preview?.content ?? preview?.text ?? '';
}

function extractEvidence(payload) {
  const data = dataOf(payload);
  for (const candidate of [data?.evidence, data?.evidence_refs, data?.hits, data?.items, payload?.evidence]) {
    if (Array.isArray(candidate)) return candidate;
  }
  return [];
}

function hasCitation(payload) {
  return extractEvidence(payload).some((item) => item?.source_id || item?.sourceId || item?.source_ref || item?.sourceRef);
}

function hasRawPath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

function stripMarkdown(markdown) {
  return markdown
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/^#+\s+/gm, '')
    .replace(/^>\s?/gm, '')
    .replace(/[*_`|]/g, '')
    .replace(/\n{3,}/g, '\n\n')
    .trim();
}

function escapePdfText(text) {
  return text.replace(/\\/g, '\\\\').replace(/\(/g, '\\(').replace(/\)/g, '\\)');
}

function createSimplePdf(text) {
  const lines = stripMarkdown(text)
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(0, 36)
    .map((line) => line.slice(0, 92));
  const content = ['BT', '/F1 10 Tf', '50 780 Td', '14 TL', ...lines.map((line) => `(${escapePdfText(line)}) Tj T*`), 'ET'].join('\n');
  const objects = [
    '1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n',
    '2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n',
    '3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n',
    '4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n',
    `5 0 obj\n<< /Length ${Buffer.byteLength(content)} >>\nstream\n${content}\nendstream\nendobj\n`
  ];
  let offset = '%PDF-1.4\n'.length;
  const offsets = [0];
  const body = objects
    .map((object) => {
      offsets.push(offset);
      offset += Buffer.byteLength(object);
      return object;
    })
    .join('');
  const xrefOffset = offset;
  const xref = ['xref', `0 ${objects.length + 1}`, '0000000000 65535 f ', ...offsets.slice(1).map((item) => `${String(item).padStart(10, '0')} 00000 n `)].join('\n');
  const trailer = `\ntrailer\n<< /Size ${objects.length + 1} /Root 1 0 R >>\nstartxref\n${xrefOffset}\n%%EOF\n`;
  return Buffer.from(`%PDF-1.4\n${body}${xref}${trailer}`);
}

async function prepareMaterials() {
  await mkdir(manualDir, { recursive: true });
  const index = await readFile(join(materialDir, 'sources_index.md'), 'utf8');
  if (!index.includes('| S001 |')) throw new Error('sources_index.md does not include expected source table');
  const markdown = {};
  for (const name of markdownFiles) {
    const text = await readFile(join(materialDir, name), 'utf8');
    if (!text.includes('来源名称') || !text.includes('摘要')) throw new Error(`${name} missing expected metadata`);
    markdown[name] = text;
  }

  const txtContent = stripMarkdown(markdown['01_industry_overview.md']);
  const pdfContent = markdown['02_technology_trends.md'];
  await writeFile(join(manualDir, 'ai-digital-human-sample.txt'), txtContent + '\n');
  let pdfSource = 'generated';
  try {
    await stat(realPdfPath);
    await copyFile(realPdfPath, join(manualDir, 'ai-digital-human-real-sample.pdf'));
    pdfSource = 'user_provided';
  } catch {
    await writeFile(join(manualDir, 'ai-digital-human-sample.pdf'), createSimplePdf(pdfContent));
  }
  await writeFile(
    join(manualDir, 'material-manifest.json'),
    JSON.stringify(
      {
        generated_at: new Date().toISOString(),
        source_folder_label: '技术分享/11-数字人/AI数字人资料包',
        markdown_files: markdownFiles,
        derived_files:
          pdfSource === 'user_provided'
            ? ['ai-digital-human-sample.txt', 'ai-digital-human-real-sample.pdf']
            : ['ai-digital-human-sample.txt', 'ai-digital-human-sample.pdf'],
        pdf_source: pdfSource,
        pdf_note:
          pdfSource === 'user_provided'
            ? 'User-provided PDF copied into manual fixtures for V1.4-C source import validation.'
            : 'Generated from Markdown as a minimal copyable-text PDF sample; not proof of arbitrary external PDF readiness.'
      },
      null,
      2
    ) + '\n'
  );
  return markdown;
}

async function createTextSource(kind, title, content, metadata = {}) {
  const payload = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title,
          content,
          metadata: { ...metadata, source_format: kind, v1_4_sources_p0: true }
        }
      ],
      metadata: { ...metadata, source_format: kind, v1_4_sources_p0: true }
    }
  });
  const sourceId = extractSourceId(payload);
  if (!sourceId) throw new Error(`${kind} source_id missing`);
  return { sourceId, payload };
}

async function createPdfBrowserUploadSource() {
  const pdfPath = join(manualDir, 'ai-digital-human-real-sample.pdf');
  const fallbackPdfPath = join(manualDir, 'ai-digital-human-sample.pdf');
  const selectedPdfPath = await stat(pdfPath)
    .then(() => pdfPath)
    .catch(() => fallbackPdfPath);
  const contentBase64 = (await readFile(selectedPdfPath)).toString('base64');
  const result = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      metadata: {
        title: 'AI 数字人技术进展 PDF 派生样本',
        source_type: 'pdf',
        file_name: basename(selectedPdfPath),
        file_import_contract: 'browser_base64_upload',
        v1_4_sources_p0: true
      },
      files: [
        {
          title: 'AI 数字人技术进展 PDF 派生样本',
          file_name: basename(selectedPdfPath),
          content_type: 'application/pdf',
          source_type: 'pdf',
          content_base64: contentBase64,
          metadata: {
            file_name: basename(selectedPdfPath),
            file_import_contract: 'browser_base64_upload',
            v1_4_sources_p0: true
          }
        }
      ]
    }
  });
  return { sourceId: result.ok ? extractSourceId(result.payload) : null, payload: result.payload, status: result.status, ok: result.ok };
}

async function pollOperation(operationId) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
    const data = dataOf(latest);
    const status = data?.operation?.status ?? data?.status ?? latest?.status;
    if (['completed', 'failed', 'cancelled', 'blocked'].includes(status)) return { status, payload: latest };
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return { status: 'poll_timeout', payload: latest };
}

async function previewSource(sourceId) {
  const result = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/preview`);
  return result;
}

async function queryWorkspace(question) {
  return mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
    method: 'POST',
    body: { query: question, top_k: 8 }
  });
}

try {
  const markdown = await prepareMaterials();
  mark('material preparation', 'pass', 'AI数字人 Markdown/TXT/PDF samples prepared');

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

  const mdSource = await createTextSource('markdown', 'AI 数字人行业概览 Markdown', markdown['01_industry_overview.md'], {
    file_name: '01_industry_overview.md'
  });
  fixtures['markdown-import-success.json'] = mdSource.payload;
  mark('markdown import', 'pass', mdSource.sourceId);

  const txtContent = await readFile(join(manualDir, 'ai-digital-human-sample.txt'), 'utf8');
  const txtSource = await createTextSource('text', 'AI 数字人行业概览 TXT 派生样本', txtContent, {
    file_name: 'ai-digital-human-sample.txt',
    generated_from: '01_industry_overview.md'
  });
  fixtures['txt-import-success.json'] = txtSource.payload;
  mark('txt import', 'pass', txtSource.sourceId);

  const pdfSource = await createPdfBrowserUploadSource();
  fixtures['pdf-import-attempt.json'] = pdfSource.payload;
  mark(
    'pdf browser upload import',
    pdfSource.sourceId ? 'pass' : 'degraded',
    pdfSource.sourceId ?? `HTTP ${pdfSource.status} source_id missing`
  );

  fixtures['source-list.json'] = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
  mark('source list', 'pass');

  const build = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = extractOperationId(build);
  if (operationId) {
    const buildResult = await pollOperation(operationId);
    fixtures['workspace-build-result.json'] = buildResult.payload;
    mark('workspace build', buildResult.status === 'completed' ? 'pass' : 'degraded', buildResult.status);
  } else {
    mark('workspace build', 'degraded', 'operation_id missing');
  }

  const mdPreview = await previewSource(mdSource.sourceId);
  fixtures['markdown-preview.json'] = { status: mdPreview.status, payload: mdPreview.payload };
  if (!mdPreview.ok || !extractPreviewText(mdPreview.payload)) throw new Error('markdown preview missing text');
  mark('markdown preview', 'pass');

  const txtPreview = await previewSource(txtSource.sourceId);
  fixtures['txt-preview.json'] = { status: txtPreview.status, payload: txtPreview.payload };
  if (!txtPreview.ok || !extractPreviewText(txtPreview.payload)) throw new Error('txt preview missing text');
  mark('txt preview', 'pass');

  let pdfClassification = 'PDF_ROUTE_UNSUPPORTED';
  if (pdfSource.sourceId) {
    const pdfPreview = await previewSource(pdfSource.sourceId);
    fixtures['pdf-preview-attempt.json'] = { status: pdfPreview.status, payload: pdfPreview.payload };
    const pdfText = pdfPreview.ok ? extractPreviewText(pdfPreview.payload) : '';
    if (pdfPreview.ok && pdfText.includes('VASA')) {
      pdfClassification = 'PDF_EXTRACTED';
      mark('pdf preview', 'pass', pdfClassification);
    } else if (pdfPreview.ok) {
      pdfClassification = 'PDF_METADATA_ONLY';
      mark('pdf preview', 'degraded', pdfClassification);
    } else if (pdfPreview.status === 400 || pdfPreview.status === 422 || pdfPreview.status === 404) {
      pdfClassification = 'PDF_ROUTE_UNSUPPORTED';
      mark('pdf preview', 'degraded', `${pdfClassification} HTTP ${pdfPreview.status}`);
    } else {
      pdfClassification = 'PDF_PARSE_FAILED';
      mark('pdf preview', 'degraded', `${pdfClassification} HTTP ${pdfPreview.status}`);
    }
  }

  fixtures['markdown-query-citation.json'] = await queryWorkspace('中国与海外 AI 数字人市场的主要落地场景有何不同？');
  if (!hasCitation(fixtures['markdown-query-citation.json'])) throw new Error('markdown query did not return citation-like evidence');
  mark('markdown query citation', 'pass');

  fixtures['txt-query-citation.json'] = await queryWorkspace('为什么不同研究机构的 AI 数字人市场规模差异很大？');
  if (!hasCitation(fixtures['txt-query-citation.json'])) throw new Error('txt query did not return citation-like evidence');
  mark('txt query citation', 'pass');

  if (pdfClassification === 'PDF_EXTRACTED') {
    fixtures['pdf-query-citation.json'] = await queryWorkspace('VASA-1 与 OmniHuman-1 解决的问题有什么不同？');
    if (!hasCitation(fixtures['pdf-query-citation.json'])) {
      pdfClassification = 'PDF_PARSE_FAILED';
      mark('pdf query citation', 'degraded', 'PDF extracted but no citation-like evidence');
    } else {
      mark('pdf query citation', 'pass');
    }
  }

  finalDecision = pdfClassification === 'PDF_EXTRACTED' ? 'PASS_LIMITED' : 'BLOCKED_BY_BACKEND_CONTRACT';
  fixtures['v1_4_sources_p0_result.json'] = {
    decision: finalDecision,
    pdf_classification: pdfClassification,
    workspace_id: workspaceId,
    source_ids: {
      markdown: mdSource.sourceId,
      txt: txtSource.sourceId,
      pdf: pdfSource.sourceId ?? null
    },
    material_folder_label: '技术分享/11-数字人/AI数字人资料包',
    results
  };

  if (hasRawPath(fixtures)) {
    mark('fixture raw path hygiene before sanitization', 'degraded', 'raw path-like values redacted in saved fixtures');
  } else {
    mark('fixture raw path hygiene before sanitization', 'pass');
  }
  await saveFixtures();
} catch (error) {
  mark('v1.4 sources p0 smoke', 'fail', error.message);
  finalDecision = 'FAIL';
  fixtures['v1_4_sources_p0_result.json'] = {
    decision: finalDecision,
    error: error.message,
    workspace_id: workspaceId || null,
    results
  };
  await saveFixtures().catch(() => {});
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    const cleanup = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
      method: 'POST',
      body: { reason: 'v1.4 sources p0 smoke cleanup' }
    });
    fixtures['workspace-cleanup.json'] = { status: cleanup.status, payload: cleanup.payload };
    mark('workspace cleanup', cleanup.ok ? 'pass' : 'degraded', `HTTP ${cleanup.status}`);
    await saveFixtures().catch(() => {});
  }
  console.log(`FINAL ${finalDecision}`);
}
