/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const folderRoot = process.env.RN_V13_FOLDER_ROOT ?? '/Users/Zhuanz/Desktop/技术分享';
const prefix = process.env.RN_V13G_WORKSPACE_PREFIX ?? `rn-v13g-evidence-summary-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'evidence-backed-summary');

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
    Object.entries({ ...fixtures, 'v1-3-g-evidence-backed-summary-result.json': summary }).map(([name, payload]) =>
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

function findJumpableEvidence(payload) {
  const data = dataOf(payload);
  const artifacts = Array.isArray(data?.run?.artifacts) ? data.run.artifacts : [];
  for (const artifact of artifacts) {
    const refs = Array.isArray(artifact.evidence_refs) ? artifact.evidence_refs : [];
    const ref = refs.find((item) => item.evidence_status === 'source_unit_span' && item.source_id && item.unit_id && item.evidence_id);
    if (ref) return { artifact, ref };
  }
  return null;
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
  fixtures['evidence-backed-summary-run.json'] = run;
  if (hasSensitivePath(run)) throw new Error('summary run response leaked path-like values');
  const found = findJumpableEvidence(run);
  if (!found) throw new Error('no source_unit_span evidence ref found in summary artifacts');
  mark('summary evidence refs', 'pass', `source_id=${found.ref.source_id}`);

  const unit = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(found.ref.source_id)}/units/${encodeURIComponent(found.ref.unit_id)}`
  );
  fixtures['summary-evidence-unit-detail.json'] = unit;
  const unitData = dataOf(unit)?.unit;
  if (unitData?.source_id !== found.ref.source_id || unitData?.unit_id !== found.ref.unit_id) {
    throw new Error('unit detail did not resolve summary evidence ref');
  }
  mark('unit detail resolution', 'pass', found.ref.unit_id);

  const evidence = await mustRequest(
    `/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(found.ref.source_id)}/units/${encodeURIComponent(found.ref.unit_id)}/evidence/${encodeURIComponent(found.ref.evidence_id)}`
  );
  fixtures['summary-evidence-span-detail.json'] = evidence;
  const span = dataOf(evidence)?.evidence_span;
  if (span?.source_id !== found.ref.source_id || span?.unit_id !== found.ref.unit_id || span?.evidence_id !== found.ref.evidence_id) {
    throw new Error('EvidenceSpan detail did not resolve summary evidence ref');
  }
  if (span.offset_basis !== 'normalized_text' || span.offset_range !== 'half_open' || span.text_basis !== 'document_unit_text') {
    throw new Error('EvidenceSpan offset contract mismatch');
  }
  mark('EvidenceSpan resolution', 'pass', found.ref.evidence_id);

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  finalDecision = 'BLOCKED';
  mark('v1.3-g evidence-backed summary smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.3-g evidence-backed summary smoke cleanup' }
      });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
