/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const folderRoot = process.env.RN_V13_FOLDER_ROOT ?? '/Users/Zhuanz/Desktop/技术分享';
const prefix = process.env.RN_V13D_WORKSPACE_PREFIX ?? `rn-v13d-summary-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'summary-generator');

const fixtures = {};
const results = [];
let workspaceId = '';
let finalDecision = 'BLOCKED';

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
        lowered === 'authorized_root' ||
        lowered === 'markdown' ||
        lowered === 'path' ||
        lowered === 'paths' ||
        lowered.endsWith('_path') ||
        lowered.endsWith('_paths') ||
        lowered.includes('physical') ||
        lowered.includes('cache') ||
        lowered.includes('stack')
      ) {
        if (lowered === 'markdown') out[key] = '[summary-redacted]';
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
  const summary = {
    base_url: baseUrl,
    workspace_id: workspaceId,
    result_count: results.length,
    results,
    final_decision: finalDecision
  };
  await Promise.all(
    Object.entries({ ...fixtures, 'v1-3-d-summary-generator-result.json': summary }).map(([name, payload]) =>
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
  if (!result.ok) throw new Error(`HTTP ${result.status} ${path}`);
  return result.payload;
}

function dataOf(payload) {
  return payload && typeof payload === 'object' && payload.data && typeof payload.data === 'object' ? payload.data : payload;
}

function hasSensitivePath(value) {
  return hasSensitivePathValue(value);
}

function hasSensitivePathValue(value) {
  if (Array.isArray(value)) return value.some(hasSensitivePathValue);
  if (value && typeof value === 'object') {
    for (const [key, item] of Object.entries(value)) {
      if (key.toLowerCase() === 'markdown') continue;
      if (/cache_path|artifact_path|physical_path/.test(key.toLowerCase())) return true;
      if (hasSensitivePathValue(item)) return true;
    }
    return false;
  }
  if (typeof value !== 'string') return false;
  return value.startsWith('/Users') || value.startsWith('/private/tmp') || value.startsWith('/tmp/') || value.startsWith('file://');
}

function assertSummaryGenerator(payload) {
  if (hasSensitivePath(payload)) throw new Error('summary generator response leaked path-like values');
  const data = dataOf(payload);
  const run = data?.run;
  const artifacts = Array.isArray(run?.artifacts) ? run.artifacts : [];
  if (run?.dry_run !== false) throw new Error('summary generator must run with dry_run=false after confirmation');
  if (!run?.run_report || run.run_report.generated_artifact_count !== artifacts.length || artifacts.length < 2) {
    throw new Error('summary artifacts missing or count mismatch');
  }
  if (run.run_report.extracted_file_count <= 0) throw new Error('expected extracted md/txt files');
  const root = artifacts.find((artifact) => artifact.artifact_type === 'root_summary');
  if (!root) throw new Error('root summary artifact missing');
  for (const artifact of artifacts) {
    if (artifact.status !== 'ready') throw new Error('summary artifact not ready');
    if (artifact.schema_version !== 'v1.3-summary-artifact') throw new Error('summary schema mismatch');
    if (!artifact.markdown || !String(artifact.markdown).includes('## 概览')) throw new Error('summary markdown missing required sections');
    if (!Array.isArray(artifact.evidence_refs) || artifact.evidence_refs.length === 0) throw new Error('summary evidence refs missing');
    for (const ref of artifact.evidence_refs) {
      if (ref.evidence_status === 'source_unit_span' && (!ref.source_id || !ref.unit_id || !ref.evidence_id)) {
        throw new Error('source_unit_span evidence refs must include source_id, unit_id, and evidence_id');
      }
      if (ref.evidence_status !== 'relative_path_only' && ref.evidence_status !== 'source_unit_span') {
        throw new Error('summary evidence refs must be relative_path_only or source_unit_span');
      }
    }
  }
}

try {
  const probe = await request('/api/workspaces');
  if (!probe.ok) throw new Error(`target route probe failed: HTTP ${probe.status}`);
  mark('target route probe', 'pass', baseUrl);

  const created = await mustRequest('/api/workspaces', {
    method: 'POST',
    body: { name: `${prefix}-workspace` }
  });
  workspaceId = dataOf(created)?.workspace?.workspace_id ?? created?.workspace_id;
  if (!workspaceId) throw new Error('workspace_id missing after create');
  mark('workspace create', 'pass', workspaceId);

  const run = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflows/folder-summary/runs`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_${Date.now()}`,
      dry_run: false,
      confirm_extract: true,
      recursive: true,
      include_extensions: ['.md', '.txt'],
      exclude_globs: ['**/*.tmp'],
      max_depth: 16,
      follow_symlinks: false
    }
  });
  fixtures['summary-generator-success.json'] = run;
  assertSummaryGenerator(run);
  const data = dataOf(run);
  mark(
    'summary generator',
    'pass',
    `artifacts=${data.run.artifacts.length} extracted=${data.run.run_report.extracted_file_count}`
  );

  const rejected = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflows/folder-summary/runs`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_reject_${Date.now()}`,
      dry_run: false,
      confirm_extract: false
    }
  });
  fixtures['summary-generator-confirm-extract-rejected.json'] = rejected.payload;
  if (rejected.status !== 422) throw new Error(`confirm_extract=false should be rejected, got HTTP ${rejected.status}`);
  mark('confirm_extract required', 'pass', 'HTTP 422');

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  finalDecision = 'BLOCKED';
  mark('v1.3-d summary generator smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.3-d summary generator smoke cleanup' }
      });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
