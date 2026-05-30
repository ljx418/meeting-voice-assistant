/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const folderRoot = process.env.RN_V13_FOLDER_ROOT ?? '/Users/Zhuanz/Desktop/技术分享';
const prefix = process.env.RN_V13B_WORKSPACE_PREFIX ?? `rn-v13b-folder-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'folder-collections');

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
  const summary = {
    base_url: baseUrl,
    workspace_id: workspaceId,
    root_label: fixtures['folder-scan-success.json']?.data?.collection?.root_label,
    result_count: results.length,
    results,
    final_decision: finalDecision
  };
  await Promise.all(
    Object.entries({ ...fixtures, 'v1-3-b-folder-connector-result.json': summary }).map(([name, payload]) =>
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

function hasSensitivePath(value) {
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

function assertFolderScan(payload) {
  if (hasSensitivePath(payload)) throw new Error('folder scan response leaked path-like values');
  const data = dataOf(payload);
  const collection = data?.collection;
  if (!collection || typeof collection !== 'object') throw new Error('collection missing');
  if (!Array.isArray(collection.folders) || collection.folders.length === 0) throw new Error('folders[] missing');
  if (!Array.isArray(collection.files)) throw new Error('files[] missing');
  if (!Array.isArray(collection.skipped_files)) throw new Error('skipped_files[] missing');
  if (!collection.folders.some((folder) => folder.relative_path !== '.')) {
    throw new Error('expected at least one discovered subfolder');
  }
  for (const file of collection.files) {
    if (!['.md', '.txt'].includes(file.extension)) throw new Error(`unexpected supported extension: ${file.extension}`);
    if (String(file.relative_path || '').startsWith('/')) throw new Error('file relative_path is absolute');
  }
  for (const skipped of collection.skipped_files) {
    if (!skipped.relative_path || !skipped.skipped_reason) throw new Error('skipped file missing reason');
    if (String(skipped.relative_path).startsWith('/')) throw new Error('skipped relative_path is absolute');
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

  const scan = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/folder-collections/scan`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_${Date.now()}`,
      dry_run: true,
      recursive: true,
      include_extensions: ['.md', '.txt'],
      exclude_globs: ['**/*.tmp'],
      max_depth: 16,
      follow_symlinks: false
    }
  });
  fixtures['folder-scan-success.json'] = scan;
  assertFolderScan(scan);
  const collection = dataOf(scan).collection;
  mark(
    'folder scan dry-run manifest',
    'pass',
    `folders=${collection.folders.length} files=${collection.files.length} skipped=${collection.skipped_files.length}`
  );

  const extractAttempt = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/folder-collections/scan`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_extract_${Date.now()}`,
      dry_run: false,
      follow_symlinks: false
    }
  });
  fixtures['folder-scan-extract-rejected.json'] = extractAttempt.payload;
  if (extractAttempt.status !== 422) throw new Error(`dry_run=false should be rejected, got HTTP ${extractAttempt.status}`);
  mark('dry_run false rejected', 'pass', 'HTTP 422');

  const unsupportedAttempt = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/folder-collections/scan`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_json_${Date.now()}`,
      dry_run: true,
      include_extensions: ['.json'],
      follow_symlinks: false
    }
  });
  fixtures['folder-scan-unsupported-extension-rejected.json'] = unsupportedAttempt.payload;
  if (unsupportedAttempt.status !== 422) throw new Error(`unsupported include extension should be rejected, got HTTP ${unsupportedAttempt.status}`);
  mark('unsupported include extension rejected', 'pass', 'HTTP 422');

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  finalDecision = 'BLOCKED';
  mark('v1.3-b folder connector smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.3-b folder connector smoke cleanup' }
      });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
