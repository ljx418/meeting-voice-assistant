import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../../app/App';

const apiRoot = ['', 'api'].join('/');
const workspaceRoot = [apiRoot, 'workspaces', 'ws_1'].join('/');
const sessionsRoot = [workspaceRoot, 'sessions'].join('/');
const sessionRoot = [sessionsRoot, 'ses_1'].join('/');
const ingestPath = [sessionRoot, 'ingest'].join('/');
const closePath = [sessionRoot, 'close'].join('/');
const sessionBuildStartPath = [sessionRoot, 'build', 'start'].join('/');
const sessionOperationPath = [sessionRoot, 'build', 'operations', 'op_session'].join('/');
const sessionQueryPath = [sessionRoot, 'query'].join('/');
const capabilitiesPath = [workspaceRoot, 'capabilities'].join('/');
const sourceDetailPath = [workspaceRoot, 'sources', 'src_1'].join('/');
const sourceTracePath = [workspaceRoot, 'sources', 'src_1', 'trace'].join('/');
const sourcePreviewPath = [workspaceRoot, 'sources', 'src_1', 'preview'].join('/');
const sourceUnitsPath = [workspaceRoot, 'sources', 'src_1', 'units?limit=20'].join('/');
const sourceUnitPath = [workspaceRoot, 'sources', 'src_1', 'units', 'unit_1'].join('/');
const sourceEvidenceSpanPath = [sourceUnitPath, 'evidence', 'ev_1'].join('/');
const sessionGraphPath = [workspaceRoot, 'graph', `session?session_id=ses_1`].join('/');
const feedbackPath = [workspaceRoot, 'quality', 'feedback'].join('/');

function jsonResponse(payload: unknown, init?: ResponseInit) {
  return Promise.resolve(
    new Response(JSON.stringify(payload), {
      status: init?.status ?? 200,
      headers: {
        'Content-Type': 'application/json'
      }
    })
  );
}

function setupWorkbenchRoute() {
  window.history.pushState({}, '', '/workspaces/ws_1/workbench');
}

function sessionPayload(state = 'active') {
  return { session_id: 'ses_1', workspace_id: 'ws_1', title: 'Interview prep', state };
}

function createWorkbenchFetch(overrides: Partial<Record<string, (init?: RequestInit) => Promise<Response>>> = {}) {
  return vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input);
    const handler = overrides[url];
    if (handler) return handler(init);
    if (url === sessionsRoot) {
      return jsonResponse({ sessions: [] });
    }
    if (url === sessionRoot) {
      return jsonResponse({ session: sessionPayload() });
    }
    if (url === sessionGraphPath) {
      return jsonResponse({ workspace_id: 'ws_1', session_id: 'ses_1', related_nodes: [], related_communities: [] });
    }
    return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
  });
}

beforeEach(() => {
  setupWorkbenchRoute();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Session Workbench M3 smoke', () => {
  it('renders session empty state', async () => {
    vi.stubGlobal('fetch', createWorkbenchFetch());

    render(<App />);

    expect(await screen.findByText('No sessions yet')).toBeInTheDocument();
    expect(screen.getByText('No active session')).toBeInTheDocument();
  });

  it('creates a session and selects it', async () => {
    let listCalls = 0;
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: (init?: RequestInit) => {
          if (init?.method === 'POST') return jsonResponse({ session: sessionPayload() });
          listCalls += 1;
          return jsonResponse({ sessions: listCalls > 1 ? [sessionPayload()] : [] });
        }
      })
    );

    render(<App />);

    await screen.findByText('No sessions yet');
    await userEvent.type(screen.getByLabelText(/session title/i), 'Interview prep');
    await userEvent.click(screen.getByRole('button', { name: /create session/i }));

    expect(await screen.findByRole('button', { name: /Interview prep/i })).toBeInTheDocument();
    expect(await screen.findByText('Current session')).toBeInTheDocument();
  });

  it('ingests snippet and starts session build', async () => {
    let detailState = 'active';
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload()] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload(detailState) }),
        [ingestPath]: () => {
          detailState = 'ingested_not_built';
          return jsonResponse({ session: sessionPayload('ingested_not_built') });
        },
        [sessionBuildStartPath]: () => jsonResponse({ operation_id: 'op_session' }),
        [sessionOperationPath]: () => jsonResponse({ operation_id: 'op_session', status: 'completed', message: 'Session build complete' })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/snippet or context/i), 'Hash table review notes');
    await userEvent.click(screen.getByRole('button', { name: /ingest snippet/i }));
    expect(await screen.findByText(/Needs build/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /build session/i }));
    expect(await screen.findByText(/Session build status: completed/i)).toBeInTheDocument();
    expect(screen.getByText('Session build complete')).toBeInTheDocument();
  });

  it('renders session query evidence and opens shared trace drawer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [sessionQueryPath]: () =>
          jsonResponse({
            answer: 'Review heap invariants.',
            evidence: [{ source_id: 'src_1', source_title: 'Heap notes', snippet: 'parent child relation' }]
          }),
        [sourceTracePath]: () =>
          jsonResponse({
            source_id: 'src_1',
            title: 'Heap notes',
            provenance: [{ label: 'Imported', value: 'manual source' }]
          }),
        [feedbackPath]: () => jsonResponse({ feedback_id: 'fb_session', workspace_id: 'ws_1', accepted: true })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/session question/i), 'What should I review?');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));

    expect(await screen.findByText('Review heap invariants.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /helpful/i }));
    expect(await screen.findByText(/Feedback submitted: up/i)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Heap notes/i }));
    expect(await screen.findByText('manual source')).toBeInTheDocument();
  });

  it('opens EvidenceSpan navigation from a jumpable session citation', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                workspace_id: 'ws_1',
                service_version: 'test',
                schema_version: 'v1.1-evidence-spans',
                generated_at: '2026-05-23T00:00:00Z',
                capabilities: {
                  source_preview: true,
                  document_units: true,
                  evidence_spans: true,
                  source_level_preview: true,
                  unit_level_navigation: true,
                  precise_span_highlight: true,
                  citation_backjump: true
                },
                supported_source_types: [{ source_type: 'text', preview: 'unit', locators: [] }]
              }
            }
          }),
        [sessionQueryPath]: () =>
          jsonResponse({
            answer: 'Session precise navigation preserves evidence ids.',
            evidence: [
              {
                source_id: 'src_1',
                source_title: 'Session Evidence Source',
                unit_id: 'unit_1',
                evidence_id: 'ev_1',
                snippet: 'preserves evidence ids'
              }
            ]
          }),
        [sourceDetailPath]: () =>
          jsonResponse({
            source_id: 'src_1',
            workspace_id: 'ws_1',
            title: 'Session Evidence Source',
            source_type: 'text'
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Session Evidence Source',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Session precise navigation preserves evidence ids for the selected unit.',
                artifact_refs: ['artifact://source/src_1']
              }
            }
          }),
        [sourceUnitsPath]: () =>
          jsonResponse({
            data: {
              units: {
                source_id: 'src_1',
                items: [
                  {
                    unit_id: 'unit_1',
                    source_id: 'src_1',
                    unit_type: 'text',
                    title: 'Session unit',
                    order_index: 0,
                    preview_available: true
                  }
                ],
                next_cursor: null,
                limit: 20,
                has_more: false
              }
            }
          }),
        [sourceUnitPath]: () =>
          jsonResponse({
            data: {
              unit: {
                unit_id: 'unit_1',
                source_id: 'src_1',
                unit_type: 'text',
                title: 'Session unit',
                content_type: 'text/plain',
                text_preview: 'Session precise navigation preserves evidence ids for the selected unit.',
                preview_available: true
              }
            }
          }),
        [sourceEvidenceSpanPath]: () =>
          jsonResponse({
            data: {
              evidence_span: {
                evidence_id: 'ev_1',
                source_id: 'src_1',
                unit_id: 'unit_1',
                snippet: 'preserves evidence ids',
                start_offset: 27,
                end_offset: 49,
                offset_basis: 'normalized_text',
                offset_range: 'half_open',
                text_basis: 'document_unit_text',
                preview_available: true
              }
            }
          })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/session question/i), 'What identifiers should session precise navigation preserve?');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));

    expect(await screen.findByText('Session precise navigation preserves evidence ids.')).toBeInTheDocument();
    await userEvent.click(await screen.findByTestId('jumpable-evidence-citation'));

    expect(await screen.findByTestId('source-preview-drawer')).toBeInTheDocument();
    expect((await screen.findAllByText('Session unit')).length).toBeGreaterThan(0);
    expect(await screen.findByText('evidence_id: ev_1')).toBeInTheDocument();
    expect(await screen.findByTestId('evidence-highlight')).toHaveTextContent('preserves evidence ids');
    expect(screen.getByText('Session precise navigation preserves evidence ids.')).toBeInTheDocument();
  });

  it('renders session graph context without blocking session answer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [sessionGraphPath]: () =>
          jsonResponse({
            workspace_id: 'ws_1',
            session_id: 'ses_1',
            related_nodes: [{ node_id: 'n_1', label: 'Heap invariant' }],
            related_communities: [{ community_id: 'c_1', title: 'Algorithms' }]
          }),
        [sessionQueryPath]: () => jsonResponse({ answer: 'Session answer still works.' })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    expect(await screen.findByText('Heap invariant')).toBeInTheDocument();
    await userEvent.type(screen.getByLabelText(/session question/i), 'Still ask?');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));
    expect(await screen.findByText('Session answer still works.')).toBeInTheDocument();
  });

  it('renders no-evidence state for session query', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [sessionQueryPath]: () => jsonResponse({ answer: 'No session evidence returned.' })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/session question/i), 'Anything?');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));

    expect(await screen.findByText('No session evidence returned.')).toBeInTheDocument();
    expect(screen.getByText('No evidence available')).toBeInTheDocument();
  });

  it('shows trace failure without clearing session answer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [sessionQueryPath]: () =>
          jsonResponse({
            answer: 'Evidence exists.',
            evidence: [{ source_id: 'src_1', source_title: 'Heap notes' }]
          }),
        [sourceDetailPath]: () =>
          jsonResponse({
            source_id: 'src_1',
            workspace_id: 'ws_1',
            title: 'Heap notes',
            artifact_refs: ['artifact:source:src_1']
          }),
        [sourceTracePath]: () => jsonResponse({ message: 'trace unavailable' }, { status: 404 })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/session question/i), 'Show evidence');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));

    expect(await screen.findByText('Evidence exists.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Heap notes/i }));
    expect(await screen.findByText('Trace unavailable')).toBeInTheDocument();
    expect(screen.getByText('Evidence exists.')).toBeInTheDocument();
  });

  it('shows feedback failure without clearing session answer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('ready')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('ready') }),
        [sessionQueryPath]: () => jsonResponse({ answer: 'Session feedback target remains visible.' }),
        [feedbackPath]: () => jsonResponse({ message: 'feedback unavailable' }, { status: 422 })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));
    await userEvent.type(screen.getByLabelText(/session question/i), 'Can I rate this?');
    await userEvent.click(screen.getByRole('button', { name: /ask session/i }));

    expect(await screen.findByText('Session feedback target remains visible.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /needs work/i }));
    expect(await screen.findByText('Feedback submit failed')).toBeInTheDocument();
    expect(screen.getByText('Session feedback target remains visible.')).toBeInTheDocument();
  });

  it('disables ingest build and query for closed session', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkbenchFetch({
        [sessionsRoot]: () => jsonResponse({ sessions: [sessionPayload('closed')] }),
        [sessionRoot]: () => jsonResponse({ session: sessionPayload('closed') }),
        [closePath]: () => jsonResponse({ session_id: 'ses_1', closed: true })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Interview prep/i }));

    expect(screen.getAllByRole('button', { name: /Session closed/i }).every((button) => button.hasAttribute('disabled'))).toBe(true);
    expect(screen.getByRole('button', { name: /^Closed$/i })).toBeDisabled();
    expect(screen.getByLabelText(/snippet or context/i)).toBeDisabled();
    expect(screen.getByLabelText(/session question/i)).toBeDisabled();
  });
});
