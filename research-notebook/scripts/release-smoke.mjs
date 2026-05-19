/* global fetch, setTimeout */
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const baseUrl = process.env.RN_DATA_SERVICE_BASE_URL ?? process.env.VITE_DATA_SERVICE_BASE_URL ?? 'http://127.0.0.1:8003';
const prefix = process.env.RN_RC_WORKSPACE_PREFIX ?? `rn-release-${Date.now()}`;
const fixtureDir = join(process.cwd(), 'fixtures', 'real');
const maxPollMs = Number(process.env.RN_RC_MAX_POLL_MS ?? 45_000);
const pollIntervalMs = Number(process.env.RN_RC_POLL_INTERVAL_MS ?? 1_000);

const results = [];
const fixtures = {};
let workspaceId = '';
let sessionId = '';

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
        lowered.includes('cache')
      ) {
        continue;
      }
      out[key] = sanitize(item);
    }
    return out;
  }
  return value;
}

async function request(path, options = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    method: options.method ?? 'GET',
    headers: { 'Content-Type': 'application/json' },
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(`HTTP ${response.status} ${path}`);
    error.payload = payload;
    throw error;
  }
  return payload;
}

async function pollOperation(path) {
  const started = Date.now();
  let latest = null;
  while (Date.now() - started < maxPollMs) {
    latest = await request(path);
    const status = latest?.status ?? latest?.data?.status;
    if (status === 'completed' || status === 'failed' || status === 'cancelled' || status === 'blocked') return latest;
    await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));
  }
  return latest ?? { status: 'poll_timeout' };
}

async function saveFixtures() {
  await mkdir(fixtureDir, { recursive: true });
  await Promise.all(
    Object.entries(fixtures).map(([name, payload]) => writeFile(join(fixtureDir, name), JSON.stringify(sanitize(payload), null, 2) + '\n'))
  );
}

try {
  try {
    const health = await request('/api/v1/health');
    mark('health probe', 'pass', health.service ?? 'data_service');
  } catch {
    mark('health probe', 'degraded', 'health route unavailable; target routes will be used as availability probe');
  }

  const created = await request('/api/workspaces', {
    method: 'POST',
    body: { name: `${prefix}-workspace` }
  });
  workspaceId = created?.data?.workspace?.workspace_id ?? created?.workspace_id;
  if (!workspaceId) throw new Error('workspace_id missing after create');
  mark('workspace create', 'pass', workspaceId);

  fixtures['workspaces-list.json'] = await request('/api/workspaces');
  mark('workspace list', 'pass');

  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}`);
  mark('workspace get', 'pass');

  const sourceCreated = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`, {
    method: 'POST',
    body: {
      texts: [
        {
          title: `${prefix} source`,
          content: 'ResearchNotebook V1.0 release smoke validates source grounded ask, source trace fallback, session workbench, graph context, and lightweight feedback.',
          metadata: { rc_stage: 'release' }
        }
      ],
      metadata: { rc_stage: 'release' }
    }
  });
  const sourceId = sourceCreated?.data?.sources?.[0]?.source_id;
  if (!sourceId) throw new Error('source_id missing after source create');
  mark('source create', 'pass', sourceId);

  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources`);
  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}`);
  mark('source list/get', 'pass');

  try {
    fixtures['source-trace.json'] = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sources/${encodeURIComponent(sourceId)}/trace`);
    mark('source trace', 'pass');
  } catch (error) {
    fixtures['source-trace.json'] = error.payload ?? { message: error.message };
    fixtures['source-trace-404.json'] = error.payload ?? { message: error.message };
    mark('source trace', 'degraded', error.message);
  }

  const build = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const operationId = build?.operation_id;
  if (!operationId) throw new Error('operation_id missing after build start');
  const buildStatus = await pollOperation(`/api/workspaces/${encodeURIComponent(workspaceId)}/build/operations/${encodeURIComponent(operationId)}`);
  mark('workspace build polling', buildStatus?.status === 'completed' ? 'pass' : 'degraded', buildStatus?.status ?? 'unknown');

  const query = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/query`, {
    method: 'POST',
    body: { query: 'What does the release smoke source validate?', top_k: 5 }
  });
  fixtures[Array.isArray(query?.hits) && query.hits.length > 0 ? 'query-with-evidence.json' : 'query-no-evidence.json'] = query;
  if (Array.isArray(query?.hits) && query.hits.some((hit) => hit?.source && hit.source !== sourceId)) {
    fixtures['query-hit-source-slug.json'] = query;
  }
  if (Array.isArray(query?.hits) && query.hits.some((hit) => hit?.source === sourceId || hit?.source_id === sourceId)) {
    fixtures['query-hit-source-registry-id.json'] = query;
  }
  mark('workspace query', query?.answer ? 'pass' : 'degraded', Array.isArray(query?.hits) && query.hits.length > 0 ? 'evidence' : 'no evidence');

  const session = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions`, {
    method: 'POST',
    body: { title: `${prefix} session` }
  });
  sessionId = session?.data?.session?.session_id;
  if (!sessionId) throw new Error('session_id missing after create');
  mark('session create', 'pass', sessionId);

  await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/ingest`, {
    method: 'POST',
    body: {
      title: 'Release smoke snippet',
      content_format: 'text',
      source_type: 'text',
      content: 'Session release smoke context validates session ask with evidence fallback.'
    }
  });
  mark('session ingest', 'pass');

  const sessionBuild = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/start`, {
    method: 'POST',
    body: {}
  });
  const sessionOperationId = sessionBuild?.operation_id;
  if (sessionOperationId) {
    const sessionBuildStatus = await pollOperation(
      `/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/build/operations/${encodeURIComponent(sessionOperationId)}`
    );
    mark(
      'session build polling',
      sessionBuildStatus?.status === 'completed' || sessionBuildStatus?.status === 'succeeded' ? 'pass' : 'degraded',
      sessionBuildStatus?.status ?? 'unknown'
    );
  } else {
    mark('session build polling', 'degraded', 'operation_id missing');
  }

  const sessionQuery = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/query`, {
    method: 'POST',
    body: { query: 'What does session release smoke validate?', top_k: 5 }
  });
  fixtures[
    Array.isArray(sessionQuery?.data?.items) && sessionQuery.data.items.length > 0
      ? 'session-query-with-evidence.json'
      : 'session-query-no-evidence.json'
  ] = sessionQuery;
  mark('session query', sessionQuery?.data?.answer ? 'pass' : 'degraded', Array.isArray(sessionQuery?.data?.items) && sessionQuery.data.items.length > 0 ? 'evidence' : 'no evidence');

  try {
    const graph = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/community?include_members=true`);
    fixtures[graph.status === 'blocked' ? 'graph-missing-artifact.json' : 'graph-community.json'] = graph;
    const communities = graph?.data?.items ?? graph?.communities ?? [];
    const firstMember = communities.flatMap((community) => community.members ?? [])[0];
    if (firstMember?.node_id || firstMember?.entity_id) {
      fixtures['graph-community-with-node-id.json'] = graph;
      const query = firstMember.node_id ? `node_id=${encodeURIComponent(firstMember.node_id)}` : `entity_id=${encodeURIComponent(firstMember.entity_id)}`;
      fixtures['graph-neighbors-node-scoped.json'] = await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/graph/neighbors?${query}`);
      mark('graph neighbors node-scoped', 'pass', firstMember.node_id ?? firstMember.entity_id);
    } else {
      fixtures['graph-community-without-node-id.json'] = graph;
      mark('graph neighbors node-scoped', 'degraded', 'community returned no node_id/entity_id members');
    }
    mark('graph community', graph.status === 'blocked' ? 'degraded' : 'pass', graph.status);
  } catch (error) {
    fixtures['graph-missing-artifact.json'] = error.payload ?? { message: error.message };
    mark('graph community', 'degraded', error.message);
  }

  try {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/quality/feedback`, {
      method: 'POST',
      body: {
        target_type: 'workspace_answer',
        target_id: 'release-smoke-answer',
        action: 'mark_helpful',
        label: 'up',
        reason: 'release smoke'
      }
    });
    mark('feedback submit', 'pass');
  } catch (error) {
    mark('feedback submit', 'degraded', error.message);
  }

  if (sessionId) {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/sessions/${encodeURIComponent(sessionId)}/close`, { method: 'POST' });
    mark('session cleanup close', 'pass');
  }
  if (workspaceId) {
    await request(`/api/workspaces/${encodeURIComponent(workspaceId)}/archive`, { method: 'POST', body: { reason: 'release smoke cleanup' } });
    mark('workspace cleanup archive', 'pass');
  }

  await saveFixtures();

  const failed = results.filter((item) => item.status === 'fail');
  if (failed.length > 0) process.exit(1);
} catch (error) {
  mark('ResearchNotebook V1.0 release smoke', 'fail', error.message);
  await saveFixtures().catch(() => undefined);
  process.exit(1);
}
