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
const capabilitiesPath = [workspaceRoot, 'capabilities'].join('/');
const sourcePreviewPath = [sourceDetailPath, 'preview'].join('/');
const sourceUnitsPath = [sourceDetailPath, 'units'].join('/');
const sourceUnitPath = (unitId: string) => [sourceUnitsPath, unitId].join('/');
const sourceEvidenceSpanPath = (unitId: string, evidenceId: string) => [sourceUnitPath(unitId), 'evidence', evidenceId].join('/');

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

  it('opens V1.1 source preview shell as unsupported when contract is missing', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Architecture notes', trace_available: true }]
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('Architecture notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('Source preview contract missing')).toBeInTheDocument();
    expect(screen.getByText(/not claimed ready/i)).toBeInTheDocument();
  });

  it('opens source-level preview drawer when capability manifest supports the source type', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            status: 'ok',
            data: {
              manifest: {
                workspace_id: 'ws_1',
                schema_version: 'v1.1-source-preview',
                capabilities: {
                  source_preview: true,
                  document_units: false,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: false,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'source', locators: [] }]
              }
            },
            warnings: [],
            next_actions: []
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [
              {
                source_id: 'src_1',
                workspace_id: 'ws_1',
                title: 'Architecture notes',
                source_type: 'text',
                trace_available: true,
                artifact_refs: [{ artifact_ref: 'source://src_1' }]
              }
            ]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            status: 'ok',
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Architecture notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Queues absorb burst traffic.',
                artifact_refs: [{ artifact_ref: 'source://src_1' }],
                preview_truncated: false,
                preview_size_bytes: 28,
                max_preview_size_bytes: 50000
              }
            },
            warnings: [],
            next_actions: []
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('Architecture notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('Queues absorb burst traffic.')).toBeInTheDocument();
    expect(screen.getByText('text/plain')).toBeInTheDocument();
    expect(screen.getByText('Artifact refs are metadata only')).toBeInTheDocument();
    expect(screen.getByText('Unit navigation unsupported')).toBeInTheDocument();
  });

  it('shows DocumentUnit metadata as non-clickable disabled shell when manifest allows units', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: true,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: false,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'unit', locators: ['page_no'] }]
              }
            }
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Unit notes', source_type: 'text' }]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Unit notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Source preview.',
                units: [
                  {
                    unit_id: 'unit_1',
                    source_id: 'src_1',
                    unit_type: 'page',
                    title: 'Page 1',
                    order_index: 0,
                    page_no: 1,
                    text_preview: 'Unit preview.'
                  }
                ]
              }
            }
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('Unit notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('Units metadata returned but navigation disabled')).toBeInTheDocument();
    expect(screen.getByText('Page 1')).toBeInTheDocument();
    expect(screen.getByText('unit_1')).toBeInTheDocument();
    expect(screen.getByText('page 1')).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Page 1/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Page 1/i })).not.toBeInTheDocument();
  });

  it('ignores preview units when manifest document_units is false', async () => {
    const fetchMock = createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: false,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: false,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'source', locators: [] }]
              }
            }
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Ignored unit notes', source_type: 'text' }]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Ignored unit notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Source preview.',
                units: [{ unit_id: 'unit_ignored', source_id: 'src_1', unit_type: 'section', title: 'Ignored unit' }]
              }
            }
          })
      });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    expect(await screen.findByText('Ignored unit notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('Document units ignored')).toBeInTheDocument();
    expect(screen.queryByText('Ignored unit')).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalledWith(sourceUnitsPath, expect.anything());
  });

  it('loads DocumentUnit outline and selected unit detail from backend routes', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: true,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: true,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'unit', locators: [] }]
              }
            }
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Unit-ready notes', source_type: 'text' }]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Unit-ready notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Source preview remains visible.'
              }
            }
          }),
        [`${sourceUnitsPath}?limit=20`]: () =>
          jsonResponse({
            data: {
              units: {
                source_id: 'src_1',
                items: [
                  {
                    unit_id: 'unit_62567063869df3b5',
                    source_id: 'src_1',
                    unit_type: 'section',
                    title: 'Overview',
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
        [sourceUnitPath('unit_62567063869df3b5')]: () =>
          jsonResponse({
            data: {
              unit: {
                unit_id: 'unit_62567063869df3b5',
                source_id: 'src_1',
                unit_type: 'section',
                title: 'Overview',
                text_preview: '<strong>Escaped unit preview</strong>',
                content_type: 'text/html',
                order_index: 0,
                artifact_ref: 'unit://src_1/unit_62567063869df3b5',
                preview_available: true
              }
            }
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('Unit-ready notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('Source preview remains visible.')).toBeInTheDocument();
    await userEvent.click(await screen.findByRole('button', { name: /Overview/i }));

    expect(await screen.findByText('<strong>Escaped unit preview</strong>')).toBeInTheDocument();
    expect(screen.getByText(/text\/html returned by backend; rendered as escaped text/i)).toBeInTheDocument();
    expect(screen.getByText('Source preview remains visible.')).toBeInTheDocument();
  });

  it('keeps loaded units visible when loading more fails', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: true,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: true,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'unit', locators: [] }]
              }
            }
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Paged units', source_type: 'text' }]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Source preview.'
              }
            }
          }),
        [`${sourceUnitsPath}?limit=20`]: () =>
          jsonResponse({
            data: {
              units: {
                source_id: 'src_1',
                items: [{ unit_id: 'unit_62567063869df3b5', source_id: 'src_1', unit_type: 'section', title: 'First unit' }],
                next_cursor: 'du_MQ',
                limit: 20,
                has_more: true
              }
            }
          }),
        [`${sourceUnitsPath}?limit=20&cursor=du_MQ`]: () => jsonResponse({ message: 'load more failed' }, { status: 503 })
      })
    );

    render(<App />);

    expect(await screen.findByText('Paged units')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));
    expect(await screen.findByText('First unit')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /load more units/i }));

    expect(await screen.findByText('Load more units failed')).toBeInTheDocument();
    expect(screen.getByText('First unit')).toBeInTheDocument();
  });

  it('does not call preview route when manifest marks source type unsupported', async () => {
    const fetchMock = createWorkspaceFetch({
      [capabilitiesPath]: () =>
        jsonResponse({
          data: {
            manifest: {
              capabilities: {
                source_preview: true,
                document_units: false,
                evidence_spans: false,
                source_level_preview: true,
                unit_level_navigation: false,
                precise_span_highlight: false,
                citation_backjump: false
              },
              supported_source_types: [{ source_type: 'video', preview: 'none', locators: [] }]
            }
          }
        }),
      [sourcesRoot]: () =>
        jsonResponse({
          sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'Architecture notes', source_type: 'video' }]
        }),
      [sourcePreviewPath]: () => jsonResponse({ message: 'must not be called' }, { status: 500 })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    expect(await screen.findByText('Architecture notes')).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /preview/i })).toBeDisabled();
    expect(fetchMock).not.toHaveBeenCalledWith(sourcePreviewPath, expect.anything());
  });

  it('renders backend html preview as escaped text', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: false,
                  evidence_spans: false,
                  source_level_preview: true,
                  unit_level_navigation: false,
                  precise_span_highlight: false,
                  citation_backjump: false
                },
                supported_source_types: [{ source_type: 'text', preview: 'source', locators: [] }]
              }
            }
          }),
        [sourcesRoot]: () =>
          jsonResponse({
            sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: 'HTML notes', source_type: 'text' }]
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'HTML notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/html',
                text_preview: '<strong>Do not render as HTML</strong>'
              }
            }
          })
      })
    );

    render(<App />);

    expect(await screen.findByText('HTML notes')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /preview/i }));

    expect(await screen.findByText('<strong>Do not render as HTML</strong>')).toBeInTheDocument();
    expect(screen.getByText(/rendered as escaped text/i)).toBeInTheDocument();
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

  it('opens EvidenceSpan navigation from a jumpable workspace citation', async () => {
    const unitId = 'unit_62567063869df3b5';
    const evidenceId = 'ev_2e14b7785f3fbb06';
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [capabilitiesPath]: () =>
          jsonResponse({
            data: {
              manifest: {
                capabilities: {
                  source_preview: true,
                  document_units: true,
                  evidence_spans: true,
                  source_level_preview: true,
                  unit_level_navigation: true,
                  precise_span_highlight: true,
                  citation_backjump: true
                },
                supported_source_types: [{ source_type: 'text', preview: 'span', locators: ['offset'] }]
              }
            }
          }),
        [queryPath]: () =>
          jsonResponse({
            answer: 'Use queues for burst traffic.',
            evidence: [
              {
                source_id: 'src_1',
                source_title: 'Architecture notes',
                unit_id: unitId,
                evidence_id: evidenceId,
                snippet: 'Queues absorb burst traffic.'
              }
            ]
          }),
        [sourceDetailPath]: () =>
          jsonResponse({
            source_id: 'src_1',
            workspace_id: 'ws_1',
            title: 'Architecture notes',
            source_type: 'text'
          }),
        [sourcePreviewPath]: () =>
          jsonResponse({
            data: {
              preview: {
                source_id: 'src_1',
                title: 'Architecture notes',
                source_type: 'text',
                preview_available: true,
                content_type: 'text/plain',
                text_preview: 'Source-level preview remains visible.'
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
                    unit_id: unitId,
                    source_id: 'src_1',
                    unit_type: 'section',
                    title: 'Queue backpressure',
                    text_preview: 'Queues absorb burst traffic.',
                    content_type: 'text/plain',
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
        [sourceUnitPath(unitId)]: () =>
          jsonResponse({
            data: {
              unit: {
                unit_id: unitId,
                source_id: 'src_1',
                unit_type: 'section',
                title: 'Queue backpressure',
                text_preview: 'Queues absorb burst traffic.',
                content_type: 'text/plain',
                order_index: 0,
                preview_available: true
              }
            }
          }),
        [sourceEvidenceSpanPath(unitId, evidenceId)]: () =>
          jsonResponse({
            data: {
              evidence_span: {
                evidence_id: evidenceId,
                source_id: 'src_1',
                unit_id: unitId,
                snippet: 'absorb',
                start_offset: 7,
                end_offset: 13,
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

    await screen.findByText('No sources yet');
    await userEvent.type(screen.getByLabelText(/question/i), 'How should we handle burst traffic?');
    await userEvent.click(screen.getByRole('button', { name: /ask workspace/i }));

    expect(await screen.findByText('Use queues for burst traffic.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Architecture notes/i }));

    expect(await screen.findByText('Source-level preview remains visible.')).toBeInTheDocument();
    expect(await screen.findByText('Queue backpressure')).toBeInTheDocument();
    expect(await screen.findByText('absorb')).toBeInTheDocument();
    expect(screen.getByText(`evidence_id: ${evidenceId}`)).toBeInTheDocument();
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
