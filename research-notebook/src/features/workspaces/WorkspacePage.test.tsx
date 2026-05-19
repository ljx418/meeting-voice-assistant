import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../../app/App';

const apiRoot = ['', 'api'].join('/');
const workspaceRoot = [apiRoot, 'workspaces', 'ws_1'].join('/');
const sourcesRoot = [workspaceRoot, 'sources'].join('/');
const buildStartPath = [workspaceRoot, 'build', 'start'].join('/');
const operationPath = [workspaceRoot, 'build', 'operations', 'op_1'].join('/');
const queryPath = [workspaceRoot, 'query'].join('/');
const feedbackPath = [workspaceRoot, 'quality', 'feedback'].join('/');
const sourceDetailPath = [sourcesRoot, 'src_1'].join('/');
const sourceTracePath = [sourcesRoot, 'src_1', 'trace'].join('/');

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

function setupWorkspaceRoute() {
  window.history.pushState({}, '', '/workspaces/ws_1');
}

function createWorkspaceFetch(overrides: Partial<Record<string, () => Promise<Response>>> = {}) {
  return vi.fn((input: RequestInfo | URL) => {
    const url = String(input);
    const handler = overrides[url];
    if (handler) return handler();
    if (url === workspaceRoot) {
      return jsonResponse({ workspace_id: 'ws_1', name: 'Research Workspace' });
    }
    if (url === sourcesRoot) {
      return jsonResponse({ sources: [] });
    }
    return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
  });
}

beforeEach(() => {
  setupWorkspaceRoute();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Workspace M2 smoke', () => {
  it('renders source library empty state', async () => {
    vi.stubGlobal('fetch', createWorkspaceFetch());

    render(<App />);

    expect(await screen.findByText('No sources yet')).toBeInTheDocument();
  });

  it('shows source after mocked import', async () => {
    let sourceListCalls = 0;
    const fetchMock = createWorkspaceFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === workspaceRoot) return jsonResponse({ workspace_id: 'ws_1', name: 'Research Workspace' });
      if (url === sourcesRoot && init?.method === 'POST') {
        return jsonResponse({ source: { source_id: 'src_1', workspace_id: 'ws_1', title: 'Architecture notes' } });
      }
      if (url === sourcesRoot) {
        sourceListCalls += 1;
        return jsonResponse({
          sources:
            sourceListCalls > 1
              ? [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Architecture notes', trace_available: true }]
              : []
        });
      }
      return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/source title/i), 'Architecture notes');
    await userEvent.click(screen.getByRole('button', { name: /import source/i }));

    expect(await screen.findByText('Architecture notes')).toBeInTheDocument();
  });

  it('starts build and shows status', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [buildStartPath]: () => jsonResponse({ operation_id: 'op_1' }),
        [operationPath]: () => jsonResponse({ operation_id: 'op_1', status: 'completed', message: 'Workspace build completed' })
      })
    );

    render(<App />);

    await screen.findByText('No sources yet');
    fireEvent.click(screen.getByRole('button', { name: /rebuild workspace knowledge/i }));

    expect(await screen.findByText(/Build status: completed/i)).toBeInTheDocument();
    expect(screen.getByText('Workspace build completed')).toBeInTheDocument();
  });

  it('renders query answer with evidence citation and opens trace drawer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [queryPath]: () =>
          jsonResponse({
            answer: 'Use a queue to absorb spikes.',
            evidence: [{ source_id: 'src_1', source_title: 'Architecture notes', snippet: 'queue depth' }]
          }),
        [sourceTracePath]: () =>
          jsonResponse({
            source_id: 'src_1',
            title: 'Architecture notes',
            artifact_refs: ['artifact:queue'],
            provenance: [{ label: 'Imported', value: 'manual note' }]
          }),
        [feedbackPath]: () => jsonResponse({ feedback_id: 'fb_1', workspace_id: 'ws_1', accepted: true })
      })
    );

    render(<App />);

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/question/i), 'How should we handle traffic spikes?');
    await userEvent.click(screen.getByRole('button', { name: /ask workspace/i }));

    expect(await screen.findByText('Use a queue to absorb spikes.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /helpful/i }));
    expect(await screen.findByText(/Feedback submitted: up/i)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Architecture notes/i }));
    expect(await screen.findByText('manual note')).toBeInTheDocument();
  });

  it('renders query answer with no evidence state', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [queryPath]: () => jsonResponse({ answer: 'The backend returned no source evidence.' })
      })
    );

    render(<App />);

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/question/i), 'What is known?');
    await userEvent.click(screen.getByRole('button', { name: /ask workspace/i }));

    expect(await screen.findByText('The backend returned no source evidence.')).toBeInTheDocument();
    expect(screen.getByText('No evidence available')).toBeInTheDocument();
  });

  it('shows trace unavailable without clearing answer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [queryPath]: () =>
          jsonResponse({
            answer: 'Evidence source exists.',
            evidence: [{ source_id: 'src_1', source_title: 'Architecture notes' }]
          }),
        [sourceDetailPath]: () =>
          jsonResponse({
            source_id: 'src_1',
            workspace_id: 'ws_1',
            title: 'Architecture notes',
            artifact_refs: ['artifact:source:src_1']
          }),
        [sourceTracePath]: () => jsonResponse({ message: 'trace unavailable' }, { status: 404 })
      })
    );

    render(<App />);

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/question/i), 'Show evidence');
    await userEvent.click(screen.getByRole('button', { name: /ask workspace/i }));

    expect(await screen.findByText('Evidence source exists.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Architecture notes/i }));
    expect(await screen.findByText('Trace unavailable')).toBeInTheDocument();
    expect(screen.getByText('Evidence source exists.')).toBeInTheDocument();
  });

  it('shows feedback failure without clearing workspace answer', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [queryPath]: () => jsonResponse({ answer: 'Feedback target remains visible.' }),
        [feedbackPath]: () => jsonResponse({ message: 'feedback unavailable' }, { status: 422 })
      })
    );

    render(<App />);

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/question/i), 'Can I rate this?');
    await userEvent.click(screen.getByRole('button', { name: /ask workspace/i }));

    expect(await screen.findByText('Feedback target remains visible.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /needs work/i }));
    expect(await screen.findByText('Feedback submit failed')).toBeInTheDocument();
    expect(screen.getByText('Feedback target remains visible.')).toBeInTheDocument();
  });
});
