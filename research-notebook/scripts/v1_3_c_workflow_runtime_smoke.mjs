/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const folderRoot = process.env.RN_V13_FOLDER_ROOT ?? '/Users/Zhuanz/Desktop/技术分享';
const prefix = process.env.RN_V13C_WORKSPACE_PREFIX ?? `rn-v13c-runtime-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'workflow-runtime');

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
    result_count: results.length,
    results,
    final_decision: finalDecision
  };
  await Promise.all(
    Object.entries({ ...fixtures, 'v1-3-c-workflow-runtime-result.json': summary }).map(([name, payload]) =>
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
  return /\/Users|file:\/\/|cache_path|artifact_path|physical_path|\/private\/tmp|\/tmp\//.test(JSON.stringify(value));
}

function assertWorkflowRuntime(payload) {
  if (hasSensitivePath(payload)) throw new Error('workflow runtime response leaked path-like values');
  const data = dataOf(payload);
  const workflow = data?.workflow;
  const run = data?.run;
  const collection = data?.collection;
  if (!workflow || !run || !collection) throw new Error('workflow/run/collection missing');
  if (workflow.template_id !== 'folder_summary_v1') throw new Error('unexpected workflow template_id');
  if (!Array.isArray(workflow.steps) || workflow.steps.length < 7) throw new Error('workflow steps missing');
  const statuses = Object.fromEntries(workflow.steps.map((step) => [step.name, step.status]));
  if (statuses.scan_folder !== 'completed') throw new Error('scan_folder did not complete');
  if (statuses.group_by_subfolder !== 'completed') throw new Error('group_by_subfolder did not complete');
  for (const name of ['extract_text', 'create_sources', 'summarize_folder', 'generate_index_report', 'write_artifacts']) {
    if (statuses[name] !== 'skipped') throw new Error(`${name} must be skipped in V1.3-C dry-run`);
  }
  if (run.dry_run !== true) throw new Error('workflow run must be dry_run=true');
  if (!run.run_report || run.run_report.generated_artifact_count !== 0 || run.run_report.extracted_file_count !== 0) {
    throw new Error('V1.3-C dry-run should not generate artifacts or extract files');
  }
  if (Array.isArray(run.artifacts) && run.artifacts.length > 0) throw new Error('V1.3-C run should not return artifacts');
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
      dry_run: true,
      recursive: true,
      include_extensions: ['.md', '.txt'],
      exclude_globs: ['**/*.tmp'],
      max_depth: 16,
      follow_symlinks: false
    }
  });
  fixtures['workflow-runtime-dry-run-success.json'] = run;
  assertWorkflowRuntime(run);
  const data = dataOf(run);
  mark(
    'workflow dry-run runtime',
    'pass',
    `steps=${data.workflow.steps.length} files=${data.collection.files.length} skipped=${data.collection.skipped_files.length}`
  );

  const nonDryRun = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/workflows/folder-summary/runs`, {
    method: 'POST',
    body: {
      authorized_root: folderRoot,
      permission_grant_id: `grant_non_dry_${Date.now()}`,
      dry_run: false
    }
  });
  fixtures['workflow-runtime-non-dry-run-rejected.json'] = nonDryRun.payload;
  if (nonDryRun.status !== 422) throw new Error(`dry_run=false should be rejected, got HTTP ${nonDryRun.status}`);
  mark('workflow dry_run false rejected', 'pass', 'HTTP 422');

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  finalDecision = 'BLOCKED';
  mark('v1.3-c workflow runtime smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.3-c workflow runtime smoke cleanup' }
      });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
