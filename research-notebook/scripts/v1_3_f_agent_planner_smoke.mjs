/* global fetch */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_V13F_WORKSPACE_PREFIX ?? `rn-v13f-agent-planner-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real', 'v1_3', 'agent-planner');

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
    Object.entries({ ...fixtures, 'v1-3-f-agent-planner-result.json': summary }).map(([name, payload]) =>
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

function assertAgentDraft(payload) {
  if (hasSensitivePath(payload)) throw new Error('agent draft response leaked path-like values');
  const data = dataOf(payload);
  const task = data?.task;
  const workflow = data?.workflow;
  if (!task || task.status !== 'awaiting_approval') throw new Error('AgentTask must wait for user approval');
  if (!workflow || workflow.status !== 'draft') throw new Error('Workflow draft missing');
  if (workflow.template_id !== 'folder_summary_v1') throw new Error('unexpected workflow template');
  if (!Array.isArray(workflow.steps) || workflow.steps.length < 5) throw new Error('workflow steps missing');
  if (!workflow.required_permissions?.includes('folder:scan')) throw new Error('folder scan permission missing');
  if (!workflow.required_permissions?.includes('folder:extract:md_txt')) throw new Error('md/txt extraction permission missing');
  if (workflow.draft_parameters?.follow_symlinks !== false) throw new Error('follow_symlinks must default false');
  if (workflow.draft_parameters?.requires_user_confirmation !== true) throw new Error('draft must require user confirmation');
  if (workflow.draft_parameters?.authorized_root_hint !== 'Desktop/技术分享') throw new Error('authorized root hint mismatch');
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

  const draft = await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/agent-workflows/draft`, {
    method: 'POST',
    body: { user_goal: '递归总结 Desktop/技术分享，每个子文件夹生成一份总结。' }
  });
  fixtures['agent-workflow-draft-success.json'] = draft;
  assertAgentDraft(draft);
  mark('agent workflow draft', 'pass', 'template=folder_summary_v1');

  const rejected = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/agent-workflows/draft`, {
    method: 'POST',
    body: { user_goal: '整理全部图片并生成视频' }
  });
  fixtures['agent-workflow-draft-unsupported-goal.json'] = rejected.payload;
  if (rejected.status !== 422) throw new Error(`unsupported goal should be rejected, got HTTP ${rejected.status}`);
  mark('unsupported goal rejected', 'pass', 'HTTP 422');

  finalDecision = 'PASS_LIMITED';
} catch (error) {
  finalDecision = 'BLOCKED';
  mark('v1.3-f agent planner smoke', 'fail', error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
} finally {
  if (workspaceId) {
    try {
      await mustRequest(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, {
        method: 'POST',
        body: { reason: 'v1.3-f agent planner smoke cleanup' }
      });
      mark('workspace archive cleanup', 'pass', workspaceId);
    } catch (error) {
      mark('workspace archive cleanup', 'fail', error instanceof Error ? error.message : String(error));
    }
  }
  await saveFixtures();
  console.log(`FINAL ${finalDecision}`);
}
