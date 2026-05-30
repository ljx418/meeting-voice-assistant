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
const guidePath = [workspaceRoot, 'guide'].join('/');
const studioArtifactsPath = [workspaceRoot, 'studio', 'artifacts'].join('/');
const researchPath = [workspaceRoot, 'research'].join('/');
const feedbackPath = [workspaceRoot, 'quality', 'feedback'].join('/');
const sourceDetailPath = [sourcesRoot, 'src_1'].join('/');
const sourceTracePath = [sourcesRoot, 'src_1', 'trace'].join('/');
const capabilitiesPath = [workspaceRoot, 'capabilities'].join('/');
const sourcePreviewPath = [sourceDetailPath, 'preview'].join('/');
const sourceUnitsPath = [sourceDetailPath, 'units'].join('/');
const sourceUnitPath = (unitId: string) => [sourceUnitsPath, unitId].join('/');
const sourceEvidenceSpanPath = (unitId: string, evidenceId: string) => [sourceUnitPath(unitId), 'evidence', evidenceId].join('/');
const folderSummaryRunsPath = [workspaceRoot, 'workflows', 'folder-summary', 'runs'].join('/');
const agentWorkflowDraftPath = [workspaceRoot, 'agent-workflows', 'draft'].join('/');

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

    expect(await screen.findByText('暂无来源')).toBeInTheDocument();
  });

  it('shows the folder summary workflow panel without starting local folder access automatically', async () => {
    const fetchMock = createWorkspaceFetch();
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    expect(await screen.findByRole('heading', { name: '文件夹总结工作流' })).toBeInTheDocument();
    expect(screen.getByText('把一个资料文件夹整理成可追溯的研究总结')).toBeInTheDocument();
    expect(screen.getByLabelText('Phase 2/3 输出工具')).toBeInTheDocument();
    expect(screen.getByText('Audio Overview')).toBeInTheDocument();
    expect(screen.getByText('PPT 生成')).toBeInTheDocument();
    expect(screen.getByText('思维导图')).toBeInTheDocument();
    expect(screen.getByText('文档对比')).toBeInTheDocument();
    expect(screen.getAllByRole('button', { name: '暂不可用' })).toHaveLength(4);
    expect(screen.getByText(/生成草案不会读取本地目录/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /生成工作流草案/ })).toBeEnabled();
    expect(screen.getByRole('button', { name: /扫描目录/ })).toBeEnabled();
    expect(screen.getByRole('button', { name: /确认并生成总结/ })).toBeEnabled();
    expect(fetchMock).toHaveBeenCalledWith(workspaceRoot, expect.objectContaining({ method: 'GET' }));
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining('agent'), expect.anything());
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining('folder-summary'), expect.anything());
  });

  it('creates a folder summary workflow draft without running the workflow automatically', async () => {
    const fetchMock = createWorkspaceFetch({
      [agentWorkflowDraftPath]: () =>
        jsonResponse({
          status: 'ok',
          data: {
            task: {
              task_id: 'task_1',
              workspace_id: 'ws_1',
              user_goal: '递归总结 Desktop/技术分享，每个子文件夹生成一份总结。',
              status: 'awaiting_approval',
              workflow_id: 'wf_1'
            },
            workflow: {
              workflow_id: 'wf_1',
              name: '递归文件夹总结',
              template_id: 'folder_summary_v1',
              status: 'draft',
              required_permissions: ['folder:scan', 'folder:extract:md_txt'],
              draft_parameters: {
                authorized_root_hint: 'Desktop/技术分享',
                include_extensions: ['.md', '.txt'],
                exclude_globs: ['**/*.tmp'],
                follow_symlinks: false,
                requires_user_confirmation: true
              },
              steps: [{ step_id: 'step_1', name: 'scan_folder', status: 'pending', retry_count: 0, artifact_refs: [] }]
            }
          }
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('文件夹总结工作流');
    await userEvent.click(screen.getByRole('button', { name: /生成工作流草案/ }));

    expect(await screen.findByLabelText('工作流草案')).toBeInTheDocument();
    expect(screen.getByText('等待用户确认')).toBeInTheDocument();
    expect(screen.getByText(/需要权限/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(agentWorkflowDraftPath, expect.objectContaining({ method: 'POST' }));
    expect(fetchMock).not.toHaveBeenCalledWith(folderSummaryRunsPath, expect.anything());
  });

  it('previews the workflow scan and renders step timeline', async () => {
    const fetchMock = createWorkspaceFetch({
      [folderSummaryRunsPath]: () =>
        jsonResponse({
          status: 'ok',
          data: {
            workflow: {
              workflow_id: 'wf_1',
              name: 'Folder Summary V1',
              template_id: 'folder_summary_v1',
              status: 'ready',
              required_permissions: ['folder:scan'],
              steps: [
                { step_id: 'step_1', name: 'scan_folder', status: 'completed', retry_count: 0, artifact_refs: [] },
                { step_id: 'step_2', name: 'summarize_folder', status: 'skipped', retry_count: 0, artifact_refs: [] }
              ]
            },
            run: {
              run_id: 'run_1',
              workflow_id: 'wf_1',
              status: 'completed',
              created_at: '2026-05-25T00:00:00Z',
              dry_run: true,
              run_report: {
                scanned_file_count: 2,
                manifest_file_count: 1,
                extracted_file_count: 0,
                skipped_file_count: 1,
                generated_artifact_count: 0
              },
              artifacts: []
            },
            collection: {
              collection_id: 'fc_1',
              workspace_id: 'ws_1',
              root_label: '技术分享',
              folders: [{ folder_id: 'fld_root', relative_path: '.', depth: 0, file_count: 1, child_folder_count: 0 }],
              files: [{ file_id: 'file_1', relative_path: 'notes.md', extension: '.md', size_bytes: 1, extraction_status: 'skipped' }],
              skipped_files: [{ relative_path: 'slides.pptx', skipped_reason: 'unsupported_extension' }]
            },
            permission_grant: {
              permission_grant_id: 'grant_1',
              workspace_id: 'ws_1',
              root_label: '技术分享',
              scopes: ['scan'],
              status: 'active'
            }
          }
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('文件夹总结工作流');
    await userEvent.click(screen.getByRole('button', { name: /扫描目录/ }));

    expect(await screen.findByText(/文件\s*1.*跳过\s*1.*产物\s*0/)).toBeInTheDocument();
    expect(screen.getByLabelText('扫描授权目录 已完成')).toBeInTheDocument();
    expect(screen.getByText('预览扫描只展示文件清单，不生成总结产物。')).toBeInTheDocument();
  });

  it('opens SummaryArtifact source_unit_span evidence in the source preview drawer', async () => {
    const fetchMock = createWorkspaceFetch({
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
              supported_source_types: [{ source_type: 'text', preview: 'span', locators: [] }]
            }
          }
        }),
      [folderSummaryRunsPath]: () =>
        jsonResponse({
          data: {
            workflow: {
              workflow_id: 'wf_1',
              name: 'Folder Summary V1',
              template_id: 'folder_summary_v1',
              status: 'ready',
              required_permissions: ['folder:scan'],
              steps: [{ step_id: 'step_1', name: 'summarize_folder', status: 'completed', retry_count: 0, artifact_refs: [] }]
            },
            run: {
              run_id: 'run_1',
              workflow_id: 'wf_1',
              status: 'completed',
              created_at: '2026-05-25T00:00:00Z',
              dry_run: false,
              run_report: {
                scanned_file_count: 1,
                manifest_file_count: 1,
                extracted_file_count: 1,
                skipped_file_count: 0,
                generated_artifact_count: 1
              },
              artifacts: [
                {
                  artifact_id: 'sum_1',
                  title: '根目录总览',
                  artifact_type: 'root_summary',
                  collection_id: 'fc_1',
                  status: 'ready',
                  schema_version: 'v1.3-summary-artifact',
                  coverage: { file_count: 1, extracted_file_count: 1, skipped_file_count: 0, evidence_ref_count: 1 },
                  markdown: '# 根目录总览',
                  evidence_refs: [
                    {
                      source_id: 'src_1',
                      source_title: 'Architecture notes',
                      unit_id: 'unit_62567063869df3b5',
                      evidence_id: 'ev_2e14b7785f3fbb06',
                      snippet: 'Queues absorb burst traffic.',
                      evidence_status: 'source_unit_span'
                    }
                  ]
                }
              ]
            },
            collection: {
              collection_id: 'fc_1',
              workspace_id: 'ws_1',
              root_label: '技术分享',
              folders: [{ folder_id: 'fld_root', relative_path: '.', depth: 0, file_count: 1, child_folder_count: 0 }],
              files: [{ file_id: 'file_1', relative_path: 'notes.md', extension: '.md', size_bytes: 1, extraction_status: 'extracted' }],
              skipped_files: []
            },
            permission_grant: {
              permission_grant_id: 'grant_1',
              workspace_id: 'ws_1',
              root_label: '技术分享',
              scopes: ['scan'],
              status: 'active'
            }
          }
        }),
      [sourceDetailPath]: () =>
        jsonResponse({ data: { source: { source_id: 'src_1', workspace_id: 'ws_1', title: 'Architecture notes', source_type: 'text' } } }),
      [sourcePreviewPath]: () =>
        jsonResponse({
          data: {
            preview: {
              source_id: 'src_1',
              title: 'Architecture notes',
              source_type: 'text',
              preview_available: true,
              content_type: 'text/plain',
              text_preview: 'Queues absorb burst traffic.'
            }
          }
        }),
      [`${sourceUnitsPath}?limit=20`]: () =>
        jsonResponse({
          data: {
            units: {
              source_id: 'src_1',
              items: [{ unit_id: 'unit_62567063869df3b5', source_id: 'src_1', unit_type: 'section', title: 'Overview' }],
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
              content_type: 'text/plain',
              text_preview: 'Queues absorb burst traffic.'
            }
          }
        }),
      [sourceEvidenceSpanPath('unit_62567063869df3b5', 'ev_2e14b7785f3fbb06')]: () =>
        jsonResponse({
          data: {
            evidence_span: {
              evidence_id: 'ev_2e14b7785f3fbb06',
              source_id: 'src_1',
              unit_id: 'unit_62567063869df3b5',
              start_offset: 0,
              end_offset: 6,
              offset_basis: 'normalized_text',
              offset_range: 'half_open',
              text_basis: 'document_unit_text',
              snippet: 'Queues'
            }
          }
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('文件夹总结工作流');
    await userEvent.click(screen.getByRole('button', { name: /确认并生成总结/ }));
    await userEvent.click(await screen.findByText('根目录总览'));
    await userEvent.click(await screen.findByTestId('summary-artifact-evidence-citation'));

    expect(await screen.findByTestId('source-preview-drawer')).toBeInTheDocument();
    expect(await screen.findByTestId('evidence-highlight')).toHaveTextContent('Queues');
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/来源标题/), 'Architecture notes');
    await userEvent.type(screen.getByLabelText(/文本或结构化内容/), 'Architecture notes content.');
    await userEvent.click(screen.getByRole('button', { name: /导入来源/ }));

    expect(await screen.findByText('Architecture notes')).toBeInTheDocument();
  });

  it('prevents empty source imports before calling the backend', async () => {
    const fetchMock = createWorkspaceFetch();
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/来源标题/), 'Only title');

    expect(screen.getByRole('button', { name: /导入来源/ })).toBeDisabled();
    expect(fetchMock).not.toHaveBeenCalledWith(sourcesRoot, expect.objectContaining({ method: 'POST' }));
  });

  it('submits public URL through URL source contract', async () => {
    let sourceListCalls = 0;
    let importBody: unknown;
    const fetchMock = createWorkspaceFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === workspaceRoot) return jsonResponse({ workspace_id: 'ws_1', name: 'Research Workspace' });
      if (url === sourcesRoot && init?.method === 'POST') {
        importBody = init.body ? JSON.parse(String(init.body)) : undefined;
        return jsonResponse({ data: { sources: [{ source_id: 'src_url', workspace_id: 'ws_1', title: '公开网页', source_type: 'url' }] } });
      }
      if (url === sourcesRoot) {
        sourceListCalls += 1;
        return jsonResponse({
          sources:
            sourceListCalls > 1
              ? [{ source_id: 'src_url', workspace_id: 'ws_1', title: '公开网页', source_type: 'url', trace_available: true }]
              : []
        });
      }
      return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/公开网页 URL/), 'https://example.com/article');
    await userEvent.type(screen.getByLabelText(/来源标题/), '公开网页');
    await userEvent.click(screen.getByRole('button', { name: /导入来源/ }));

    expect(await screen.findByText('公开网页')).toBeInTheDocument();
    expect(importBody).toMatchObject({
      urls: [
        {
          title: '公开网页',
          url: 'https://example.com/article',
          metadata: { url_import_contract: 'public_url_text_v1', url_source_input: true }
        }
      ],
      metadata: { url_import_contract: 'public_url_text_v1', url_source_input: true }
    });
  });

  it('rejects private URL imports on the client', async () => {
    const fetchMock = createWorkspaceFetch();
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/公开网页 URL/), 'http://127.0.0.1/private');
    await userEvent.click(screen.getByRole('button', { name: /导入来源/ }));

    expect(await screen.findByText(/不能是本机、内网或私有地址/)).toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalledWith(sourcesRoot, expect.objectContaining({ method: 'POST' }));
  });

  it('submits selected PDF through browser file upload contract', async () => {
    let sourceListCalls = 0;
    let importBody: unknown;
    const fetchMock = createWorkspaceFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === workspaceRoot) return jsonResponse({ workspace_id: 'ws_1', name: 'Research Workspace' });
      if (url === sourcesRoot && init?.method === 'POST') {
        importBody = init.body ? JSON.parse(String(init.body)) : undefined;
        return jsonResponse({ data: { sources: [{ source_id: 'src_pdf', workspace_id: 'ws_1', title: '数字人报告' }] } });
      }
      if (url === sourcesRoot) {
        sourceListCalls += 1;
        return jsonResponse({
          sources:
            sourceListCalls > 1
              ? [{ source_id: 'src_pdf', workspace_id: 'ws_1', title: '数字人报告', source_type: 'pdf', trace_available: true }]
              : []
        });
      }
      return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    const pdf = new globalThis.File(['%PDF-1.7 browser fixture'], '数字人报告.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText('文件', { selector: 'input' }), pdf);
    await userEvent.click(screen.getByRole('button', { name: /导入来源/ }));

    expect(await screen.findByText('数字人报告')).toBeInTheDocument();
    expect(importBody).toMatchObject({
      files: [
        {
          title: '数字人报告.pdf',
          file_name: '数字人报告.pdf',
          content_type: 'application/pdf',
          source_type: 'pdf',
          metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
        }
      ],
      metadata: { browser_file_import: true, file_upload_contract: 'base64_file_content' }
    });
    expect((importBody as { files: Array<{ content_base64: string }> }).files[0].content_base64).toBeTruthy();
  });

  it('imports multiple selected P0 files sequentially', async () => {
    const importedBodies: unknown[] = [];
    let sourceListCalls = 0;
    const fetchMock = createWorkspaceFetch();
    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url === workspaceRoot) return jsonResponse({ workspace_id: 'ws_1', name: 'Research Workspace' });
      if (url === sourcesRoot && init?.method === 'POST') {
        importedBodies.push(init.body ? JSON.parse(String(init.body)) : undefined);
        return jsonResponse({ data: { sources: [{ source_id: `src_${importedBodies.length}`, workspace_id: 'ws_1', title: `Source ${importedBodies.length}` }] } });
      }
      if (url === sourcesRoot) {
        sourceListCalls += 1;
        return jsonResponse({
          sources:
            sourceListCalls > 1
              ? [
                  { source_id: 'src_md', workspace_id: 'ws_1', title: 'brief.md', source_type: 'markdown', trace_available: true },
                  { source_id: 'src_pdf', workspace_id: 'ws_1', title: 'report.pdf', source_type: 'pdf', trace_available: true }
                ]
              : []
        });
      }
      return jsonResponse({ message: `Unhandled ${url}` }, { status: 404 });
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    const markdown = new globalThis.File(['# 数字人资料'], 'brief.md', { type: 'text/markdown' });
    const pdf = new globalThis.File(['%PDF-1.7 browser fixture'], 'report.pdf', { type: 'application/pdf' });
    await userEvent.upload(screen.getByLabelText('文件', { selector: 'input' }), [markdown, pdf]);
    expect(await screen.findByText(/将按顺序导入 2 个文件/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /导入 2 个来源/ }));

    expect(await screen.findByText('brief.md')).toBeInTheDocument();
    expect(await screen.findByText('report.pdf')).toBeInTheDocument();
    expect(importedBodies).toHaveLength(2);
    expect(importedBodies[0]).toMatchObject({
      files: [{ title: 'brief.md', file_name: 'brief.md', source_type: 'markdown' }]
    });
    expect(importedBodies[1]).toMatchObject({
      files: [{ title: 'report.pdf', file_name: 'report.pdf', source_type: 'pdf' }]
    });
  });

  it('renders generated Notebook Guide and sends suggested question to chat', async () => {
    const fetchMock = createWorkspaceFetch({
      [sourcesRoot]: () =>
        jsonResponse({
          sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: '数字人报告', source_type: 'pdf', trace_available: true }]
        }),
      [guidePath]: () =>
        jsonResponse({
          data: {
            guide: {
              guide_available: true,
              source_count: 1,
              overview: '当前 Notebook 已导入 1 个来源。',
              key_topics: [{ title: '来源范围', summary: '包含可抽取文本 PDF。' }],
              suggested_questions: ['数字人报告的核心观点是什么？'],
              evidence_refs: []
            }
          }
        }),
      [queryPath]: () =>
        new Promise((resolve) => {
          globalThis.setTimeout(() => {
            resolve(
              new Response(
                JSON.stringify({
                  answer: '数字人报告认为企业应用需要可追溯证据。',
                  evidence: [{ source_id: 'src_1', source_title: '数字人报告', snippet: '企业应用需要可追溯证据。' }]
                }),
                { status: 200, headers: { 'Content-Type': 'application/json' } }
              )
            );
          }, 50);
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    expect(await screen.findByText('当前 Notebook 已导入 1 个来源。')).toBeInTheDocument();
    expect(screen.getByText('包含可抽取文本 PDF。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '数字人报告的核心观点是什么？' }));

    expect(await screen.findByText('正在基于来源生成回答')).toBeInTheDocument();
    expect(await screen.findByText('数字人报告认为企业应用需要可追溯证据。')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(guidePath, expect.objectContaining({ method: 'GET' }));
    expect(fetchMock).toHaveBeenCalledWith(
      queryPath,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ query: '数字人报告的核心观点是什么？' })
      })
    );
  });

  it('generates Studio lightweight output with citations', async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(globalThis.navigator, 'clipboard', {
      configurable: true,
      value: { writeText }
    });
    Object.defineProperty(URL, 'createObjectURL', {
      configurable: true,
      value: vi.fn().mockReturnValue('blob:studio-export')
    });
    Object.defineProperty(URL, 'revokeObjectURL', {
      configurable: true,
      value: vi.fn()
    });
    const createObjectUrl = vi.mocked(URL.createObjectURL);
    const revokeObjectUrl = vi.mocked(URL.revokeObjectURL);
    const fetchMock = createWorkspaceFetch({
      [sourcesRoot]: () =>
        jsonResponse({
          sources: [{ source_id: 'src_1', workspace_id: 'ws_1', title: '数字人报告', source_type: 'pdf', trace_available: true }]
        }),
      [capabilitiesPath]: () =>
        jsonResponse({
          data: {
            manifest: {
              capabilities: {
                source_preview: true,
                source_level_preview: true,
                document_units: true,
                unit_level_navigation: true,
                evidence_spans: true,
                precise_span_highlight: true,
                citation_backjump: true
              },
              supported_source_types: [{ source_type: 'pdf', preview: 'unit', locators: ['page_no'] }]
            }
          }
        }),
      [studioArtifactsPath]: () =>
        jsonResponse({
          data: {
            artifact: {
              artifact_id: 'studio_study_guide_1',
              artifact_type: 'study_guide',
              title: 'Study Guide',
              artifact_available: true,
              summary: 'Study Guide 已基于当前 Notebook sources 生成，并保留可跳转引用。',
              sections: [{ title: '学习目标', content: '理解数字人资料中的证据治理。' }],
              evidence_refs: [
                {
                  source_id: 'src_1',
                  source_title: '数字人报告',
                  unit_id: 'unit_1',
                  evidence_id: 'ev_1',
                  snippet: '数字人需要证据治理。'
                }
              ]
            }
          }
        }),
      [sourceDetailPath]: () =>
        jsonResponse({
          source_id: 'src_1',
          workspace_id: 'ws_1',
          title: '数字人报告',
          source_type: 'pdf'
        }),
      [sourcePreviewPath]: () =>
        jsonResponse({
          data: {
            preview: {
              source_id: 'src_1',
              title: '数字人报告',
              source_type: 'pdf',
              preview_available: true,
              content_type: 'text/plain',
              text_preview: '数字人报告来源级预览。'
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
                  unit_type: 'page',
                  title: 'Page 1',
                  order_index: 0,
                  page_no: 1,
                  preview_available: true
                }
              ],
              next_cursor: null,
              limit: 20,
              has_more: false
            }
          }
        }),
      [sourceUnitPath('unit_1')]: () =>
        jsonResponse({
          data: {
            unit: {
              unit_id: 'unit_1',
              source_id: 'src_1',
              unit_type: 'page',
              title: 'Page 1',
              text_preview: '数字人需要证据治理。',
              content_type: 'text/plain',
              order_index: 0,
              page_no: 1,
              preview_available: true
            }
          }
        }),
      [sourceEvidenceSpanPath('unit_1', 'ev_1')]: () =>
        jsonResponse({
          data: {
            evidence_span: {
              evidence_id: 'ev_1',
              source_id: 'src_1',
              unit_id: 'unit_1',
              snippet: '证据治理',
              start_offset: 5,
              end_offset: 9,
              offset_basis: 'normalized_text',
              offset_range: 'half_open',
              text_basis: 'document_unit_text',
              preview_available: true
            }
          }
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByRole('heading', { name: 'Studio' });
    await userEvent.click(screen.getAllByRole('button', { name: '生成' })[1]);

    expect(await screen.findByText('Study Guide 已基于当前 Notebook sources 生成，并保留可跳转引用。')).toBeInTheDocument();
    expect(screen.getByText('理解数字人资料中的证据治理。')).toBeInTheDocument();
    expect(screen.getByText('数字人需要证据治理。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '复制 Markdown' }));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('## 学习目标'));
    expect(writeText).toHaveBeenCalledWith(expect.stringContaining('ev_1'));
    expect(await screen.findByText('Markdown 已复制，包含 citation metadata。')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '下载 Markdown' }));
    await userEvent.click(screen.getByRole('button', { name: '下载 JSON' }));
    expect(createObjectUrl).toHaveBeenCalledTimes(2);
    expect(revokeObjectUrl).toHaveBeenCalledWith('blob:studio-export');
    await userEvent.click(screen.getByTestId('jumpable-evidence-citation'));
    expect(await screen.findByText('证据治理')).toBeInTheDocument();
    expect(screen.getByLabelText('已选文档单元')).toHaveTextContent('unit_1');
    expect(fetchMock).toHaveBeenCalledWith(
      studioArtifactsPath,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ artifact_type: 'study_guide' })
      })
    );
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('缺少来源预览合同')).toBeInTheDocument();
    expect(screen.getByText(/来源预览保持禁用状态/)).toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('Queues absorb burst traffic.')).toBeInTheDocument();
    expect(screen.getByText('text/plain')).toBeInTheDocument();
    expect(screen.getByText('工件引用仅作为元数据展示')).toBeInTheDocument();
    expect(screen.getByText('暂不支持单元导航')).toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('已返回单元元数据，但导航未启用')).toBeInTheDocument();
    expect(screen.getByText('Page 1')).toBeInTheDocument();
    expect(screen.getByText('unit_1')).toBeInTheDocument();
    expect(screen.getByText('页码 1')).toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('已忽略文档单元')).toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('Source preview remains visible.')).toBeInTheDocument();
    await userEvent.click(await screen.findByRole('button', { name: /Overview/i }));

    expect(await screen.findByText('<strong>Escaped unit preview</strong>')).toBeInTheDocument();
    expect(screen.getByText(/后端返回 text\/html，已按转义文本渲染/)).toBeInTheDocument();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));
    expect(await screen.findByText('First unit')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /加载更多单元/ }));

    expect(await screen.findByText('加载更多单元失败')).toBeInTheDocument();
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
    expect(await screen.findByRole('button', { name: /预览/ })).toBeDisabled();
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
    await userEvent.click(screen.getByRole('button', { name: /预览/ }));

    expect(await screen.findByText('<strong>Do not render as HTML</strong>')).toBeInTheDocument();
    expect(screen.getByText(/已按转义文本渲染/)).toBeInTheDocument();
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

    await screen.findByText('暂无来源');
    fireEvent.click(screen.getByRole('button', { name: /重建工作区知识|重建知识/ }));

    expect(await screen.findByText(/构建状态：已完成/)).toBeInTheDocument();
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'How should we handle traffic spikes?');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('Use a queue to absorb spikes.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /有帮助/ }));
    expect(await screen.findByText(/反馈已提交：有帮助/)).toBeInTheDocument();
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'How should we handle burst traffic?');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('Use queues for burst traffic.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Architecture notes/i }));

    expect(await screen.findByText('Source-level preview remains visible.')).toBeInTheDocument();
    expect(await screen.findByText('Queue backpressure')).toBeInTheDocument();
    expect(await screen.findByText('absorb')).toBeInTheDocument();
    expect(screen.getByText(`证据片段：${evidenceId}`)).toBeInTheDocument();
  });

  it('switches to the cited unit when another same-source citation is clicked', async () => {
    const firstUnitId = 'unit_62567063869df3b5';
    const secondUnitId = 'unit_72567063869df3b6';
    const firstEvidenceId = 'ev_2e14b7785f3fbb06';
    const secondEvidenceId = 'ev_3e14b7785f3fbb07';
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
            answer: 'Use queues and keep answers visible.',
            evidence: [
              {
                source_id: 'src_1',
                source_title: 'Architecture notes',
                unit_id: firstUnitId,
                evidence_id: firstEvidenceId,
                snippet: 'Queues absorb burst traffic.'
              },
              {
                source_id: 'src_1',
                source_title: 'Architecture notes',
                unit_id: secondUnitId,
                evidence_id: secondEvidenceId,
                snippet: 'Keep the answer visible.'
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
                    unit_id: firstUnitId,
                    source_id: 'src_1',
                    unit_type: 'section',
                    title: 'Queue backpressure',
                    order_index: 0,
                    preview_available: true
                  },
                  {
                    unit_id: secondUnitId,
                    source_id: 'src_1',
                    unit_type: 'section',
                    title: 'Answer locality',
                    order_index: 1,
                    preview_available: true
                  }
                ],
                next_cursor: null,
                limit: 20,
                has_more: false
              }
            }
          }),
        [sourceUnitPath(firstUnitId)]: () =>
          jsonResponse({
            data: {
              unit: {
                unit_id: firstUnitId,
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
        [sourceUnitPath(secondUnitId)]: () =>
          jsonResponse({
            data: {
              unit: {
                unit_id: secondUnitId,
                source_id: 'src_1',
                unit_type: 'section',
                title: 'Answer locality',
                text_preview: 'Keep the answer visible.',
                content_type: 'text/plain',
                order_index: 1,
                preview_available: true
              }
            }
          }),
        [sourceEvidenceSpanPath(firstUnitId, firstEvidenceId)]: () =>
          jsonResponse({
            data: {
              evidence_span: {
                evidence_id: firstEvidenceId,
                source_id: 'src_1',
                unit_id: firstUnitId,
                snippet: 'absorb',
                start_offset: 7,
                end_offset: 13,
                offset_basis: 'normalized_text',
                offset_range: 'half_open',
                text_basis: 'document_unit_text',
                preview_available: true
              }
            }
          }),
        [sourceEvidenceSpanPath(secondUnitId, secondEvidenceId)]: () =>
          jsonResponse({
            data: {
              evidence_span: {
                evidence_id: secondEvidenceId,
                source_id: 'src_1',
                unit_id: secondUnitId,
                snippet: 'answer',
                start_offset: 9,
                end_offset: 15,
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'What should remain visible?');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('Use queues and keep answers visible.')).toBeInTheDocument();
    const citations = await screen.findAllByTestId('jumpable-evidence-citation');
    await userEvent.click(citations[0]);
    expect(await screen.findByText(`证据片段：${firstEvidenceId}`)).toBeInTheDocument();
    expect(await screen.findByText('absorb')).toBeInTheDocument();

    await userEvent.click(citations[1]);
    expect(await screen.findByText(`证据片段：${secondEvidenceId}`)).toBeInTheDocument();
    expect(await screen.findByText('answer')).toBeInTheDocument();
    expect(screen.getByLabelText('已选文档单元')).toHaveTextContent(secondUnitId);
  });

  it('renders query answer with no evidence state', async () => {
    vi.stubGlobal(
      'fetch',
      createWorkspaceFetch({
        [queryPath]: () =>
          jsonResponse({
            answer: '当前资料未覆盖这个问题。',
            evidence: [],
            no_evidence: true,
            coverage_status: 'insufficient_evidence',
            answer_basis: 'source_grounded_refusal',
            unsupported_reason: 'insufficient_evidence',
            suggested_source_actions: ['添加相关 PDF、TXT 或 Markdown']
          })
      })
    );

    render(<App />);

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'What is known?');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('当前资料未覆盖这个问题。')).toBeInTheDocument();
    expect(screen.getByText('当前资料未覆盖')).toBeInTheDocument();
    expect(screen.getByText('添加相关 PDF、TXT 或 Markdown')).toBeInTheDocument();
    expect(screen.getByText('暂无可用证据')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: '添加来源' }));
    expect(screen.getByLabelText('来源标题')).toHaveFocus();
  });

  it('generates a source-grounded Research report from the current question', async () => {
    const fetchMock = createWorkspaceFetch({
      [capabilitiesPath]: () =>
        jsonResponse({
          data: {
            manifest: {
              capabilities: {
                source_preview: true,
                source_level_preview: true,
                document_units: true,
                unit_level_navigation: true,
                evidence_spans: true,
                precise_span_highlight: true,
                citation_backjump: true
              },
              supported_source_types: [{ source_type: 'markdown', preview: 'span', locators: [] }]
            }
          }
        }),
      [queryPath]: () =>
        jsonResponse({
          answer: '数字人应用需要标注 AI 生成身份。',
          evidence: [
            {
              source_id: 'src_1',
              source_title: '数字人资料',
              unit_id: 'unit_1',
              evidence_id: 'ev_1',
              snippet: '数字人应用需要标注 AI 生成身份。'
            }
          ],
          no_evidence: false
        }),
      [researchPath]: () =>
        jsonResponse({
          data: {
            research: {
              research_available: true,
              question: '数字人风险是什么？',
              coverage_status: 'source_supported',
              answer_basis: 'source_supported',
              answer: '已基于当前 Notebook sources 生成受限 Research 输出。',
              supported_conclusions: [
                {
                  claim: '数字人应用需要标注 AI 生成身份。',
                  evidence_refs: [
                    {
                      source_id: 'src_1',
                      source_title: '数字人资料',
                      unit_id: 'unit_1',
                      evidence_id: 'ev_1',
                      snippet: '数字人应用需要标注 AI 生成身份。'
                    }
                  ]
                }
              ],
              inferences: [
                {
                  inference: '基于来源的推断：需要人工审阅来源上下文。',
                  evidence_refs: [
                    {
                      source_id: 'src_1',
                      unit_id: 'unit_1',
                      evidence_id: 'ev_1'
                    }
                  ],
                  inference_notice: '该段为基于来源的推断。'
                }
              ],
              conflicts: [],
              missing_evidence: [],
              suggested_source_actions: [],
              evidence_refs: []
            }
          }
        })
    });
    vi.stubGlobal('fetch', fetchMock);

    render(<App />);

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), '数字人风险是什么？');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));
    expect((await screen.findAllByText('数字人应用需要标注 AI 生成身份。')).length).toBeGreaterThan(0);
    await userEvent.click(screen.getByRole('button', { name: '生成 Research 综合' }));

    expect(await screen.findByLabelText('Research 综合输出')).toBeInTheDocument();
    expect(screen.getByText('资料明确支持的结论')).toBeInTheDocument();
    expect(screen.getByText('来源支持')).toBeInTheDocument();
    expect(screen.getByText(/不代表全量冲突分析 ready/)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      researchPath,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ question: '数字人风险是什么？', top_k: 8 })
      })
    );
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'Show evidence');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('Evidence source exists.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /Architecture notes/i }));
    expect(await screen.findByText('溯源不可用')).toBeInTheDocument();
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

    await screen.findByText('暂无来源');
    await userEvent.type(screen.getByLabelText(/问题/), 'Can I rate this?');
    await userEvent.click(screen.getByRole('button', { name: /询问工作区/ }));

    expect(await screen.findByText('Feedback target remains visible.')).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: /需要改进/ }));
    expect(await screen.findByText('反馈提交失败')).toBeInTheDocument();
    expect(screen.getByText('Feedback target remains visible.')).toBeInTheDocument();
  });
});
