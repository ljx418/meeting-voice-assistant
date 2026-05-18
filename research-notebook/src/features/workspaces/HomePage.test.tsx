import { describe, expect, it, vi, afterEach, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../../app/App';

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

afterEach(() => {
  vi.unstubAllGlobals();
});

beforeEach(() => {
  window.history.pushState({}, '', '/');
});

describe('Workspace Home smoke', () => {
  it('renders Home empty state', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({ workspaces: [] })));

    render(<App />);

    expect(await screen.findByText('No workspaces yet')).toBeInTheDocument();
  });

  it('renders workspace list', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        jsonResponse({
          workspaces: [{ workspace_id: 'ws_1', name: 'Research', description: 'Notes' }]
        })
      )
    );

    render(<App />);

    expect(await screen.findByText('Research')).toBeInTheDocument();
    expect(screen.getByText(/ws_1/)).toBeInTheDocument();
  });

  it('creates workspace with mocked adapter path', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ workspaces: [] }))
      .mockResolvedValueOnce(jsonResponse({ workspace: { workspace_id: 'ws_2', name: 'Interviews' } }))
      .mockResolvedValueOnce(jsonResponse({ workspaces: [{ workspace_id: 'ws_2', name: 'Interviews' }] }))
      .mockResolvedValueOnce(jsonResponse({ workspace_id: 'ws_2', name: 'Interviews' }));
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('No workspaces yet');
    await userEvent.type(screen.getByPlaceholderText('Technical interview notes'), 'Interviews');
    await userEvent.click(screen.getByRole('button', { name: /create workspace/i }));

    await waitFor(() => {
      expect(screen.getByText('Interviews')).toBeInTheDocument();
    });
  });

  it('renders create workspace failure state', async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse({ workspaces: [] }))
      .mockResolvedValueOnce(jsonResponse({ message: 'name already exists' }, { status: 409 }));
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('No workspaces yet');
    await userEvent.type(screen.getByPlaceholderText('Technical interview notes'), 'Duplicate');
    await userEvent.click(screen.getByRole('button', { name: /create workspace/i }));

    expect(await screen.findByText('Create workspace failed')).toBeInTheDocument();
    expect(screen.getByText('name already exists')).toBeInTheDocument();
  });
});
