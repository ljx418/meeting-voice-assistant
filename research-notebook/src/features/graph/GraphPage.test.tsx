import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../../app/App';

const apiRoot = ['', 'api'].join('/');
const workspaceRoot = [apiRoot, 'workspaces', 'ws_1'].join('/');
const graphNeighborsPath = [workspaceRoot, 'graph', 'neighbors'].join('/');
const graphCommunitiesPath = [workspaceRoot, 'graph', 'community'].join('/');
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

function setupGraphRoute() {
  window.history.pushState({}, '', '/workspaces/ws_1/graph');
}

function createGraphFetch(overrides: Partial<Record<string, () => Promise<Response>>> = {}) {
  return vi.fn((input: RequestInfo | URL) => {
    const url = String(input);
    const handler = overrides[url];
    if (handler) return handler();
    if (url.startsWith(`${graphNeighborsPath}?`)) {
      return jsonResponse({ workspace_id: 'ws_1', nodes: [], edges: [], neighbors: [] });
    }
    if (url.startsWith(graphCommunitiesPath)) {
      return jsonResponse({ workspace_id: 'ws_1', communities: [] });
    }
    return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
  });
}

beforeEach(() => {
  setupGraphRoute();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('Graph M4 smoke', () => {
  it('renders missing graph artifact state', async () => {
    vi.stubGlobal(
      'fetch',
      createGraphFetch({
        [`${graphCommunitiesPath}?include_members=true`]: () => jsonResponse({ message: 'graph artifact no_artifact' }, { status: 404 })
      })
    );

    render(<App />);

    expect(await screen.findByText('Missing graph artifact')).toBeInTheDocument();
  });

  it('renders read-only communities and node-scoped neighbors', async () => {
    vi.stubGlobal(
      'fetch',
      createGraphFetch({
        [`${graphNeighborsPath}?node_id=n_1`]: () =>
          jsonResponse({
            workspace_id: 'ws_1',
            nodes: [{ node_id: 'n_1', label: 'Queues', node_type: 'concept' }],
            neighbors: [{ node_id: 'n_2', label: 'Backpressure', relationship: 'mitigates' }],
            edges: [{ edge_id: 'e_1', source_node_id: 'n_1', target_node_id: 'n_2' }]
          }),
        [`${graphCommunitiesPath}?include_members=true`]: () =>
          jsonResponse({
            workspace_id: 'ws_1',
            communities: [
              {
                community_id: 'c_1',
                title: 'Architecture',
                node_count: 3,
                relationship_count: 2,
                members: [{ node_id: 'n_1', label: 'Queues', node_type: 'concept' }]
              }
            ]
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('Architecture')).toBeInTheDocument();
    await userEvent.click(await screen.findByRole('button', { name: /Queues/i }));
    expect(await screen.findByText('Backpressure')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /edit/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /delete/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /merge/i })).not.toBeInTheDocument();
  });

  it('selects graph node locally without mutation UI', async () => {
    vi.stubGlobal(
      'fetch',
      createGraphFetch({
        [`${graphCommunitiesPath}?include_members=true`]: () =>
          jsonResponse({
            workspace_id: 'ws_1',
            communities: [
              {
                community_id: 'c_1',
                title: 'Architecture',
                members: [{ node_id: 'n_2', label: 'Backpressure', node_type: 'concept' }]
              }
            ]
          })
      })
    );

    render(<App />);

    await userEvent.click(await screen.findByRole('button', { name: /Backpressure/i }));
    expect(screen.getByText('Selected node: n_2')).toBeInTheDocument();
  });

  it('submits graph context feedback', async () => {
    vi.stubGlobal(
      'fetch',
      createGraphFetch({
        [feedbackPath]: () => jsonResponse({ feedback_id: 'fb_graph', workspace_id: 'ws_1', accepted: true })
      })
    );

    render(<App />);

    await screen.findByText('Read-only Graph Context');
    await userEvent.click(screen.getByRole('button', { name: /helpful/i }));
    expect(await screen.findByText(/Feedback submitted: up/i)).toBeInTheDocument();
  });
});
