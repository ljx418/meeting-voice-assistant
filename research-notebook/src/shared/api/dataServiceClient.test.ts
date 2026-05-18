import { describe, expect, it, vi } from 'vitest';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { createDataServiceClient, DataServiceError } from './dataServiceClient';

const workspacesPath = ['', 'api', 'workspaces'].join('/');
const workspacePath = (workspaceId: string) => [workspacesPath, workspaceId].join('/');
const sourcesPath = (workspaceId: string) => [workspacePath(workspaceId), 'sources'].join('/');
const sessionsPath = (workspaceId: string) => [workspacePath(workspaceId), 'sessions'].join('/');
const sessionPath = (workspaceId: string, sessionId: string) => [sessionsPath(workspaceId), sessionId].join('/');

function jsonResponse(payload: unknown, init?: ResponseInit) {
  return new Response(JSON.stringify(payload), {
    status: init?.status ?? 200,
    headers: {
      'Content-Type': 'application/json'
    }
  });
}

function realFixture(name: string) {
  return JSON.parse(readFileSync(join(process.cwd(), 'fixtures', 'real', name), 'utf8')) as unknown;
}

describe('dataServiceClient workspace wrappers', () => {
  it('loads workspace list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspaces: [{ workspace_id: 'ws_1', name: 'Research' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).resolves.toEqual([{ workspace_id: 'ws_1', name: 'Research' }]);
    expect(fetchImpl).toHaveBeenCalledWith(workspacesPath, expect.objectContaining({ method: 'GET' }));
  });

  it('creates workspace successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace: { workspace_id: 'ws_2', name: 'Interviews' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.create({ name: 'Interviews' })).resolves.toEqual({
      workspace: { workspace_id: 'ws_2', name: 'Interviews' }
    });
    expect(fetchImpl).toHaveBeenCalledWith(
      workspacesPath,
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ name: 'Interviews' }) })
    );
  });

  it('normalizes backend unavailable errors', async () => {
    const fetchImpl = vi.fn().mockRejectedValue(new TypeError('network failed'));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).rejects.toMatchObject({
      code: 'backend_unavailable',
      retryable: true
    });
  });

  it('normalizes not found errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'missing workspace' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.get('missing')).rejects.toMatchObject({
      code: 'not_found',
      status: 404
    });
  });

  it('normalizes validation errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'name is required' }, { status: 422 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.create({ name: '' })).rejects.toMatchObject({
      code: 'validation_error',
      status: 422,
      retryable: false
    });
  });

  it('normalizes schema mismatch during response validation', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ workspaces: [{ name: 'Missing id' }] }));
    const client = createDataServiceClient({ fetchImpl });

    const result = client.workspaces.list();
    await expect(result).rejects.toBeInstanceOf(DataServiceError);
    await expect(result).rejects.toMatchObject({
      code: 'version_or_schema_mismatch'
    });
  });

  it('loads source list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'System design', trace_available: true }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.list('ws_1')).resolves.toEqual([
      expect.objectContaining({ source_id: 'src_1', workspace_id: 'ws_1', title: 'System design' })
    ]);
    expect(fetchImpl).toHaveBeenCalledWith(sourcesPath('ws_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('creates source successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source: { source_id: 'src_2', workspace_id: 'ws_1', title: 'Algorithms' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.create('ws_1', { title: 'Algorithms' })).resolves.toEqual({
      source: expect.objectContaining({ source_id: 'src_2', title: 'Algorithms' })
    });
  });

  it('loads source trace successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        source_id: 'src_1',
        title: 'System design',
        artifact_refs: ['artifact:1'],
        provenance: [{ label: 'Imported', value: 'today' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'src_1')).resolves.toEqual(
      expect.objectContaining({ source_id: 'src_1', trace_available: true })
    );
  });

  it('starts workspace build successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.start('ws_1')).resolves.toEqual({ operation_id: 'op_1' });
  });

  it('loads build operation status successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1', status: 'running' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.getOperation('ws_1', 'op_1')).resolves.toEqual(
      expect.objectContaining({ operation_id: 'op_1', status: 'running', cancellable: true })
    );
  });

  it('maps unknown build operation status to operation unavailable', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_1', status: 'paused_elsewhere' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.build.getOperation('ws_1', 'op_1')).resolves.toEqual(
      expect.objectContaining({ status: 'operation_unavailable' })
    );
  });

  it('normalizes query response with evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Use queues for backpressure.',
        evidence: [{ source_id: 'src_1', source_title: 'Architecture notes', snippet: 'queue depth' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'How handle load?' })).resolves.toEqual({
      answer: 'Use queues for backpressure.',
      evidence: [
        expect.objectContaining({
          sourceId: 'src_1',
          sourceTitle: 'Architecture notes',
          traceAvailable: true
        })
      ],
      noEvidence: false
    });
  });

  it('normalizes query response without evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ answer: 'No grounded source returned.' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('ws_1', { question: 'Anything?' })).resolves.toEqual({
      answer: 'No grounded source returned.',
      evidence: [],
      noEvidence: true
    });
  });

  it('normalizes source trace not found', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'source missing' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sources.trace('ws_1', 'missing')).rejects.toMatchObject({ code: 'not_found' });
  });

  it('loads session list successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        sessions: [{ session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'active' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.list('ws_1')).resolves.toEqual([
      expect.objectContaining({ session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'active' })
    ]);
    expect(fetchImpl).toHaveBeenCalledWith(sessionsPath('ws_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('creates session successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session: { session_id: 'ses_2', workspace_id: 'ws_1', title: 'Algorithms', state: 'active' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.create('ws_1', { title: 'Algorithms' })).resolves.toEqual({
      session: expect.objectContaining({ session_id: 'ses_2', title: 'Algorithms' })
    });
  });

  it('loads session detail successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session_id: 'ses_1',
        workspace_id: 'ws_1',
        title: 'Interview prep',
        state: 'ready',
        artifact_refs: ['artifact:session']
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.get('ws_1', 'ses_1')).resolves.toEqual(
      expect.objectContaining({ session_id: 'ses_1', state: 'ready', artifact_refs: ['artifact:session'] })
    );
    expect(fetchImpl).toHaveBeenCalledWith(sessionPath('ws_1', 'ses_1'), expect.objectContaining({ method: 'GET' }));
  });

  it('closes session successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ session_id: 'ses_1', closed: true }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.close('ws_1', 'ses_1')).resolves.toEqual({ session_id: 'ses_1', closed: true });
  });

  it('ingests session snippet successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        session: { session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state: 'ingested_not_built' }
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.ingest('ws_1', 'ses_1', { content: 'queue notes' })).resolves.toEqual({
      session: expect.objectContaining({ session_id: 'ses_1', state: 'ingested_not_built' })
    });
  });

  it('starts session build successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_session' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.build.start('ws_1', 'ses_1')).resolves.toEqual({ operation_id: 'op_session' });
  });

  it('loads session build operation status successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ operation_id: 'op_session', status: 'running' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.build.getOperation('ws_1', 'ses_1', 'op_session')).resolves.toEqual(
      expect.objectContaining({ operation_id: 'op_session', status: 'running' })
    );
  });

  it('normalizes session query response with evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        answer: 'Review heap invariants.',
        evidence: [{ source_id: 'src_1', source_title: 'Heap notes' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.query('ws_1', 'ses_1', { question: 'What should I review?' })).resolves.toEqual({
      answer: 'Review heap invariants.',
      evidence: [expect.objectContaining({ sourceId: 'src_1', sourceTitle: 'Heap notes' })],
      noEvidence: false
    });
  });

  it('normalizes session query response without evidence', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ answer: 'No evidence returned.' }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.query('ws_1', 'ses_1', { question: 'Anything?' })).resolves.toEqual({
      answer: 'No evidence returned.',
      evidence: [],
      noEvidence: true
    });
  });

  it('normalizes session not found', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'session missing' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.sessions.get('ws_1', 'missing')).rejects.toMatchObject({ code: 'not_found' });
  });

  it('loads graph neighbors successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        nodes: [{ node_id: 'n_1', label: 'Queues', node_type: 'concept' }],
        edges: [{ edge_id: 'e_1', source_node_id: 'n_1', target_node_id: 'n_2', label: 'relates' }],
        neighbors: [{ node_id: 'n_2', label: 'Backpressure', relationship: 'mitigates' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.neighbors('ws_1')).resolves.toEqual(
      expect.objectContaining({
        workspace_id: 'ws_1',
        status: 'ready',
        neighbors: [expect.objectContaining({ node_id: 'n_2', label: 'Backpressure' })]
      })
    );
  });

  it('loads graph communities successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        communities: [{ community_id: 'c_1', title: 'Architecture', node_count: 4, relationship_count: 3 }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.communities('ws_1')).resolves.toEqual(
      expect.objectContaining({
        communities: [expect.objectContaining({ community_id: 'c_1', title: 'Architecture' })]
      })
    );
  });

  it('loads session graph context successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse({
        workspace_id: 'ws_1',
        session_id: 'ses_1',
        related_nodes: [{ node_id: 'n_1', label: 'Heap' }],
        related_communities: [{ community_id: 'c_1', title: 'Algorithms' }]
      })
    );
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.session('ws_1', 'ses_1')).resolves.toEqual(
      expect.objectContaining({
        session_id: 'ses_1',
        related_nodes: [expect.objectContaining({ node_id: 'n_1' })]
      })
    );
  });

  it('normalizes missing graph artifact errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'graph artifact no_artifact' }, { status: 404 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.neighbors('ws_1')).rejects.toMatchObject({ code: 'missing_graph_artifact' });
  });

  it('submits quality feedback successfully', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ feedback_id: 'fb_1', workspace_id: 'ws_1', accepted: true }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.quality.feedback('ws_1', { target_type: 'workspace_answer', rating: 'up' })).resolves.toEqual({
      feedback_id: 'fb_1',
      workspace_id: 'ws_1',
      accepted: true
    });
  });

  it('normalizes feedback validation errors', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse({ message: 'rating required' }, { status: 422 }));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.quality.feedback('ws_1', { target_type: 'workspace_answer', rating: 'up' })).rejects.toMatchObject({
      code: 'validation_error'
    });
  });

  it('normalizes real workspace list envelope fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('workspaces-list.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.workspaces.list()).resolves.toEqual(expect.arrayContaining([
      expect.objectContaining({ workspace_id: expect.stringMatching(/^rn-rc1-/), name: expect.stringMatching(/^rn-rc1-/) })
    ]));
  });

  it('normalizes real query hits as evidence fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('query-with-evidence.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('rn-rc1-fixture', { question: 'What is this?' })).resolves.toEqual(
      expect.objectContaining({
        noEvidence: false,
        evidence: expect.arrayContaining([expect.objectContaining({ sourceId: expect.any(String), traceAvailable: true })])
      })
    );
  });

  it('normalizes real no-evidence query fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('query-no-evidence.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.query.workspace('rn-rc1-fixture', { question: 'What is missing?' })).resolves.toEqual(
      expect.objectContaining({ noEvidence: true, evidence: [] })
    );
  });

  it('normalizes real graph missing artifact envelope fixture', async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(realFixture('graph-missing-artifact.json')));
    const client = createDataServiceClient({ fetchImpl });

    await expect(client.graph.communities('rn-rc1-fixture')).rejects.toMatchObject({ code: 'missing_graph_artifact' });
  });
});
